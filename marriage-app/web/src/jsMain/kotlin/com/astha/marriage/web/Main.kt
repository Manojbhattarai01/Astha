package com.astha.marriage.web

import com.astha.marriage.English
import com.astha.marriage.Language
import com.astha.marriage.Strings
import com.astha.marriage.engine.Arrange
import com.astha.marriage.engine.Bot
import com.astha.marriage.engine.BotLevel
import com.astha.marriage.engine.Card
import com.astha.marriage.engine.DiscardBlock
import com.astha.marriage.engine.GameEvent
import com.astha.marriage.engine.GameRuleException
import com.astha.marriage.engine.JokerContext
import com.astha.marriage.engine.MaalKind
import com.astha.marriage.engine.MarriageGame
import com.astha.marriage.engine.Melds
import com.astha.marriage.engine.Phase
import com.astha.marriage.engine.PlayerState
import com.astha.marriage.engine.Ranks
import com.astha.marriage.engine.Suit
import com.astha.marriage.stringsFor
import kotlinx.browser.document
import kotlinx.browser.window
import org.w3c.dom.Element
import org.w3c.dom.HTMLElement
import org.w3c.dom.events.Event
import kotlin.random.Random

private const val HUMAN = 0
private const val BOT_DELAY_MS = 1100
private const val FLIGHT_MS = 380
private const val FLIGHT_GAP_MS = 430

private enum class View { HOME, RULES, GAME }
private enum class Sort { SETS, SUIT, RANK }

/** localStorage may be missing or throw inside the viewer's frame. */
private object Prefs {
    fun get(key: String): String? = try {
        window.localStorage.getItem("marriage.$key")
    } catch (_: Throwable) {
        null
    }

    fun set(key: String, value: String) {
        try {
            window.localStorage.setItem("marriage.$key", value)
        } catch (_: Throwable) {
        }
    }
}

private fun esc(text: String): String =
    text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;")

private fun maalTag(kind: MaalKind): String? = when (kind) {
    MaalKind.TIPLU -> "T"
    MaalKind.POPLU -> "P"
    MaalKind.JHIPLU -> "Jh"
    MaalKind.ALTER -> "A"
    MaalKind.ORDINARY_JOKER -> "★"
    MaalKind.NONE -> null
}

/** Suit shapes on a 100×100 grid, drawn as SVG so every phone shows the same card. */
private fun suitSvg(suit: Suit, cls: String): String {
    val shape = when (suit) {
        Suit.HEARTS -> """<path d="M50 90C22 68 4 50 4 31 4 16 15 6 28 6c10 0 18 6 22 15 4-9 12-15 22-15 13 0 24 10 24 25 0 19-18 37-46 59z"/>"""
        Suit.DIAMONDS -> """<path d="M50 3l38 47-38 47-38-47z"/>"""
        Suit.SPADES -> """<path d="M50 4C30 28 6 42 6 61c0 13 10 21 22 21 8 0 14-4 17-9-1 11-5 18-12 23h34c-7-5-11-12-12-23 3 5 9 9 17 9 12 0 22-8 22-21C94 42 70 28 50 4z"/>"""
        Suit.CLUBS -> """<circle cx="50" cy="27" r="20"/><circle cx="27" cy="57" r="20"/><circle cx="73" cy="57" r="20"/><path d="M45 50c0 22-4 35-12 46h34c-8-11-12-24-12-46z"/>"""
    }
    return """<svg class="$cls" viewBox="0 0 100 100" aria-hidden="true">$shape</svg>"""
}

/** A playing card as HTML. [act] makes it tappable. */
private fun cardHtml(c: Card, maal: MaalKind = MaalKind.NONE, classes: String = "", act: String? = null): String {
    val tag = maalTag(maal)?.let { """<i class="tag">$it</i>""" } ?: ""
    val red = if (c.suit.isRed) " red" else ""
    val maalClass = if (maal != MaalKind.NONE) " maal" else ""
    val a = if (act != null) """ data-act="$act" data-id="${c.id}"""" else ""
    return """<div class="card$red$maalClass $classes"$a><b>${Ranks.label(c.rank)}</b>${suitSvg(c.suit, "sm")}$tag${suitSvg(c.suit, "big")}</div>"""
}

