package com.astha.marriage.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.astha.marriage.GameViewModel
import com.astha.marriage.GameViewModel.Companion.HUMAN
import com.astha.marriage.LocalStrings
import com.astha.marriage.Notice
import com.astha.marriage.SortMode
import com.astha.marriage.Strings
import com.astha.marriage.engine.Card
import com.astha.marriage.engine.GameEvent
import com.astha.marriage.engine.JokerContext
import com.astha.marriage.engine.MarriageGame
import com.astha.marriage.engine.Phase
import com.astha.marriage.engine.PlayerState

@Composable
fun GameScreen(vm: GameViewModel) {
    val s = LocalStrings.current
    val game = vm.game ?: return
    // Reading the version makes this screen redraw after every move.
    val version = vm.version
    var confirmQuit by remember { mutableStateOf(false) }
    var inspect by remember { mutableStateOf<Int?>(null) }
    val snackbar = remember { SnackbarHostState() }

    BackHandler { confirmQuit = true }

    val notice = vm.notice
    LaunchedEffect(notice) {
        if (notice != null) {
            snackbar.showSnackbar(noticeText(notice, s))
            vm.clearNotice()
        }
    }

    val human = game.players[HUMAN]
    val ctx = game.contextFor(HUMAN)
    val humanTurn = vm.isHumanTurn
    // Expensive checks, recomputed only after a move.
    val canShow = remember(version) { humanTurn && game.phase == Phase.PLAY && game.canShow(HUMAN) }
    val canShowDublees = remember(version) { humanTurn && game.canShowDublees(HUMAN) }
    val canWin = remember(version) { humanTurn && game.canWin(HUMAN) }
    val exposable = remember(version) { game.exposableTunnelas(HUMAN).isNotEmpty() }

    // The engine is plain mutable state, so rebuild the table after every move.
    key(version) {
    BoxWithConstraints(
        Modifier
            .fillMaxSize()
            .background(TableColors.felt)
            .safeDrawingPadding(),
    ) {
        val handCardWidth: Dp = ((maxWidth - 16.dp) / 8 - 4.dp).coerceIn(34.dp, 56.dp)
        Column(Modifier.fillMaxSize()) {
            // Top bar
            Row(
                Modifier.fillMaxWidth().background(TableColors.feltDark).padding(horizontal = 4.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                TextButton(onClick = { confirmQuit = true }) { Text("‹ ${s.home}", color = Color.White) }
                Spacer(Modifier.weight(1f))
                Text(s.handNumber(vm.handNumber), color = TableColors.gold, fontWeight = FontWeight.Bold)
                Spacer(Modifier.weight(1f))
                Text(
                    "${s.total}: ${vm.totals.getOrElse(HUMAN) { 0 }}",
                    color = Color.White,
                    modifier = Modifier.padding(end = 12.dp),
                )
            }

            // Opponents
            Row(
                Modifier.fillMaxWidth().padding(6.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                for (i in 1 until game.playerCount) {
                    OpponentChip(
                        name = vm.playerName(i, s),
                        player = game.players[i],
                        isTurn = game.current == i && game.phase != Phase.ROUND_OVER,
                        total = vm.totals.getOrElse(i) { 0 },
                        s = s,
                        modifier = Modifier.weight(1f),
                        onClick = { inspect = i },
                    )
                }
            }

            // Table: deck, discard, joker
            Row(
                Modifier.fillMaxWidth().padding(top = 8.dp),
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.Top,
            ) {
                val drawing = humanTurn && game.phase == Phase.DRAW
                TableSlot(s.deck + " (${game.stockSize})", glow = drawing) {
                    CardBack(width = 62.dp, onClick = { vm.tapStock() })
                }
                TableSlot(s.discard, glow = drawing && game.canDrawDiscard(HUMAN)) {
                    val top = game.topDiscard
                    if (top != null) {
                        PlayingCard(top, width = 62.dp, maal = ctx.kind(top), onClick = { vm.tapDiscard() })
                    } else {
                        EmptySlot(width = 62.dp)
                    }
                }
                TableSlot(s.joker) {
                    val t = game.tiplu
                    when {
                        t == null -> EmptySlot(width = 62.dp)
                        vm.humanSeen -> PlayingCard(t, width = 62.dp, maal = ctx.kind(t))
                        else -> CardBack(width = 62.dp, label = "?")
                    }
                }
            }

            // Recent moves
            Column(
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 6.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(Color(0x33000000))
                    .padding(horizontal = 10.dp, vertical = 6.dp),
            ) {
                val events = vm.recentEvents(3)
                for ((k, e) in events.withIndex()) {
                    Text(
                        eventText(e, vm, s),
                        color = if (k == events.lastIndex) Color.White else Color(0xAAFFFFFF),
                        fontSize = 13.sp,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
                if (events.isEmpty()) Text(" ", fontSize = 13.sp)
            }

            Spacer(Modifier.weight(1f))

            // Status line
            val status = when {
                game.phase == Phase.ROUND_OVER -> s.handOver
                humanTurn && game.phase == Phase.DRAW -> s.yourTurnDraw
                humanTurn -> if (vm.selected == null) s.yourTurnPlay else ""
                else -> s.waitingFor(vm.playerName(game.current, s))
            }
            if (status.isNotEmpty()) {
                Text(
                    status,
                    color = if (humanTurn) TableColors.gold else Color(0xFFD5E6DB),
                    fontWeight = if (humanTurn) FontWeight.SemiBold else FontWeight.Normal,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 4.dp),
                )
            }

            // My cards on the table
            val laid = laidCards(human)
            if (laid.isNotEmpty()) {
                Row(
                    Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    for (group in laid) {
                        Row(horizontalArrangement = Arrangement.spacedBy((-12).dp)) {
                            for (c in group) PlayingCard(c, width = 30.dp, maal = ctx.kind(c))
                        }
                    }
                }
            }

            // Hand
            HandView(
                cards = vm.humanHand(),
                ctx = ctx,
                selected = vm.selected,
                drawn = if (humanTurn && game.phase == Phase.PLAY) game.drawnCard else null,
                cardWidth = handCardWidth,
                onTap = { vm.tapCard(it) },
            )

            // Actions
            ActionBar(
                vm = vm,
                game = game,
                s = s,
                canShow = canShow,
                canShowDublees = canShowDublees,
                canWin = canWin,
                exposable = exposable && game.phase != Phase.ROUND_OVER,
            )
        }
        SnackbarHost(snackbar, Modifier.align(Alignment.BottomCenter).padding(bottom = 80.dp))
    }
    }

    if (confirmQuit) {
        AlertDialog(
            onDismissRequest = { confirmQuit = false },
            text = { Text(s.quitConfirm) },
            confirmButton = { TextButton(onClick = { confirmQuit = false; vm.leaveGame() }) { Text(s.yes) } },
            dismissButton = { TextButton(onClick = { confirmQuit = false }) { Text(s.no) } },
        )
    }

    inspect?.let { i ->
        AlertDialog(
            onDismissRequest = { inspect = null },
            title = { Text(vm.playerName(i, s)) },
            text = {
                val groups = laidCards(game.players[i])
                if (groups.isEmpty()) {
                    Text(s.nothingLaid)
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(s.laidDown)
                        @OptIn(ExperimentalLayoutApi::class)
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            for (g in groups) Row(horizontalArrangement = Arrangement.spacedBy((-10).dp)) {
                                for (c in g) PlayingCard(c, width = 34.dp, maal = ctx.kind(c))
                            }
                        }
                    }
                }
            },
            confirmButton = { TextButton(onClick = { inspect = null }) { Text(s.close) } },
        )
    }

    if (vm.showResult) {
        ResultDialog(vm, game, s)
    }
}

private fun laidCards(p: PlayerState): List<List<Card>> =
    p.startTunnelas.map { it.cards } + p.shownMelds.map { it.cards } + p.shownDublees.map { it.cards }

fun noticeText(n: Notice, s: Strings): String = when (n) {
    Notice.CANNOT_TAKE_JOKER -> s.cannotTakeJoker
    Notice.DUBLEE_ONLY_TO_WIN -> s.dubleeOnlyToWin
    Notice.CANNOT_THROW_TAKEN -> s.cannotThrowTaken
    Notice.CANNOT_FINISH -> s.cannotFinish
    Notice.NEED_THREE_PURE -> s.needThreePure
}

fun eventText(e: GameEvent, vm: GameViewModel, s: Strings): String {
    val name = vm.playerName(e.player, s)
    return when (e) {
        is GameEvent.DrewStock -> s.drewStock(name)
        is GameEvent.TookDiscard -> s.tookDiscard(name, e.card.toString())
        is GameEvent.Discarded -> s.threw(name, e.card.toString())
        is GameEvent.ExposedTunnela -> s.exposed(name, e.meld.cards[0].toString())
        is GameEvent.ShowedMelds -> s.showedSets(name)
        is GameEvent.ShowedDublees -> s.showedDublees(name)
        is GameEvent.Won -> s.won(name)
        is GameEvent.StockReshuffled -> s.reshuffled
        is GameEvent.NoWinner -> s.noWinner
    }
}

@Composable
private fun TableSlot(label: String, glow: Boolean = false, content: @Composable () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Column(
            Modifier
                .clip(RoundedCornerShape(10.dp))
                .border(2.dp, if (glow) TableColors.gold else Color.Transparent, RoundedCornerShape(10.dp))
                .padding(4.dp),
        ) { content() }
        Text(label, color = Color(0xFFD5E6DB), fontSize = 12.sp, modifier = Modifier.padding(top = 2.dp))
    }
}

