package com.astha.marriage.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.DialogProperties
import com.astha.marriage.GameViewModel
import com.astha.marriage.Strings
import com.astha.marriage.engine.JokerContext
import com.astha.marriage.engine.MarriageGame

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ResultDialog(vm: GameViewModel, game: MarriageGame, s: Strings) {
    val r = game.result ?: return
    val ctx = JokerContext(r.tiplu?.face)
    AlertDialog(
        onDismissRequest = {},
        properties = DialogProperties(dismissOnBackPress = false, dismissOnClickOutside = false),
        title = {
            val w = r.winner
            Text(
                if (w == null) s.handOver else s.winnerIs(vm.playerName(w, s)) + if (r.byDublees) " (${s.byDublees})" else "",
                fontWeight = FontWeight.Bold,
            )
        },
        text = {
            Column(Modifier.verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                if (r.winner == null) Text(s.noWinner)
                r.tiplu?.let { t ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("${s.tiplu}: ", fontWeight = FontWeight.SemiBold)
                        PlayingCard(t, width = 34.dp, maal = ctx.kind(t))
                    }
                }
                // Score table
                Row(Modifier.fillMaxWidth()) {
                    Text("", Modifier.weight(1.4f))
                    Text(s.points, Modifier.weight(1f), textAlign = TextAlign.End, fontSize = 13.sp)
                    Text(s.thisHand, Modifier.weight(1.2f), textAlign = TextAlign.End, fontSize = 13.sp)
                    Text(s.total, Modifier.weight(1f), textAlign = TextAlign.End, fontSize = 13.sp)
                }
                HorizontalDivider()
                for (i in 0 until game.playerCount) {
                    Column {
                        Row(Modifier.fillMaxWidth()) {
                            Text(
                                vm.playerName(i, s) + if (r.seen[i]) "" else " ✗",
                                Modifier.weight(1.4f),
                                fontWeight = if (i == r.winner) FontWeight.Bold else FontWeight.Normal,
                            )
                            Text("${r.points[i]}", Modifier.weight(1f), textAlign = TextAlign.End)
                            val net = r.net[i]
                            Text(
                                if (net > 0) "+$net" else "$net",
                                Modifier.weight(1.2f),
                                textAlign = TextAlign.End,
                                color = if (net >= 0) Color(0xFF81C784) else Color(0xFFE57373),
                                fontWeight = FontWeight.Bold,
                            )
                            Text("${vm.totals.getOrElse(i) { 0 }}", Modifier.weight(1f), textAlign = TextAlign.End)
                        }
                        val items = r.breakdown[i]
                        if (items.isNotEmpty()) {
                            Text(
                                items.joinToString(" · ") { "${s.pointLabel(it.label)}${if (it.count > 1) " ×${it.count}" else ""} ${it.points}" },
                                fontSize = 12.sp,
                                color = Color(0xFFB7CCBF),
                            )
                        }
                    }
                }
                val groups = r.winningMelds.map { it.cards } + r.winningDublees.map { it.cards }
                val w = r.winner
                if (w != null) {
                    HorizontalDivider()
                    Text(s.winningHand, fontWeight = FontWeight.SemiBold)
                    val p = game.players[w]
                    val laid = p.startTunnelas.map { it.cards } + p.shownMelds.map { it.cards } + p.shownDublees.map { it.cards }
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        for (g in laid + groups) Row(horizontalArrangement = Arrangement.spacedBy((-10).dp)) {
                            for (c in g) PlayingCard(c, width = 30.dp, maal = ctx.kind(c))
                        }
                    }
                }
            }
        },
        confirmButton = { Button(onClick = { vm.nextHand() }) { Text(s.nextHand) } },
        dismissButton = { TextButton(onClick = { vm.leaveGame() }) { Text(s.home) } },
        modifier = Modifier.padding(4.dp),
    )
}