private fun backHtml(classes: String = "", label: String = "", act: String? = null): String {
    val a = if (act != null) """ data-act="$act"""" else ""
    return """<div class="card back $classes"$a>${if (label.isNotEmpty()) "<b>$label</b>" else ""}</div>"""
}

/** Orders a set for display: runs in rank order (ace high after a king). */
private fun displayOrder(cards: List<Card>): List<Card> {
    val highAce = cards.any { it.rank >= 12 }
    return cards.sortedBy { if (it.rank == 1 && highAce) 14 else it.rank }
}

private fun laidCards(p: PlayerState): List<List<Card>> =
    p.startTunnelas.map { it.cards } + p.shownMelds.map { displayOrder(it.cards) } + p.shownDublees.map { it.cards }

class App(private val root: HTMLElement, private val overlay: HTMLElement) {
    private var language = runCatching { Language.valueOf(Prefs.get("language") ?: "EN") }.getOrDefault(Language.EN)
    private var playerCount = (Prefs.get("players")?.toIntOrNull() ?: 4).coerceIn(2, 5)
    private var level = runCatching { BotLevel.valueOf(Prefs.get("level") ?: "HARD") }.getOrDefault(BotLevel.HARD)
    private var sort = runCatching { Sort.valueOf(Prefs.get("sort") ?: "SETS") }.getOrDefault(Sort.SETS)

    private var view = View.HOME
    private var game: MarriageGame? = null
    private var totals = List(playerCount) { 0 }
    private var handNumber = 0
    private var dealer = 0
    private var handSettled = false
    private var showResult = false
    private var inspect: Int? = null
    private var confirmQuit = false
    private val selection = LinkedHashSet<Card>()

    private val random = Random(js("Date.now()").unsafeCast<Double>().toLong())
    private var bot = Bot(random, level)
    private var botTimer: Int? = null
    private var toastTimer: Int? = null

    private var processedLog = 0
    private var pendingToDiscard = 0

    private val s: Strings get() = stringsFor(language)

    init {
        root.addEventListener("click", { e -> onClick(e) })
        render()
    }

    // ----- Events -----

    private fun onClick(e: Event) {
        val el = (e.target as? Element)?.closest("[data-act]") ?: return
        val act = el.getAttribute("data-act") ?: return
        val arg = el.getAttribute("data-v")
        val id = el.getAttribute("data-id")?.toIntOrNull()
        when (act) {
            "players" -> { playerCount = arg!!.toInt(); Prefs.set("players", arg); render() }
            "level" -> { level = BotLevel.valueOf(arg!!); bot = Bot(random, level); Prefs.set("level", arg); render() }
            "lang" -> { language = Language.valueOf(arg!!); Prefs.set("language", arg); render() }
            "play" -> startMatch()
            "rules" -> { view = View.RULES; render(); window.scrollTo(0.0, 0.0) }
            "home" -> { view = View.HOME; render() }
            "quit" -> { confirmQuit = true; render() }
            "quit-yes" -> leaveGame()
            "quit-no" -> { confirmQuit = false; render() }
            "inspect" -> { inspect = arg!!.toInt(); render() }
            "close" -> { inspect = null; render() }
            "next" -> nextHand()
            "stock" -> tapStock()
            "discard" -> tapDiscard()
            "card" -> tapCard(id!!)
            "sort" -> { sort = Sort.entries[(sort.ordinal + 1) % Sort.entries.size]; Prefs.set("sort", sort.name); render() }
            "clear" -> { selection.clear(); render() }
            "expose" -> act { it.exposeTunnelas(HUMAN) }
            "show" -> showSets()
            "dublee" -> showDublees()
            "finish" -> finish()
            "throw" -> throwSelected()
        }
    }

    // ----- Match flow -----

    private fun startMatch() {
        totals = List(playerCount) { 0 }
        handNumber = 0
        dealer = random.nextInt(playerCount)
        view = View.GAME
        startHand()
    }

