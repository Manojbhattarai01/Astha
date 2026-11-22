package com.astha.marriage.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.astha.marriage.engine.Card
import com.astha.marriage.engine.MaalKind
import com.astha.marriage.engine.Ranks

object TableColors {
    val felt = Color(0xFF0E5A36)
    val feltDark = Color(0xFF093D25)
    val feltLight = Color(0xFF17754A)
    val gold = Color(0xFFF2C14E)
    val cardFace = Color(0xFFFFFDF7)
    val red = Color(0xFFC62828)
    val black = Color(0xFF1B1B1B)
    val back1 = Color(0xFF8E1B2B)
    val back2 = Color(0xFF5E0F1C)
    val selected = Color(0xFF42A5F5)
}

@Composable
fun MarriageTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = TableColors.gold,
            onPrimary = Color(0xFF2A1E00),
            secondary = Color(0xFF9FD8B4),
            surface = Color(0xFF12301F),
            onSurface = Color(0xFFF1F5F2),
            background = TableColors.felt,
            onBackground = Color(0xFFF1F5F2),
            surfaceVariant = Color(0xFF1C4A31),
            onSurfaceVariant = Color(0xFFD5E6DB),
        ),
        content = content,
    )
}

/** Short tag drawn on known maal cards. */
fun maalTag(kind: MaalKind): String? = when (kind) {
    MaalKind.TIPLU -> "T"
    MaalKind.POPLU -> "P"
    MaalKind.JHIPLU -> "Jh"
    MaalKind.ALTER -> "A"
    MaalKind.ORDINARY_JOKER -> "★"
    MaalKind.NONE -> null
}

@Composable
fun PlayingCard(
    card: Card,
    modifier: Modifier = Modifier,
    width: Dp = 44.dp,
    selected: Boolean = false,
    highlight: Boolean = false,
    maal: MaalKind = MaalKind.NONE,
    onClick: (() -> Unit)? = null,
) {
    val height = width * 1.42f
    val color = if (card.suit.isRed) TableColors.red else TableColors.black
    val shape = RoundedCornerShape(width * 0.12f)
    val borderColor = when {
        selected -> TableColors.selected
        maal != MaalKind.NONE -> TableColors.gold
        highlight -> Color(0xFF66BB6A)
        else -> Color(0xFF9E9E9E)
    }
    val borderWidth = if (selected || maal != MaalKind.NONE || highlight) 2.5.dp else 1.dp
    Box(
        modifier
            .size(width, height)
            .clip(shape)
            .background(TableColors.cardFace)
            .border(borderWidth, borderColor, shape)
            .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier),
    ) {
        val unit = width.value
        Column(Modifier.padding(start = (unit * 0.08f).dp, top = (unit * 0.04f).dp)) {
            Text(
                Ranks.label(card.rank),
                color = color,
                fontWeight = FontWeight.Bold,
                fontSize = (unit * 0.36f).sp,
                lineHeight = (unit * 0.38f).sp,
            )
            Text(card.suit.symbol, color = color, fontSize = (unit * 0.3f).sp, lineHeight = (unit * 0.3f).sp)
        }
        Text(
            card.suit.symbol,
            color = color,
            fontSize = (unit * 0.55f).sp,
            modifier = Modifier.align(Alignment.BottomEnd).padding(end = (unit * 0.08f).dp, bottom = (unit * 0.02f).dp),
        )
        val tag = maalTag(maal)
        if (tag != null) {
            Box(
                Modifier
                    .align(Alignment.TopEnd)
                    .padding((unit * 0.05f).dp)
                    .clip(RoundedCornerShape(50))
                    .background(TableColors.gold)
                    .padding(horizontal = (unit * 0.06f).dp),
            ) {
                Text(tag, color = Color(0xFF3A2A00), fontSize = (unit * 0.22f).sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
fun CardBack(
    modifier: Modifier = Modifier,
    width: Dp = 44.dp,
    label: String? = null,
    onClick: (() -> Unit)? = null,
) {
    val height = width * 1.42f
    val shape = RoundedCornerShape(width * 0.12f)
    Box(
        modifier
            .size(width, height)
            .clip(shape)
            .background(Brush.linearGradient(listOf(TableColors.back1, TableColors.back2)))
            .border(2.dp, Color(0xFFF5E6C8), shape)
            .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            Modifier
                .padding(width * 0.12f)
                .border(1.dp, Color(0x88F5E6C8), RoundedCornerShape(width * 0.08f))
                .size(width * 0.7f, height * 0.75f),
        )
        if (label != null) {
            Text(label, color = Color.White, fontWeight = FontWeight.Bold, fontSize = (width.value * 0.3f).sp)
        }
    }
}

/** An empty slot where a card would be. */
@Composable
fun EmptySlot(modifier: Modifier = Modifier, width: Dp = 44.dp, onClick: (() -> Unit)? = null) {
    val shape = RoundedCornerShape(width * 0.12f)
    Box(
        modifier
            .size(width, width * 1.42f)
            .clip(shape)
            .border(1.5.dp, Color(0x66FFFFFF), shape)
            .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier),
    )
}
