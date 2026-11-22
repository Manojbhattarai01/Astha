package com.astha.marriage.engine

import kotlin.random.Random

enum class BotLevel { EASY, HARD }

/**
 * A computer player. It only uses what its seat may know: its own hand, the
 * table, and the tiplu once it has seen it.
 *
 * [BotLevel.HARD] also counts which cards are still live (not visible in the
 * discard pile, on the table or in its own hand), values partial sets by how
 * many cards could still complete them, and avoids feeding the next player.
 */
class Bot(private val random: Random = Random.Default, val level: BotLevel = BotLevel.HARD) {

    /** Copies of each face (index suit*13 + rank-1) that might still turn up. Null on EASY. */
    private var live: IntArray? = null

    private fun faceIndex(f: Face) = f.suit.ordinal * 13 + f.rank - 1

    private fun liveOf(f: Face): Int = live?.get(faceIndex(f)) ?: 3

    private fun computeLive(game: MarriageGame, me: Int): IntArray? {
        if (level == BotLevel.EASY) return null
        val counts = IntArray(52) { 3 }
        fun see(c: Card) {
            val i = faceIndex(c.face)
            if (counts[i] > 0) counts[i]--
        }
        game.discardPile.forEach(::see)
        game.players.forEach { p ->
            p.startTunnelas.forEach { m -> m.cards.forEach(::see) }
            p.shownMelds.forEach { m -> m.cards.forEach(::see) }
            p.shownDublees.forEach { d -> d.cards.forEach(::see) }
        }
        game.players[me].hand.forEach(::see)
        if (game.players[me].hasSeen) game.tiplu?.let(::see)
        return counts
    }

    /** Plays one full turn for the current player of [game]. */
    fun playTurn(game: MarriageGame) {
        val me = game.current
        val p = game.players[me]
        if (!p.hasPlayed) game.exposeTunnelas(me)
        live = computeLive(game, me)

        // 1. Draw.
        if (game.canDrawDiscard(me) && wantsDiscard(game, me)) game.drawDiscard(me) else game.drawStock(me)

        // 2. See the joker if possible.
        if (!p.hasSeen) {
            val dubleeMode = prefersDublees(p)
            if (dubleeMode && game.canShowDublees(me)) {
                game.showDublees(me)
            } else {
                val show = game.findShow(me) { melds ->
                    val used = melds.flatMap { it.cards }.toSet()
                    evaluate(p.hand.filter { it !in used }, JokerContext.UNSEEN, p, dubleeMode = false)
                }
                if (show != null) game.show(me, show)
                else if (game.canShowDublees(me)) game.showDublees(me)
            }
        }

        // 3. Finish if possible.
        if (game.canWin(me)) {
            game.declareWin(me)
            return
        }

        // 4. Discard.
        game.discard(me, chooseDiscard(game, me))
    }

    /** Cards the next player has picked up from the discard pile this hand. */
    private fun nextPlayerWants(game: MarriageGame, me: Int): List<Card> {
        val next = (me + 1) % game.playerCount
        return game.log.filterIsInstance<GameEvent.TookDiscard>().filter { it.player == next }.map { it.card }
    }

    private fun prefersDublees(p: PlayerState): Boolean {
        if (p.seen == SeenVia.DUBLEES) return true
        if (p.seen == SeenVia.MELDS || p.startTunnelas.isNotEmpty()) return false
        val pairs = Melds.dublees(p.hand).size
        val pure = Melds.findDisjointPure(p.hand, 2) != null
        return pairs >= 6 || (pairs >= 5 && !pure)
    }

    private fun wantsDiscard(game: MarriageGame, me: Int): Boolean {
        val p = game.players[me]
        val top = game.topDiscard ?: return false
        // A dublee player who may take it is completing the winning pair.
        if (p.seen == SeenVia.DUBLEES) return true
        val ctx = game.contextFor(me)
        val dublee = prefersDublees(p)
        val now = evaluate(p.hand, ctx, p, dublee)
        val with = p.hand + top
        val best = with.filter { it != top }.distinctBy { it.face }
            .maxOf { x -> evaluate(with - x, ctx, p, dublee) }
        if (level == BotLevel.EASY) return best > now + 4.0
        // Compare with what a blind draw from the stock is expected to bring.
        return best > now + expectedGain(p.hand, ctx, p, dublee) + 0.5
    }