    private fun nextHand() {
        dealer = (dealer + 1) % playerCount
        startHand()
    }

    private fun leaveGame() {
        stopBots()
        game = null
        confirmQuit = false
        showResult = false
        view = View.HOME
        render()
    }

    private fun startHand() {
        stopBots()
        val g = MarriageGame(playerCount, dealer, Random(random.nextLong()))
        game = g
        handNumber++
        handSettled = false
        showResult = false
        selection.clear()
        processedLog = g.log.size
        pendingToDiscard = 0
        update()
    }

    private val humanTurn: Boolean
        get() = game?.let { it.current == HUMAN && it.phase != Phase.ROUND_OVER } == true

    private fun stopBots() {
        botTimer?.let { window.clearTimeout(it) }
        botTimer = null
    }

    private fun scheduleBots() {
        stopBots()
        val g = game ?: return
        if (g.phase == Phase.ROUND_OVER) {
            handOver()
            return
        }
        if (g.current == HUMAN) return
        botTimer = window.setTimeout({
            botTimer = null
            if (game === g && g.phase != Phase.ROUND_OVER && g.current != HUMAN) {
                bot.playTurn(g)
                update()
            }
        }, BOT_DELAY_MS)
    }

    private fun handOver() {
        val g = game ?: return
        val r = g.result ?: return
        if (handSettled) return
        handSettled = true
        totals = totals.mapIndexed { i, t -> t + r.net[i] }
        window.setTimeout({
            if (game === g) {
                showResult = true
                render()
            }
        }, 1000)
    }

    /** After any change to the game: animate new moves, redraw, let the bots play. */
    private fun update() {
        val g = game ?: return
        val fresh = g.log.drop(processedLog)
        processedLog = g.log.size
        val flights = fresh.mapNotNull { e ->
            val who = if (e.player == HUMAN) "hand" else "p${e.player}"
            when (e) {
                is GameEvent.DrewStock -> Triple<Card?, String, String>(null, "deck", who)
                is GameEvent.TookDiscard -> Triple(e.card, "discard", who)
                is GameEvent.Discarded -> Triple(e.card, who, "discard")
                else -> null
            }
        }
        pendingToDiscard += flights.count { it.third == "discard" }
        render()
        flights.forEachIndexed { i, (card, from, to) ->
            window.setTimeout({ fly(card, from, to) }, i * FLIGHT_GAP_MS)
        }
        scheduleBots()
    }

    // ----- Human actions -----

    private inline fun act(block: (MarriageGame) -> Unit) {
        val g = game ?: return
        try {
            block(g)
        } catch (_: GameRuleException) {
        }
        selection.clear()
        update()
    }

    private fun tapStock() {
        val g = game ?: return
        if (humanTurn && g.phase == Phase.DRAW) act { it.drawStock(HUMAN) }
    }

    private fun tapDiscard() {
        val g = game ?: return
        if (!humanTurn || g.phase != Phase.DRAW) return
        when (g.discardBlockReason(HUMAN)) {
            null -> act { it.drawDiscard(HUMAN) }
            DiscardBlock.JOKER -> toast(s.cannotTakeJoker)
            DiscardBlock.DUBLEE_ONLY_TO_WIN -> toast(s.dubleeOnlyToWin)
            DiscardBlock.NOT_NOW -> Unit
        }
    }

    private fun tapCard(id: Int) {
        val card = game?.players?.get(HUMAN)?.hand?.firstOrNull { it.id == id } ?: return
        if (!selection.remove(card)) selection.add(card)
        render()
    }

    private fun showSets() {
        val g = game ?: return
        if (!g.canShow(HUMAN)) {
            toast(s.needThreePure)
            return
        }
        if (selection.isEmpty()) {
            act { it.show(HUMAN) }
            return
        }
        val need = (3 - g.players[HUMAN].startTunnelas.size).coerceAtLeast(0)
        val chosen = selection.toList()
        val melds = if (chosen.size == need * 3) Melds.findDisjointPure(chosen, need) else null
        if (melds == null) {
            toast(s.selectionNotPure)
            return
        }
        act { it.show(HUMAN, melds) }
    }

