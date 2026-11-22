package com.astha.marriage

import android.app.Application
import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.astha.marriage.engine.Bot
import com.astha.marriage.engine.Card
import com.astha.marriage.engine.DiscardBlock
import com.astha.marriage.engine.GameEvent
import com.astha.marriage.engine.GameRuleException
import com.astha.marriage.engine.MarriageGame
import com.astha.marriage.engine.Phase
import com.astha.marriage.engine.SeenVia
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.random.Random

enum class Screen { HOME, RULES, GAME }

enum class SortMode { SUIT, RANK }

/** A short message to show the human, chosen from [Strings]. */
enum class Notice { CANNOT_TAKE_JOKER, DUBLEE_ONLY_TO_WIN, CANNOT_THROW_TAKEN, CANNOT_FINISH, NEED_THREE_PURE }

class GameViewModel(app: Application) : AndroidViewModel(app) {
    private val prefs = app.getSharedPreferences("marriage", Context.MODE_PRIVATE)

    var language by mutableStateOf(
        runCatching { Language.valueOf(prefs.getString("language", "EN")!!) }.getOrDefault(Language.EN),
    )
        private set

    var playerCount by mutableIntStateOf(prefs.getInt("players", 4).coerceIn(2, 5))
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

    var selected: Card? by mutableStateOf(null)
        private set

    var sortMode by mutableStateOf(SortMode.SUIT)

    var notice: Notice? by mutableStateOf(null)
        private set

    var showResult by mutableStateOf(false)

    private var dealer = 0
    private var handSettled = false
    private val random = Random(System.nanoTime())
    private val bot = Bot(random)
    private var botJob: Job? = null

    fun updateLanguage(l: Language) {
        language = l
        prefs.edit().putString("language", l.name).apply()
    }

    fun updatePlayerCount(n: Int) {
        playerCount = n.coerceIn(2, 5)
        prefs.edit().putInt("players", playerCount).apply()
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
        selected = null
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

    // ----- Human actions -----

    fun tapStock() {
        val g = game ?: return
        if (!isHumanTurn || g.phase != Phase.DRAW) return
        act { g.drawStock(HUMAN); selected = null }
    }

    fun tapDiscard() {
        val g = game ?: return
        if (!isHumanTurn || g.phase != Phase.DRAW) return
        when (g.discardBlockReason(HUMAN)) {
            null -> act { g.drawDiscard(HUMAN); selected = null }
            DiscardBlock.JOKER -> notice = Notice.CANNOT_TAKE_JOKER
            DiscardBlock.DUBLEE_ONLY_TO_WIN -> notice = Notice.DUBLEE_ONLY_TO_WIN
            DiscardBlock.NOT_NOW -> Unit
        }
    }

    fun tapCard(card: Card) {
        selected = if (selected == card) null else card
    }

    fun exposeTunnelas() {
        val g = game ?: return
        act { g.exposeTunnelas(HUMAN) }
    }

    fun showSets() {
        val g = game ?: return
        if (!g.canShow(HUMAN)) {
            notice = Notice.NEED_THREE_PURE
            return
        }
        act { g.show(HUMAN); selected = null }
    }

    fun showDublees() {
        val g = game ?: return
        act { g.showDublees(HUMAN); selected = null }
    }

    fun finish() {
        val g = game ?: return
        if (!g.canWin(HUMAN)) {
            notice = Notice.CANNOT_FINISH
            return
        }
        act { g.declareWin(HUMAN, selected) }
        afterChange()
    }

    fun throwSelected() {
        val g = game ?: return
        val card = selected ?: return
        if (card == g.takenFromDiscard) {
            notice = Notice.CANNOT_THROW_TAKEN
            return
        }
        if (!g.canDiscard(HUMAN, card)) return
        act { g.discard(HUMAN, card) }
        selected = null
        afterChange()
    }

    /** Lets the computer play the human's turn. Used by tests to reach later game states. */
    @androidx.annotation.VisibleForTesting
    fun autoPlayHumanTurn() {
        val g = game ?: return
        if (!isHumanTurn) return
        if (g.phase == Phase.DRAW) bot.playTurn(g) else g.discard(HUMAN, bot.chooseDiscard(g, HUMAN))
        selected = null
        touch()
        afterChange()
    }

    private inline fun act(block: () -> Unit) {
        try {
            block()
        } catch (_: GameRuleException) {
            // The buttons only allow legal moves; ignore anything that slips through.
        }
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
                delay(BOT_DELAY_MS)
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
            delay(700)
            showResult = true
        }
    }

    fun playerName(index: Int, s: Strings): String = if (index == HUMAN) s.you else s.botNames[index - 1]

    /** The most recent events, newest last, for the action log. */
    fun recentEvents(count: Int): List<GameEvent> =
        game?.log?.filter { it !is GameEvent.DrewStock || it.player != HUMAN }?.takeLast(count).orEmpty()

    fun humanHand(): List<Card> {
        val g = game ?: return emptyList()
        val hand = g.players[HUMAN].hand
        val ctx = g.contextFor(HUMAN)
        fun rankValue(c: Card) = if (c.rank == 1) 14 else c.rank
        val suitOrder = listOf(com.astha.marriage.engine.Suit.SPADES, com.astha.marriage.engine.Suit.HEARTS,
            com.astha.marriage.engine.Suit.CLUBS, com.astha.marriage.engine.Suit.DIAMONDS)
        return when (sortMode) {
            SortMode.SUIT -> hand.sortedWith(compareBy({ if (ctx.isWild(it)) 1 else 0 }, { suitOrder.indexOf(it.suit) }, { rankValue(it) }))
            SortMode.RANK -> hand.sortedWith(compareBy({ if (ctx.isWild(it)) 1 else 0 }, { rankValue(it) }, { suitOrder.indexOf(it.suit) }))
        }
    }

    val humanSeen: Boolean get() = game?.players?.get(HUMAN)?.seen?.let { it != SeenVia.NONE } == true

    companion object {
        const val HUMAN = 0
        const val BOT_DELAY_MS = 1100L
    }
}
