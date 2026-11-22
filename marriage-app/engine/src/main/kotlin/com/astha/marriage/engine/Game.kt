package com.astha.marriage.engine

import kotlin.random.Random

enum class SeenVia { NONE, MELDS, DUBLEES }

enum class Phase {
    /** The current player must draw from the stock or take the top discard. */
    DRAW,

    /** The current player has drawn and may show, win, or discard. */
    PLAY,

    ROUND_OVER,
}

class PlayerState(val index: Int) {
    val hand = mutableListOf<Card>()

    /** Tunnelas exposed right after the deal. Only these score tunnela points. */
    val startTunnelas = mutableListOf<Meld>()

    /** Pure combinations laid down to see the joker (besides [startTunnelas]). */
    val shownMelds = mutableListOf<Meld>()

    /** Dublees laid down to see the joker. */
    val shownDublees = mutableListOf<Dublee>()

    var seen: SeenVia = SeenVia.NONE
        internal set

    /** False until the player's first turn ends; tunnelas may be exposed until then. */
    var hasPlayed: Boolean = false
        internal set

    val hasSeen: Boolean get() = seen != SeenVia.NONE

    /** Every card the player owns, in hand or on the table. */
    val allCards: List<Card>
        get() = hand + startTunnelas.flatMap { it.cards } + shownMelds.flatMap { it.cards } + shownDublees.flatMap { it.cards }

    val laidMeldCount: Int get() = startTunnelas.size + shownMelds.size
}

sealed interface GameEvent {
    val player: Int

    data class ExposedTunnela(override val player: Int, val meld: Meld) : GameEvent
    data class DrewStock(override val player: Int) : GameEvent
    data class TookDiscard(override val player: Int, val card: Card) : GameEvent
    data class Discarded(override val player: Int, val card: Card) : GameEvent
    data class ShowedMelds(override val player: Int, val melds: List<Meld>, val choseTiplu: Boolean) : GameEvent
    data class ShowedDublees(override val player: Int, val dublees: List<Dublee>, val choseTiplu: Boolean) : GameEvent
    data class Won(override val player: Int, val byDublees: Boolean) : GameEvent
    data class StockReshuffled(override val player: Int) : GameEvent
    data class NoWinner(override val player: Int) : GameEvent
}

/** How a player can finish the hand right now. */
data class WinPlan(val discard: Card, val melds: List<Meld>, val dublees: List<Dublee>, val byDublees: Boolean)

data class RoundResult(
    /** Null when the cards ran out and nobody won. */
    val winner: Int?,
    val byDublees: Boolean,
    val tiplu: Card?,
    val seen: List<Boolean>,
    val points: List<Int>,
    val breakdown: List<List<PointItem>>,
    /** Each player's gain (negative: loss) for this hand. */
    val net: List<Int>,
    val winningMelds: List<Meld>,
    val winningDublees: List<Dublee>,
    val finalDiscard: Card?,
)

class GameRuleException(message: String) : IllegalStateException(message)

/**
 * One hand of Marriage. Players sit in index order; play goes clockwise, which
 * here means increasing index, starting with the player after the dealer.
 */