    private fun showDublees() {
        if (selection.isEmpty()) {
            act { it.showDublees(HUMAN) }
            return
        }
        val pairs = Melds.dublees(selection.toList())
        if (selection.size != 14 || pairs.size != 7) {
            toast(s.selectionNotDublees)
            return
        }
        act { it.showDublees(HUMAN, pairs) }
    }

    private fun finish() {
        val g = game ?: return
        if (!g.canWin(HUMAN)) {
            toast(s.cannotFinish)
            return
        }
        val preferred = selection.singleOrNull()
        act { it.declareWin(HUMAN, preferred) }
    }

    private fun throwSelected() {
        val g = game ?: return
        val card = selection.singleOrNull()
        if (card == null) {
            toast(s.selectOneToThrow)
            return
        }
        if (card == g.takenFromDiscard) {
            toast(s.cannotThrowTaken)
            return
        }
        if (g.canDiscard(HUMAN, card)) act { it.discard(HUMAN, card) }
    }

    private fun toast(text: String) {
        val el = document.getElementById("toast") as? HTMLElement ?: return
        el.textContent = text
        el.className = "toast on"
        toastTimer?.let { window.clearTimeout(it) }
        toastTimer = window.setTimeout({ el.className = "toast" }, 2800)
    }

    // ----- Animation -----

    /** Moves a card from one anchor to another, above the page. */
    private fun fly(card: Card?, from: String, to: String) {
        val a = document.querySelector("[data-anchor=\"$from\"]")?.getBoundingClientRect()
        val b = document.querySelector("[data-anchor=\"$to\"]")?.getBoundingClientRect()
        if (a == null || b == null) {
            landed(to)
            return
        }
        val el = document.createElement("div") as HTMLElement
        el.className = "flight"
        el.innerHTML = if (card == null) backHtml() else cardHtml(card)
        val w = 46.0
        val h = w * 1.42
        val x0 = a.left + a.width / 2 - w / 2
        val y0 = a.top + a.height / 2 - h / 2
        val dx = b.left + b.width / 2 - w / 2 - x0
        val dy = b.top + b.height / 2 - h / 2 - y0
        el.style.left = "${x0}px"
        el.style.top = "${y0}px"
        overlay.appendChild(el)
        window.requestAnimationFrame {
            window.requestAnimationFrame {
                el.style.transform = "translate(${dx}px, ${dy}px)"
            }
        }
        window.setTimeout({
            el.remove()
            landed(to)
        }, FLIGHT_MS + 40)
    }

    private fun landed(to: String) {
        if (to == "discard" && pendingToDiscard > 0) {
            pendingToDiscard--
            if (view == View.GAME) render()
        }
    }

    // ----- Rendering -----

    private fun name(i: Int) = if (i == HUMAN) s.you else s.botNames[i - 1]

    private fun render() {
        document.documentElement?.setAttribute("lang", if (language == Language.NE) "ne" else "en")
        root.innerHTML = when (view) {
            View.HOME -> homeHtml()
            View.RULES -> rulesHtml()
            View.GAME -> gameHtml()
        }
    }

    private fun chip(act: String, value: String, label: String, on: Boolean) =
        """<button class="chip${if (on) " on" else ""}" data-act="$act" data-v="$value">${esc(label)}</button>"""

    private fun homeHtml(): String {
        val fan = listOf(Card.of(Suit.HEARTS, 10), Card.of(Suit.HEARTS, 11), Card.of(Suit.HEARTS, 12))
        return """
        <main class="home">
          <div class="fan">${cardHtml(fan[0], classes = "f1")}${cardHtml(fan[2], classes = "f3")}${cardHtml(fan[1], classes = "f2")}</div>
          <h1>${esc(s.appTitle)}</h1>
          <p class="sub">${esc(s.subtitle)}</p>
          <h2>${esc(s.players)}</h2>
          <div class="chips">${(2..5).joinToString("") { chip("players", "$it", "$it", it == playerCount) }}</div>
          <h2>${esc(s.difficulty)}</h2>
          <div class="chips">${chip("level", "EASY", s.easy, level == BotLevel.EASY)}${chip("level", "HARD", s.hard, level == BotLevel.HARD)}</div>
          <button class="primary big" data-act="play">${esc(s.play)}</button>
          <button class="ghost big" data-act="rules">${esc(s.rules)}</button>
          <h2 class="lang">${esc(s.language)}</h2>
          <div class="chips">${chip("lang", "EN", "English", language == Language.EN)}${chip("lang", "NE", "नेपाली", language == Language.NE)}</div>
        </main>"""
    }

