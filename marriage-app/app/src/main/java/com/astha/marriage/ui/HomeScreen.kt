package com.astha.marriage.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.astha.marriage.GameViewModel
import com.astha.marriage.Language
import com.astha.marriage.LocalStrings
import com.astha.marriage.Screen
import com.astha.marriage.engine.Card
import com.astha.marriage.engine.Suit

@Composable
fun HomeScreen(vm: GameViewModel) {
    val s = LocalStrings.current
    Box(
        Modifier
            .fillMaxSize()
            .background(Brush.radialGradient(listOf(TableColors.feltLight, TableColors.feltDark), radius = 1400f))
            .safeDrawingPadding(),
    ) {
        Column(
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(Modifier.height(32.dp))
            // A fan of the three cards of a marriage.
            Box(Modifier.height(130.dp).width(200.dp), contentAlignment = Alignment.Center) {
                PlayingCard(Card.of(Suit.HEARTS, 10), width = 66.dp, modifier = Modifier.offset(x = (-46).dp, y = 10.dp).rotate(-14f))
                PlayingCard(Card.of(Suit.HEARTS, 12), width = 66.dp, modifier = Modifier.offset(x = 46.dp, y = 10.dp).rotate(14f))
                PlayingCard(Card.of(Suit.HEARTS, 11), width = 66.dp)
            }
            Spacer(Modifier.height(20.dp))
            Text(s.appTitle, fontSize = 44.sp, fontWeight = FontWeight.Bold, color = TableColors.gold)
            Text(s.subtitle, fontSize = 16.sp, color = Color(0xFFD5E6DB))
            Spacer(Modifier.height(40.dp))

            Text(s.players, color = Color.White, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                for (n in 2..5) {
                    FilterChip(
                        selected = vm.playerCount == n,
                        onClick = { vm.updatePlayerCount(n) },
                        label = { Text("$n", fontSize = 18.sp, modifier = Modifier.padding(horizontal = 6.dp)) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = TableColors.gold,
                            selectedLabelColor = Color(0xFF2A1E00),
                            labelColor = Color.White,
                        ),
                    )
                }
            }
            Spacer(Modifier.height(28.dp))
            Button(
                onClick = { vm.startMatch() },
                modifier = Modifier.fillMaxWidth(0.7f).height(56.dp),
                shape = RoundedCornerShape(16.dp),
            ) {
                Text(s.play, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(12.dp))
            OutlinedButton(
                onClick = { vm.screen = Screen.RULES },
                modifier = Modifier.fillMaxWidth(0.7f).height(48.dp),
                shape = RoundedCornerShape(16.dp),
            ) {
                Text(s.rules, fontSize = 18.sp, color = Color.White)
            }
            Spacer(Modifier.height(36.dp))
            Text(s.language, color = Color(0xFFD5E6DB), fontSize = 14.sp)
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.padding(top = 6.dp)) {
                LanguageChip("English", vm.language == Language.EN) { vm.updateLanguage(Language.EN) }
                LanguageChip("नेपाली", vm.language == Language.NE) { vm.updateLanguage(Language.NE) }
            }
        }
    }
}

@Composable
fun LanguageChip(label: String, selected: Boolean, onClick: () -> Unit) {
    FilterChip(
        selected = selected,
        onClick = onClick,
        label = { Text(label) },
        colors = FilterChipDefaults.filterChipColors(
            selectedContainerColor = Color(0xFF9FD8B4),
            selectedLabelColor = Color(0xFF0B2B1A),
            labelColor = Color.White,
        ),
    )
}

@Composable
fun RulesScreen(vm: GameViewModel) {
    val s = LocalStrings.current
    Column(
        Modifier
            .fillMaxSize()
            .background(TableColors.feltDark)
            .safeDrawingPadding(),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(8.dp)) {
            TextButton(onClick = { vm.screen = Screen.HOME }) { Text("‹ ${s.back}", color = Color.White, fontSize = 16.sp) }
            Text(s.rules, fontSize = 22.sp, fontWeight = FontWeight.Bold, color = TableColors.gold)
        }
        Column(
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 8.dp),
        ) {
            for ((title, body) in s.rulesSections) {
                Text(title, color = TableColors.gold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Spacer(Modifier.height(4.dp))
                Text(body, color = Color(0xFFEFF5F1), fontSize = 15.sp, lineHeight = 22.sp)
                Spacer(Modifier.height(18.dp))
            }
            Text(
                "♠ ♥ ♣ ♦",
                color = Color(0x88FFFFFF),
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
                style = MaterialTheme.typography.titleMedium,
            )
            Spacer(Modifier.size(8.dp))
        }
    }
}
