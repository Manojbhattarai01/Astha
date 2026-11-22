package com.astha.marriage

import android.app.Application
import android.content.Context
import androidx.annotation.VisibleForTesting
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.astha.marriage.engine.Arrange
import com.astha.marriage.engine.Bot
import com.astha.marriage.engine.BotLevel
import com.astha.marriage.engine.Card
import com.astha.marriage.engine.DiscardBlock
import com.astha.marriage.engine.GameEvent
import com.astha.marriage.engine.GameRuleException
import com.astha.marriage.engine.MarriageGame
import com.astha.marriage.engine.Melds
import com.astha.marriage.engine.Phase
import com.astha.marriage.engine.SeenVia
import com.astha.marriage.engine.Suit
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.random.Random

enum class Screen { HOME, RULES, GAME }

/** How the hand is laid out: grouped into sets, or sorted by suit or rank. */
enum class SortMode { SETS, SUIT, RANK }

/** A short message to show the human, chosen from [Strings]. */
enum class Notice {
    CANNOT_TAKE_JOKER, DUBLEE_ONLY_TO_WIN, CANNOT_THROW_TAKEN, CANNOT_FINISH, NEED_THREE_PURE,
    SELECTION_NOT_PURE, SELECTION_NOT_DUBLEES, SELECT_ONE_TO_THROW,
}

class GameViewModel(app: Application) : AndroidViewModel(app) {
    private val prefs = app.getSharedPreferences("marriage", Context.MODE_PRIVATE)

    var language by mutableStateOf(
        runCatching { Language.valueOf(prefs.getString("language", "EN")!!) }.getOrDefault(Language.EN),
    )
        private set

    var playerCount by mutableIntStateOf(prefs.getInt("players", 4).coerceIn(2, 5))
        private set

    var level by mutableStateOf(
        runCatching { BotLevel.valueOf(prefs.getString("level", "HARD")!!) }.getOrDefault(BotLevel.HARD),
    )
        private set

    var screen by mutableStateOf(Screen.HOME)

    var game: MarriageGame? by mutableStateOf(null)
        private set

    /** Bumped after every change to [game], which is not itself observable. */
    var version by mutableIntStateOf(0)
        private set

    var totals: List<Int> by mutableStateOf(emptyList())
        private set

    var handNumber by mutableIntStateOf(0)
        private set

    /** Cards the human has tapped. One card can be thrown; several can be laid down. */
    var selection: Set<Card> by mutableStateOf(emptySet())
        private set

    var sortMode by mutableStateOf(
        runCatching { SortMode.valueOf(prefs.getString("sort", "SETS")!!) }.getOrDefault(SortMode.SETS),
    )
        private set

    var notice: Notice? by mutableStateOf(null)
        private set

    var showResult by mutableStateOf(false)

    /** Pause between computer moves; tests set it to 0. */
    var botDelayMs = 1100L

    private var dealer = 0
    private var handSettled = false
    private val random = Random(System.nanoTime())
    private var bot = Bot(random, level)
    private val helper = Bot(random, BotLevel.HARD)
    private var botJob: Job? = null

    fun updateLanguage(l: Language) {
        language = l
        prefs.edit().putString("language", l.name).apply()
    }

    fun updatePlayerCount(n: Int) {
        playerCount = n.coerceIn(2, 5)
        prefs.edit().putInt("players", playerCount).apply()
    }

    fun updateLevel(l: BotLevel) {
        level = l
        bot = Bot(random, l)
        prefs.edit().putString("level", l.name).apply()
    }

    fun cycleSort() {
        sortMode = SortMode.entries[(sortMode.ordinal + 1) % SortMode.entries.size]
        prefs.edit().putString("sort", sortMode.name).apply()
    }

    fun startMatch() {
        totals = List(playerCount) { 0 }
        handNumber = 0
        dealer = random.nextInt(playerCount)
        screen = Screen.GAME
        startHand()
    }

    fun nextHand() {
        dealer = (dealer + 1) % playerCount
        startHand()
    }

    fun leaveGame() {
        botJob?.cancel()
        game = null
        showResult = false
        screen = Screen.HOME
    }

    private fun startHand() {
        botJob?.cancel()
        game = MarriageGame(playerCount, dealer, Random(random.nextLong()))
        handNumber++
        handSettled = false
        selection = emptySet()
        showResult = false
        notice = null
        touch()
        runBots()
    }

    private fun touch() {
        version++
    }

    fun clearNotice() {
        notice = null
    }

    val isHumanTurn: Boolean
        get() = game?.let { it.current == HUMAN && it.phase != Phase.ROUND_OVER } == true

    /** The single selected card, if exactly one is selected. */
    val selectedOne: Card? get() = selection.singleOrNull()

    // ----- Human actions -----

    fun tapStock() {
        val g = game ?: return
        if (!isHumanTurn || g.phase != Phase.DRAW) return
        act { g.drawStock(HUMAN) }
    }

    fun tapDiscard() {
        val g = game ?: return
        if (!isHumanTurn || g.phase != Phase.DRAW) return
        when (g.discardBlockReason(HUMAN)) {
            null -> act { g.drawDiscard(HUMAN) }
            DiscardBlock.JOKER -> notice = Notice.CANNOT_TAKE_JOKER
            DiscardBlock.DUBLEE_ONLY_TO_WIN -> notice = Notice.DUBLEE_ONLY_TO_WIN
            DiscardBlock.NOT_NOW -> Unit
        }
    }

    fun tapCard(card: Card) {
        selection = if (card in selection) selection - card else selection + card
    }

    fun clearSelection() {
        selection = emptySet()
    }

    fun exposeTunnelas() {
        val g = game ?: return
        act { g.exposeTunnelas(HUMAN) }
    }