    private fun rulesHtml(): String = """
        <main class="rules">
          <div class="bar"><button class="link" data-act="home">‹ ${esc(s.back)}</button><h1>${esc(s.rules)}</h1></div>
          ${s.rulesSections.joinToString("") { (t, b) -> "<section><h2>${esc(t)}</h2><p>${esc(b).replace("\n", "<br>")}</p></section>" }}
          <button class="ghost big" data-act="home">‹ ${esc(s.back)}</button>
        </main>"""

    private fun gameHtml(): String {
        val g = game ?: return homeHtml()
        val ctx = g.contextFor(HUMAN)
        val human = g.players[HUMAN]
        val turn = humanTurn
        val playing = turn && g.phase == Phase.PLAY
        val drawing = turn && g.phase == Phase.DRAW
        val canShow = playing && g.canShow(HUMAN)
        val canDublee = playing && g.canShowDublees(HUMAN)
        val canWin = playing && g.canWin(HUMAN)
        val exposable = g.phase != Phase.ROUND_OVER && g.exposableTunnelas(HUMAN).isNotEmpty()

        val opponents = (1 until g.playerCount).joinToString("") { i ->
            val p = g.players[i]
            val active = g.current == i && g.phase != Phase.ROUND_OVER
            """<button class="opp${if (active) " turn" else ""}" data-act="inspect" data-v="$i" data-anchor="p$i">
                 <b>${esc(name(i))}</b>
                 <span class="cnt"><i class="mini"></i>${p.hand.size}</span>
                 <span class="${if (p.hasSeen) "seen" else "unseen"}">${if (p.hasSeen) "✓ " + esc(s.seen) else esc(s.notSeen)}</span>
                 <span class="score">${totals.getOrElse(i) { 0 }}</span>
               </button>"""
        }

        val pile = g.discardPile
        val top = pile.getOrNull(pile.size - 1 - pendingToDiscard)
        val discardHtml = if (top != null) cardHtml(top, ctx.kind(top), "table-card", "discard") else """<div class="card empty table-card"></div>"""
        val tiplu = g.tiplu
        val jokerHtml = when {
            tiplu == null -> """<div class="card empty table-card"></div>"""
            human.hasSeen -> cardHtml(tiplu, ctx.kind(tiplu), "table-card")
            else -> backHtml("table-card", "?")
        }

        val events = g.log.filter { it !is GameEvent.DrewStock || it.player != HUMAN }.takeLast(3)
        val log = events.mapIndexed { k, e ->
            """<div class="${if (k == events.lastIndex) "now" else ""}">${esc(eventText(e))}</div>"""
        }.joinToString("").ifEmpty { "<div>&nbsp;</div>" }

        val status = when {
            g.phase == Phase.ROUND_OVER -> s.handOver
            drawing -> s.yourTurnDraw
            playing && (canShow || canDublee) -> s.showTip
            playing -> if (selection.isEmpty()) s.yourTurnPlay else ""
            else -> s.waitingFor(name(g.current))
        }

        val laid = laidCards(human)
        val laidHtml = if (laid.isEmpty()) "" else
            """<div class="laid">${laid.joinToString("") { grp -> "<div class=\"grp\">" + grp.joinToString("") { cardHtml(it, ctx.kind(it)) } + "</div>" }}</div>"""

        val drawn = if (playing) g.drawnCard else null
        val hand = handGroups(g).flatMap { it.chunked(8) }.joinToString("") { grp ->
            "<div class=\"grp\">" + grp.joinToString("") { c ->
                val cls = buildString {
                    if (c in selection) append(" sel")
                    if (c == drawn) append(" drawn")
                }
                cardHtml(c, ctx.kind(c), cls, "card")
            } + "</div>"
        }

        val sortLabel = when (sort) {
            Sort.SETS -> s.sortSets
            Sort.SUIT -> s.sortSuit
            Sort.RANK -> s.sortRank
        }
        val actions = buildString {
            append("""<button class="ghost" data-act="sort">⇅ ${esc(sortLabel)}</button>""")
            if (selection.size > 1) append("""<button class="ghost" data-act="clear">${esc(s.clear)} (${selection.size})</button>""")
            if (exposable) append("""<button class="primary" data-act="expose">${esc(s.exposeTunnela)}</button>""")
            if (canShow) append("""<button class="primary" data-act="show">${esc(s.showSets)}</button>""")
            if (canDublee) append("""<button class="primary" data-act="dublee">${esc(s.showDublees)}</button>""")
            if (canWin) append("""<button class="win" data-act="finish">${esc(s.finish)}</button>""")
            if (playing) append("""<button class="primary" data-act="throw"${if (selection.size == 1) "" else " disabled"}>${esc(s.throwCard)}</button>""")
        }

        return """
        <main class="game">
          <header><button class="link" data-act="quit">‹ ${esc(s.home)}</button><b>${esc(s.handNumber(handNumber))}</b><span>${esc(s.total)}: ${totals.getOrElse(HUMAN) { 0 }}</span></header>
          <div class="opps">$opponents</div>
          <div class="tbl">
            <div class="slot${if (drawing) " glow" else ""}"><div data-anchor="deck">${backHtml("table-card", act = "stock")}</div><small>${esc(s.deck)} (${g.stockSize})</small></div>
            <div class="slot${if (drawing && g.canDrawDiscard(HUMAN)) " glow" else ""}"><div data-anchor="discard">$discardHtml</div><small>${esc(s.discard)}</small></div>
            <div class="slot"><div>$jokerHtml</div><small>${esc(s.joker)}</small></div>
          </div>
          <div class="log">$log</div>
          <div class="grow"></div>
          ${if (status.isNotEmpty()) "<p class=\"status${if (turn) " mine" else ""}\">${esc(status)}</p>" else ""}
          $laidHtml
          <div class="hand" data-anchor="hand">$hand</div>
          <nav class="actions">$actions</nav>
        </main>
        ${if (confirmQuit) quitHtml() else ""}
        ${inspect?.let { inspectHtml(g, it, ctx) } ?: ""}
        ${if (showResult) resultHtml(g) else ""}"""
    }