class MarriageGame(
    val playerCount: Int,
    val dealer: Int,
    private val random: Random = Random.Default,
) {
    init {
        require(playerCount in 2..5) { "2 to 5 players" }
        require(dealer in 0 until playerCount)
    }

    val players: List<PlayerState> = List(playerCount) { PlayerState(it) }

    /** Face-down stock; the last element is the top. The tiplu is kept apart, below it. */
    private val stock = ArrayDeque<Card>()

    /** Discard pile; the last element is the top. */
    private val discards = mutableListOf<Card>()

    private val _log = mutableListOf<GameEvent>()
    val log: List<GameEvent> get() = _log

    var tiplu: Card? = null
        private set

    var current: Int = (dealer + 1) % playerCount
        private set

    var phase: Phase = Phase.DRAW
        private set

    /** The card the current player took from the discard pile this turn. */
    var takenFromDiscard: Card? = null
        private set

    /** The card the current player drew this turn (from either pile). */
    var drawnCard: Card? = null
        private set

    /** Whether the current player had already seen when they drew this turn. */
    private var seenAtDraw: SeenVia = SeenVia.NONE

    var result: RoundResult? = null
        private set

    val stockSize: Int get() = stock.size
    val discardPile: List<Card> get() = discards
    val topDiscard: Card? get() = discards.lastOrNull()

    init {
        val shoe = Card.fullShoe().shuffled(random)
        stock.addAll(shoe)
        // Deal one at a time, starting left of the dealer.
        repeat(21) {
            for (k in 1..playerCount) {
                players[(dealer + k) % playerCount].hand.add(stock.removeLast())
            }
        }
        discards.add(stock.removeLast())
    }

    /** Joker knowledge of [player]. */
    fun contextFor(player: Int): JokerContext =
        if (players[player].hasSeen) JokerContext(tiplu?.face) else JokerContext.UNSEEN

    private fun fail(msg: String): Nothing = throw GameRuleException(msg)

    private fun requireTurn(player: Int, phase: Phase) {
        if (this.phase == Phase.ROUND_OVER) fail("The hand is over")
        if (player != current) fail("Not this player's turn")
        if (this.phase != phase) fail(if (phase == Phase.DRAW) "Draw first" else "Already drew")
    }

    // ----- Exposing tunnelas after the deal -----

    /** Tunnelas in hand that [player] may still expose. */
    fun exposableTunnelas(player: Int): List<Meld> {
        val p = players[player]
        if (p.hasPlayed || phase == Phase.ROUND_OVER || p.hasSeen) return emptyList()
        if (player == current && phase != Phase.DRAW) return emptyList()
        return p.hand.groupBy { it.face }.values.filter { it.size >= 3 }
            .map { Meld(it.take(3), MeldType.TUNNELA) }
    }

    /** Lays down every tunnela [player] holds, before their first draw. */
    fun exposeTunnelas(player: Int): List<Meld> {
        val melds = exposableTunnelas(player)
        val p = players[player]
        for (m in melds) {
            p.hand.removeAll(m.cards)
            p.startTunnelas.add(m)
            _log.add(GameEvent.ExposedTunnela(player, m))
        }
        return melds
    }

    // ----- Drawing -----

    fun canDrawDiscard(player: Int): Boolean {
        if (phase != Phase.DRAW || player != current) return false
        val top = topDiscard ?: return false
        val p = players[player]
        return when (p.seen) {
            SeenVia.NONE -> true
            SeenVia.MELDS -> !contextFor(player).isWild(top)
            SeenVia.DUBLEES -> p.shownDublees.size + Melds.dublees(p.hand + top).size >= 8 &&
                p.hand.any { it.face == top.face }
        }
    }

    /** Why [player] may not take the top discard, for messages; null if they may. */
    fun discardBlockReason(player: Int): DiscardBlock? {
        if (phase != Phase.DRAW || player != current || topDiscard == null) return DiscardBlock.NOT_NOW
        if (canDrawDiscard(player)) return null
        return if (players[player].seen == SeenVia.DUBLEES) DiscardBlock.DUBLEE_ONLY_TO_WIN else DiscardBlock.JOKER
    }

    fun drawStock(player: Int): Card {
        requireTurn(player, Phase.DRAW)
        if (stock.isEmpty()) fail("The stock is empty")
        val card = stock.removeLast()
        players[player].hand.add(card)
        drawnCard = card
        takenFromDiscard = null
        seenAtDraw = players[player].seen
        phase = Phase.PLAY
        _log.add(GameEvent.DrewStock(player))
        return card
    }

    fun drawDiscard(player: Int): Card {
        requireTurn(player, Phase.DRAW)
        if (!canDrawDiscard(player)) fail("You may not take that card")
        val card = discards.removeLast()
        players[player].hand.add(card)
        drawnCard = card
        takenFromDiscard = card
        seenAtDraw = players[player].seen
        phase = Phase.PLAY
        _log.add(GameEvent.TookDiscard(player, card))
        return card
    }

    // ----- Seeing the joker -----

    /** Pure combinations [player] could lay down now to see the joker, or null. */
    fun findShow(player: Int, prefer: ((List<Meld>) -> Double)? = null): List<Meld>? {
        val p = players[player]
        if (phase != Phase.PLAY || player != current || p.hasSeen) return null
        val need = (3 - p.startTunnelas.size).coerceAtLeast(0)
        return Melds.findDisjointPure(p.hand, need, prefer)
    }

    fun canShow(player: Int): Boolean = findShow(player) != null

    /** Lays down [melds] (or ones found automatically) and sees the joker. */
    fun show(player: Int, melds: List<Meld>? = null): List<Meld> {
        requireTurn(player, Phase.PLAY)
        val p = players[player]
        if (p.hasSeen) fail("Already seen")
        val need = (3 - p.startTunnelas.size).coerceAtLeast(0)
        val chosen = melds ?: findShow(player) ?: fail("You need three pure sequences or tunnelas")
        if (chosen.size != need) fail("Lay down exactly $need combinations")
        val cards = chosen.flatMap { it.cards }
        if (cards.distinct().size != cards.size || !p.hand.containsAll(cards)) fail("Those cards are not in your hand")
        if (chosen.any { !Melds.isPure(it.cards) }) fail("Only pure sequences and tunnelas")
        val pureMelds = chosen.map { Meld(it.cards, Melds.naturalType(it.cards[0], it.cards[1], it.cards[2])!!) }
        p.hand.removeAll(cards)
        p.shownMelds.addAll(pureMelds)
        p.seen = SeenVia.MELDS
        val chose = chooseTipluIfNeeded()
        _log.add(GameEvent.ShowedMelds(player, pureMelds, chose))
        return pureMelds
    }

    fun canShowDublees(player: Int): Boolean {
        val p = players[player]
        return phase == Phase.PLAY && player == current && !p.hasSeen && Melds.dublees(p.hand).size >= 7
    }

    /** Lays down seven dublees ([dublees], or the first seven found) and sees the joker. */
    fun showDublees(player: Int, dublees: List<Dublee>? = null): List<Dublee> {
        requireTurn(player, Phase.PLAY)
        if (!canShowDublees(player)) fail("You need seven dublees")
        val p = players[player]
        val chosen = dublees ?: Melds.dublees(p.hand).take(7)
        val cards = chosen.flatMap { it.cards }
        if (chosen.size != 7 || cards.distinct().size != 14 || !p.hand.containsAll(cards)) fail("Choose seven dublees from your hand")
        p.hand.removeAll(chosen.flatMap { it.cards })
        p.shownDublees.addAll(chosen)
        p.seen = SeenVia.DUBLEES
        val chose = chooseTipluIfNeeded()
        _log.add(GameEvent.ShowedDublees(player, chosen, chose))
        return chosen
    }

    /** The first player to see picks a random card from the middle of the stock. */
    private fun chooseTipluIfNeeded(): Boolean {
        if (tiplu != null) return false
        if (stock.isEmpty()) reshuffle()
        if (stock.isEmpty()) {
            // No card left anywhere to choose; use the top discard.
            tiplu = discards.removeLast()
            return true
        }
        val n = stock.size
        val lo = n / 4
        val hi = maxOf(lo + 1, n - n / 4)
        val idx = random.nextInt(lo, hi)
        tiplu = stock.removeAt(idx)
        return true
    }

    // ----- Winning -----

    /** A way for [player] to end the hand now, or null. */
    fun findWin(player: Int, preferredDiscard: Card? = null): WinPlan? {
        val p = players[player]
        if (phase != Phase.PLAY || player != current) return null
        return when (p.seen) {
            SeenVia.NONE -> null
            SeenVia.MELDS -> {
                val ctx = contextFor(player)
                val options = p.hand.filter { it != takenFromDiscard }
                val ordered = buildList {
                    if (preferredDiscard != null && preferredDiscard in options) add(preferredDiscard)
                    // Try throwing non-wild cards first, and each face only once.
                    addAll(options.sortedBy { if (ctx.isWild(it)) 1 else 0 })
                }.distinctBy { it.face }
                for (d in ordered) {
                    val rest = p.hand - d
                    val melds = Melds.partition(rest, ctx) ?: continue
                    return WinPlan(d, melds, emptyList(), byDublees = false)
                }
                null
            }
            SeenVia.DUBLEES -> {
                val pairs = Melds.dublees(p.hand)
                if (p.shownDublees.size + pairs.size < 8) return null
                val needed = pairs.take(8 - p.shownDublees.size)
                val used = needed.flatMap { it.cards }.toSet()
                val options = p.hand.filter { it !in used && it != takenFromDiscard }
                val d = preferredDiscard?.takeIf { it in options } ?: options.firstOrNull() ?: return null
                WinPlan(d, emptyList(), needed, byDublees = true)
            }
        }
    }

    fun canWin(player: Int): Boolean = findWin(player) != null

    /** Ends the hand with [player] as winner. */
    fun declareWin(player: Int, preferredDiscard: Card? = null): RoundResult {
        requireTurn(player, Phase.PLAY)
        val plan = findWin(player, preferredDiscard) ?: fail("You cannot finish yet")
        val p = players[player]
        p.hand.remove(plan.discard)
        discards.add(plan.discard)
        _log.add(GameEvent.Discarded(player, plan.discard))
        _log.add(GameEvent.Won(player, plan.byDublees))
        return finish(player, plan)
    }

    // ----- Discarding -----

    fun canDiscard(player: Int, card: Card): Boolean {
        if (phase != Phase.PLAY || player != current) return false
        val p = players[player]
        if (card !in p.hand || card == takenFromDiscard) return false
        // A dublee player may take a discard only to win with it.
        if (seenAtDraw == SeenVia.DUBLEES && takenFromDiscard != null) return false
        return true
    }

    fun discard(player: Int, card: Card) {
        requireTurn(player, Phase.PLAY)
        if (card == takenFromDiscard) fail("You cannot throw the card you just picked up")
        if (!canDiscard(player, card)) fail("You cannot throw that card")
        val p = players[player]
        p.hand.remove(card)
        discards.add(card)
        p.hasPlayed = true
        _log.add(GameEvent.Discarded(player, card))
        endTurn()
    }

    private fun endTurn() {
        takenFromDiscard = null
        drawnCard = null
        if (stock.isEmpty()) reshuffle()
        if (stock.isEmpty()) {
            _log.add(GameEvent.NoWinner(current))
            finish(null, null)
            return
        }
        current = (current + 1) % playerCount
        phase = Phase.DRAW
    }

    /** All discards except the top one become the new stock; the tiplu stays at the bottom. */
    private fun reshuffle() {
        if (discards.size <= 1) return
        val top = discards.removeLast()
        stock.addAll(discards.shuffled(random))
        discards.clear()
        discards.add(top)
        _log.add(GameEvent.StockReshuffled(current))
    }

    private fun finish(winner: Int?, plan: WinPlan?): RoundResult {
        phase = Phase.ROUND_OVER
        val seen = players.map { it.hasSeen }
        val t = tiplu
        val breakdown = players.map { p ->
            if (p.hasSeen && t != null) Scoring.points(p.allCards, p.startTunnelas, t.face) else emptyList()
        }
        val points = breakdown.map { items -> items.sumOf { it.points } }
        val net = if (winner == null) List(playerCount) { 0 } else Scoring.settle(points, seen, winner, plan!!.byDublees)
        val r = RoundResult(
            winner = winner,
            byDublees = plan?.byDublees == true,
            tiplu = t,
            seen = seen,
            points = points,
            breakdown = breakdown,
            net = net,
            winningMelds = plan?.melds.orEmpty(),
            winningDublees = plan?.dublees.orEmpty(),
            finalDiscard = plan?.discard,
        )
        result = r
        return r
    }
}

enum class DiscardBlock { NOT_NOW, JOKER, DUBLEE_ONLY_TO_WIN }