    /**
     * Sees the joker. With nothing selected the app picks the sets; otherwise the
     * selected cards must make exactly the pure sets needed.
     */
    fun showSets() {
        val g = game ?: return
        if (!g.canShow(HUMAN)) {
            notice = Notice.NEED_THREE_PURE
            return
        }
        if (selection.isEmpty()) {
            act { g.show(HUMAN) }
            return
        }
        val need = (3 - g.players[HUMAN].startTunnelas.size).coerceAtLeast(0)
        val chosen = selection.toList()
        val melds = if (chosen.size == need * 3) Melds.findDisjointPure(chosen, need) else null
        if (melds == null) {
            notice = Notice.SELECTION_NOT_PURE
            return
        }
        act { g.show(HUMAN, melds) }
    }

    /** Sees the joker with seven dublees: the selected 14 cards, or chosen by the app. */
    fun showDublees() {
        val g = game ?: return
        if (selection.isEmpty()) {
            act { g.showDublees(HUMAN) }
            return
        }
        val pairs = Melds.dublees(selection.toList())
        if (selection.size != 14 || pairs.size != 7) {
            notice = Notice.SELECTION_NOT_DUBLEES
            return
        }
        act { g.showDublees(HUMAN, pairs) }
    }

    fun finish() {
        val g = game ?: return
        if (!g.canWin(HUMAN)) {
            notice = Notice.CANNOT_FINISH
            return
        }
        act { g.declareWin(HUMAN, selectedOne) }
        afterChange()
    }

    fun throwSelected() {
        val g = game ?: return
        val card = selectedOne
        if (card == null) {
            notice = Notice.SELECT_ONE_TO_THROW
            return
        }
        if (card == g.takenFromDiscard) {
            notice = Notice.CANNOT_THROW_TAKEN
            return
        }
        if (!g.canDiscard(HUMAN, card)) return
        act { g.discard(HUMAN, card) }
        afterChange()
    }

    /** Lets the computer play the human's turn. Used by tests to reach later game states. */
    @VisibleForTesting
    fun autoPlayHumanTurn() {
        val g = game ?: return
        if (!isHumanTurn) return
        if (g.phase == Phase.DRAW) helper.playTurn(g) else g.discard(HUMAN, helper.chooseDiscard(g, HUMAN))
        selection = emptySet()
        touch()
        afterChange()
    }

    private inline fun act(block: () -> Unit) {
        try {
            block()
        } catch (_: GameRuleException) {
            // The buttons only allow legal moves; ignore anything that slips through.
        }
        selection = emptySet()
        touch()
    }

    private fun afterChange() {
        val g = game ?: return
        if (g.phase == Phase.ROUND_OVER) onHandOver() else runBots()
    }

    private fun runBots() {
        botJob?.cancel()
        botJob = viewModelScope.launch {
            while (true) {
                val g = game ?: return@launch
                if (g.phase == Phase.ROUND_OVER) {
                    onHandOver()
                    return@launch
                }
                if (g.current == HUMAN) return@launch
                delay(botDelayMs)
                bot.playTurn(g)
                touch()
            }
        }
    }

    private fun onHandOver() {
        val g = game ?: return
        val r = g.result ?: return
        if (handSettled) return
        handSettled = true
        totals = totals.mapIndexed { i, t -> t + r.net[i] }
        viewModelScope.launch {
            delay(900)
            showResult = true
        }
    }

    fun playerName(index: Int, s: Strings): String = if (index == HUMAN) s.you else s.botNames[index - 1]

    /** The most recent events, newest last, for the action log. */
    fun recentEvents(count: Int): List<GameEvent> =
        game?.log?.filter { it !is GameEvent.DrewStock || it.player != HUMAN }?.takeLast(count).orEmpty()

    /** The human's hand in display groups, according to [sortMode]. */
    fun humanGroups(): List<List<Card>> {
        val g = game ?: return emptyList()
        val hand = g.players[HUMAN].hand
        val ctx = g.contextFor(HUMAN)
        val suitOrder = listOf(Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS)
        fun rankValue(c: Card) = if (c.rank == 1) 14 else c.rank
        return when (sortMode) {
            SortMode.SETS -> {
                val a = Arrange.arrange(hand, ctx)
                a.sets.map { displayOrder(it.cards, ctx) } + a.partials + listOf(a.loose).filter { it.isNotEmpty() }
            }
            SortMode.SUIT -> {
                val wild = hand.filter { ctx.isWild(it) }
                hand.filter { !ctx.isWild(it) }
                    .groupBy { it.suit }
                    .toSortedMap(compareBy { suitOrder.indexOf(it) })
                    .values.map { cards -> cards.sortedBy(::rankValue) } + listOf(wild).filter { it.isNotEmpty() }
            }
            SortMode.RANK -> listOf(
                hand.sortedWith(compareBy({ if (ctx.isWild(it)) 1 else 0 }, { rankValue(it) }, { suitOrder.indexOf(it.suit) })),
            )
        }
    }

    val humanSeen: Boolean get() = game?.players?.get(HUMAN)?.seen?.let { it != SeenVia.NONE } == true

    companion object {
        const val HUMAN = 0

        /** Orders a set for display: runs in rank order (ace high after a king), jokers last. */
        fun displayOrder(cards: List<Card>, ctx: com.astha.marriage.engine.JokerContext): List<Card> {
            val highAce = cards.any { it.rank >= 12 }
            return cards.sortedWith(
                compareBy({ if (ctx.isWild(it) && Melds.naturalType(cards[0], cards[1], cards[2]) == null) 1 else 0 },
                    { if (it.rank == 1 && highAce) 14 else it.rank }),
            )
        }
    }
}