    private fun handGroups(g: MarriageGame): List<List<Card>> {
        val hand = g.players[HUMAN].hand
        val ctx = g.contextFor(HUMAN)
        val suitOrder = listOf(Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS)
        fun rankValue(c: Card) = if (c.rank == 1) 14 else c.rank
        return when (sort) {
            Sort.SETS -> {
                val a = Arrange.arrange(hand, ctx)
                a.sets.map { displayOrder(it.cards) } + a.partials + listOf(a.loose).filter { it.isNotEmpty() }
            }
            Sort.SUIT -> {
                val wild = hand.filter { ctx.isWild(it) }
                suitOrder.map { suit -> hand.filter { it.suit == suit && !ctx.isWild(it) }.sortedBy(::rankValue) }
                    .filter { it.isNotEmpty() } + listOf(wild).filter { it.isNotEmpty() }
            }
            Sort.RANK -> listOf(
                hand.sortedWith(compareBy({ if (ctx.isWild(it)) 1 else 0 }, { rankValue(it) }, { suitOrder.indexOf(it.suit) })),
            )
        }
    }

    private fun eventText(e: GameEvent): String {
        val n = name(e.player)
        return when (e) {
            is GameEvent.DrewStock -> s.drewStock(n)
            is GameEvent.TookDiscard -> s.tookDiscard(n, e.card.toString())
            is GameEvent.Discarded -> s.threw(n, e.card.toString())
            is GameEvent.ExposedTunnela -> s.exposed(n, e.meld.cards[0].toString())
            is GameEvent.ShowedMelds -> s.showedSets(n)
            is GameEvent.ShowedDublees -> s.showedDublees(n)
            is GameEvent.Won -> s.won(n)
            is GameEvent.StockReshuffled -> s.reshuffled
            is GameEvent.NoWinner -> s.noWinner
        }
    }