    /**
     * How much one draw from the stock is expected to improve [hand], weighting each
     * face by its live copies. Only HARD bots look ahead like this.
     */
    private fun expectedGain(hand: List<Card>, ctx: JokerContext, p: PlayerState, dublee: Boolean): Double {
        val counts = live ?: return 0.0
        val base = evaluate(hand, ctx, p, dublee)
        var total = 0
        var gain = 0.0
        for (i in 0 until 52) {
            val n = counts[i]
            if (n == 0) continue
            // Any physical copy not already in hand stands for the drawn card.
            val drawn = (0..2).map { Card.of(Suit.entries[i / 13], i % 13 + 1, it) }.firstOrNull { it !in hand } ?: continue
            val improved = evaluate(hand + drawn, ctx, p, dublee) - base
            total += n
            if (improved > 0) gain += n * improved
        }
        return if (total == 0) 0.0 else gain / total
    }

    fun chooseDiscard(game: MarriageGame, me: Int): Card {
        val p = game.players[me]
        val ctx = game.contextFor(me)
        val dublee = prefersDublees(p)
        val options = p.hand.filter { game.canDiscard(me, it) }
        var best = options.first()
        var bestScore = Double.NEGATIVE_INFINITY
        if (live == null && level == BotLevel.HARD) live = computeLive(game, me)
        val wanted = if (level == BotLevel.HARD) nextPlayerWants(game, me) else emptyList()
        val scored = options.distinctBy { it.face }.shuffled(random).map { c -> c to evaluate(p.hand - c, ctx, p, dublee) }
        // HARD: look one draw ahead for the most promising few.
        val ahead = if (level == BotLevel.HARD) {
            scored.sortedByDescending { it.second }.take(5)
                .associate { (c, _) -> c to expectedGain(p.hand - c, ctx, p, dublee) }
        } else emptyMap()
        for ((c, base) in scored) {
            var s = base + (ahead[c] ?: if (level == BotLevel.HARD) -1000.0 else 0.0)
            // Keep point cards when they are known.
            if (ctx.isWild(c)) s -= 6.0
            // Don't hand the next player a card that fits what they have been picking up.
            if (wanted.any { w -> w.face == c.face || Melds.isSequencePartial(w, c) || Melds.isTripletPartial(w, c) }) s -= 3.0
            if (s > bestScore) {
                bestScore = s
                best = c
            }
        }
        return best
    }

    /** Higher is better: how close [hand] is to finishing. */
    fun evaluate(hand: List<Card>, ctx: JokerContext, p: PlayerState, dubleeMode: Boolean): Double {
        if (dubleeMode) return evaluateDublees(hand)
        return if (ctx.tiplu == null) evaluateUnseen(hand, p) else evaluateSeen(hand, ctx)
    }

    private fun evaluateDublees(hand: List<Card>): Double {
        val pairs = Melds.dublees(hand).size
        // Cards in a group of three are only one pair; the third is spare.
        return pairs * 10.0
    }

    /** Before seeing: build pure combinations first, then anything natural. */
    private fun evaluateUnseen(hand: List<Card>, p: PlayerState): Double {
        val need = (3 - p.startTunnelas.size).coerceAtLeast(0)
        val (pure, rest) = maxDisjoint(Melds.allPure(hand), hand)
        var score = 100.0 * minOf(pure.size, need) + 40.0 * (pure.size - minOf(pure.size, need)).coerceAtLeast(0)
        val (naturals, rest2) = maxDisjoint(Melds.allNatural(rest), rest)
        score += 15.0 * naturals.size
        score += partialScore(rest2, pureOnly = true) * 8.0
        score += partialScore(rest2, pureOnly = false) * 2.0
        return score
    }

    /** After seeing: how many cards are still missing, using known jokers. */
    private fun evaluateSeen(hand: List<Card>, ctx: JokerContext): Double {
        val jokers = hand.count { ctx.isWild(it) }
        val naturalsOnly = hand.filter { !ctx.isWild(it) }
        val groups = hand.size / 3
        val (complete, rest) = maxDisjoint(Melds.allNatural(naturalsOnly), naturalsOnly)
        val partials = greedyPartials(rest, ctx)
        val c = minOf(complete.size, groups)
        val q = minOf(partials.size, groups - c)
        val singles = rest.size - 2 * q
        val r = groups - c - q
        val fromSingles = minOf(r, singles)
        val need = q + 2 * fromSingles + 3 * (r - fromSingles)
        val missing = (need - jokers).coerceAtLeast(0)
        val partialValue = partials.sumOf { (a, b) ->
            if (Melds.isTripletPartial(a, b)) {
                outsWeight(Suit.entries.filter { it != a.suit && it != b.suit }.map { Face(it, a.rank) }, 2)
            } else {
                sequenceOuts(a, b)
            }
        }
        return -20.0 * missing + 2.0 * jokers + partialValue
    }