@Composable
private fun OpponentChip(
    name: String,
    player: PlayerState,
    isTurn: Boolean,
    total: Int,
    s: Strings,
    modifier: Modifier,
    onClick: () -> Unit,
) {
    val shape = RoundedCornerShape(12.dp)
    Column(
        modifier
            .clip(shape)
            .background(if (isTurn) Color(0x55F2C14E) else Color(0x33000000))
            .border(if (isTurn) 2.dp else 0.dp, if (isTurn) TableColors.gold else Color.Transparent, shape)
            .clickable(onClick = onClick)
            .padding(6.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(name, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp, maxLines = 1)
        Row(verticalAlignment = Alignment.CenterVertically) {
            CardBack(width = 14.dp)
            Text(" ${player.hand.size}", color = Color.White, fontSize = 12.sp)
        }
        Text(
            if (player.hasSeen) "✓ ${s.seen}" else s.notSeen,
            color = if (player.hasSeen) Color(0xFF9FE6B4) else Color(0xAAFFFFFF),
            fontSize = 11.sp,
            maxLines = 1,
        )
        Text("$total", color = TableColors.gold, fontSize = 12.sp)
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun HandView(
    cards: List<Card>,
    ctx: JokerContext,
    selected: Card?,
    drawn: Card?,
    cardWidth: Dp,
    onTap: (Card) -> Unit,
) {
    FlowRow(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp)
            .verticalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(4.dp, Alignment.CenterHorizontally),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        for (c in cards) {
            PlayingCard(
                card = c,
                width = cardWidth,
                selected = c == selected,
                highlight = c == drawn,
                maal = ctx.kind(c),
                modifier = Modifier.offset(y = if (c == selected) (-6).dp else 0.dp),
                onClick = { onTap(c) },
            )
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun ActionBar(
    vm: GameViewModel,
    game: MarriageGame,
    s: Strings,
    canShow: Boolean,
    canShowDublees: Boolean,
    canWin: Boolean,
    exposable: Boolean,
) {
    val humanTurn = vm.isHumanTurn
    val playing = humanTurn && game.phase == Phase.PLAY
    FlowRow(
        Modifier
            .fillMaxWidth()
            .background(TableColors.feltDark)
            .padding(horizontal = 8.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp, Alignment.CenterHorizontally),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        OutlinedButton(
            onClick = { vm.sortMode = if (vm.sortMode == SortMode.SUIT) SortMode.RANK else SortMode.SUIT },
            contentPadding = ButtonDefaults.TextButtonContentPadding,
        ) {
            Text(if (vm.sortMode == SortMode.SUIT) s.sortRank else s.sortSuit, color = Color.White, fontSize = 13.sp)
        }
        if (exposable) {
            Button(onClick = { vm.exposeTunnelas() }) { Text(s.exposeTunnela) }
        }
        if (playing && canShow) {
            Button(onClick = { vm.showSets() }) { Text(s.showSets) }
        }
        if (playing && canShowDublees) {
            Button(onClick = { vm.showDublees() }) { Text(s.showDublees) }
        }
        if (playing && canWin) {
            Button(
                onClick = { vm.finish() },
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF43A047), contentColor = Color.White),
            ) { Text(s.finish, fontWeight = FontWeight.Bold) }
        }
        if (playing) {
            Button(
                onClick = { vm.throwSelected() },
                enabled = vm.selected != null,
                modifier = Modifier.width(110.dp),
            ) { Text(s.throwCard) }
        }
        if (!humanTurn) Spacer(Modifier.height(40.dp))
    }
}