    private fun quitHtml() = """
        <div class="modal"><div class="box">
          <p>${esc(s.quitConfirm)}</p>
          <div class="row"><button class="ghost" data-act="quit-no">${esc(s.no)}</button><button class="primary" data-act="quit-yes">${esc(s.yes)}</button></div>
        </div></div>"""

    private fun inspectHtml(g: MarriageGame, i: Int, ctx: JokerContext): String {
        val groups = laidCards(g.players[i])
        val body = if (groups.isEmpty()) "<p>${esc(s.nothingLaid)}</p>" else
            "<p>${esc(s.laidDown)}</p><div class=\"sets\">" +
                groups.joinToString("") { grp -> "<div class=\"grp\">" + grp.joinToString("") { cardHtml(it, ctx.kind(it)) } + "</div>" } + "</div>"
        return """
        <div class="modal"><div class="box">
          <h2>${esc(name(i))}</h2>$body
          <div class="row"><button class="primary" data-act="close">${esc(s.close)}</button></div>
        </div></div>"""
    }

    private fun resultHtml(g: MarriageGame): String {
        val r = g.result ?: return ""
        val ctx = JokerContext(r.tiplu?.face)
        val w = r.winner
        val title = if (w == null) s.handOver else s.winnerIs(name(w)) + if (r.byDublees) " (${s.byDublees})" else ""
        val rows = (0 until g.playerCount).joinToString("") { i ->
            val net = r.net[i]
            val items = r.breakdown[i].joinToString(" · ") {
                s.pointLabel(it.label) + (if (it.count > 1) " ×${it.count}" else "") + " " + it.points
            }
            """<tr class="${if (i == w) "won" else ""}">
                 <td>${esc(name(i))}${if (r.seen[i]) "" else " ✗"}${if (items.isNotEmpty()) "<small>${esc(items)}</small>" else ""}</td>
                 <td>${r.points[i]}</td>
                 <td class="${if (net >= 0) "plus" else "minus"}">${if (net > 0) "+$net" else "$net"}</td>
                 <td>${totals.getOrElse(i) { 0 }}</td>
               </tr>"""
        }
        val winning = if (w == null) "" else {
            val p = g.players[w]
            val groups = laidCards(p) + r.winningMelds.map { displayOrder(it.cards) } + r.winningDublees.map { it.cards }
            "<h3>${esc(s.winningHand)}</h3><div class=\"sets\">" +
                groups.joinToString("") { grp -> "<div class=\"grp\">" + grp.joinToString("") { cardHtml(it, ctx.kind(it)) } + "</div>" } + "</div>"
        }
        return """
        <div class="modal"><div class="box result">
          <h2>${esc(title)}</h2>
          ${if (w == null) "<p>${esc(s.noWinner)}</p>" else ""}
          ${r.tiplu?.let { "<div class=\"tiplu\">${esc(s.tiplu)}: ${cardHtml(it, ctx.kind(it))}</div>" } ?: ""}
          <table><thead><tr><th></th><th>${esc(s.points)}</th><th>${esc(s.thisHand)}</th><th>${esc(s.total)}</th></tr></thead><tbody>$rows</tbody></table>
          $winning
          <div class="row"><button class="ghost" data-act="quit-yes">${esc(s.home)}</button><button class="primary" data-act="next">${esc(s.nextHand)}</button></div>
        </div></div>"""
    }
}

fun main() {
    val root = document.getElementById("app") as HTMLElement
    val overlay = document.getElementById("flights") as HTMLElement
    App(root, overlay)
    // Keep the English object referenced so the default language is always available.
    English.appTitle
}