    /** Disjoint combinations covering as many cards as possible (pure ones count a bit more). */
    private fun maxDisjoint(candidates: List<Meld>, cards: List<Card>): Pair<List<Meld>, List<Card>> {
        var best: List<Meld> = emptyList()
        var bestScore = -1.0
        var nodes = 0
        fun dfs(start: Int, chosen: ArrayList<Meld>, used: HashSet<Card>, score: Double) {
            nodes++
            if (score > bestScore) {
                bestScore = score
                best = chosen.toList()
            }
            if (nodes > 3000) return
            for (i in start until candidates.size) {
                val m = candidates[i]
                if (m.cards.any { it in used }) continue
                chosen.add(m)
                used.addAll(m.cards)
                dfs(i + 1, chosen, used, score + if (m.type.isPure) 1.1 else 1.0)
                chosen.removeAt(chosen.size - 1)
                m.cards.forEach { used.remove(it) }
            }
        }
        dfs(0, ArrayList(), HashSet(), 0.0)
        val used = best.flatMap { it.cards }.toSet()
        return best to cards.filter { it !in used }
    }

    /** Pairs one wild card (or a natural third card) away from a combination. */
    private fun greedyPartials(cards: List<Card>, ctx: JokerContext): List<Pair<Card, Card>> {
        val left = cards.toMutableList()
        val out = ArrayList<Pair<Card, Card>>()
        // Adjacent-in-suit first, then two apart, then same rank.
        val tests: List<(Card, Card) -> Boolean> = listOf(
            { a, b -> a.suit == b.suit && Melds.isSequencePartial(a, b) && kotlin.math.abs(a.rank - b.rank) == 1 },
            { a, b -> Melds.isSequencePartial(a, b) },
            { a, b -> Melds.isTripletPartial(a, b) },
        )
        for (test in tests) {
            var i = 0
            while (i < left.size) {
                val a = left[i]
                val j = (i + 1 until left.size).firstOrNull { test(a, left[it]) }
                if (j != null) {
                    out.add(a to left[j])
                    left.removeAt(j)
                    left.removeAt(i)
                } else i++
            }
        }
        return out
    }

    /** 0..1: how likely a partial set is to be completed, from the live copies of its [outs]. */
    private fun outsWeight(outs: List<Face>, full: Int): Double {
        if (live == null) return 1.0
        val n = outs.sumOf { liveOf(it) }
        return (n.toDouble() / full).coerceAtMost(1.0)
    }

    /** Value of two same-suit cards that one more card would make a pure sequence. */
    private fun sequenceOuts(a: Card, b: Card): Double {
        // The ranks that would complete the run (A-2 → 3, Q-K → J or A, 4-6 → 5, ...).
        val outs = (1..13)
            .filter { r -> r != a.rank && r != b.rank && Melds.isPure(listOf(a, b, Card.of(a.suit, r))) }
            .map { Face(a.suit, it) }
        val adjacent = outs.size >= 2
        return (if (adjacent) 1.0 else 0.6) * outsWeight(outs, if (adjacent) 3 else 2)
    }

    /** Counts pairs that could grow into a combination. */
    private fun partialScore(cards: List<Card>, pureOnly: Boolean): Double {
        var s = 0.0
        for (i in cards.indices) for (j in i + 1 until cards.size) {
            val a = cards[i]
            val b = cards[j]
            s += when {
                a.face == b.face -> if (pureOnly) outsWeight(listOf(a.face), 1) else 0.0
                Melds.isSequencePartial(a, b) -> if (pureOnly) sequenceOuts(a, b) else 0.0
                Melds.isTripletPartial(a, b) -> if (pureOnly) 0.0 else 1.0
                else -> 0.0
            }
        }
        return s
    }
}
