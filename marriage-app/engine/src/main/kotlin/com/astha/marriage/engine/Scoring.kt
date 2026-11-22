package com.astha.marriage.engine

/** One line of a player's maal points, for showing the breakdown. */
data class PointItem(val label: PointLabel, val count: Int, val points: Int)

enum class PointLabel {
    MARRIAGE, TIPLU, POPLU, JHIPLU, ALTER,
    TUNNELA_ORDINARY, TUNNELA_JOKER, TUNNELA_POPLU, TUNNELA_JHIPLU, TUNNELA_ALTER,
}

object Scoring {
    /** Points for 0, 1, 2 or 3 held cards of each kind. */
    private val POPLU_JHIPLU = intArrayOf(0, 2, 5, 10)
    private val TIPLU = intArrayOf(0, 3, 7, 10)
    private val ALTER = intArrayOf(0, 5, 15, 35)
    private val MARRIAGE = intArrayOf(0, 10, 30, 30)

    const val SEEN_PAYMENT = 3
    const val UNSEEN_PAYMENT = 10
    const val DUBLEE_BONUS = 5

    /**
     * Maal points for a player who has seen the tiplu.
     * [cards] are all the cards the player holds at the end (in hand and laid down),
     * [startTunnelas] are the tunnelas they exposed right after the deal.
     */
    fun points(cards: List<Card>, startTunnelas: List<Meld>, tiplu: Face): List<PointItem> {
        val ctx = JokerContext(tiplu)
        val items = ArrayList<PointItem>()
        val inTunnela = startTunnelas.flatMap { it.cards }.toSet()
        for (t in startTunnelas) {
            val (label, pts) = when (ctx.kind(t.cards[0])) {
                MaalKind.POPLU -> PointLabel.TUNNELA_POPLU to 20
                MaalKind.JHIPLU -> PointLabel.TUNNELA_JHIPLU to 20
                MaalKind.ALTER -> PointLabel.TUNNELA_ALTER to 35
                MaalKind.ORDINARY_JOKER, MaalKind.TIPLU -> PointLabel.TUNNELA_JOKER to 10
                MaalKind.NONE -> PointLabel.TUNNELA_ORDINARY to 5
            }
            items.add(PointItem(label, 1, pts))
        }
        val rest = cards.filter { it !in inTunnela }
        fun count(kind: MaalKind) = rest.count { ctx.kind(it) == kind }.coerceAtMost(3)
        val j = count(MaalKind.JHIPLU)
        val t = count(MaalKind.TIPLU)
        val p = count(MaalKind.POPLU)
        val a = count(MaalKind.ALTER)

        // Pick the number of marriages that gives the most points.
        var bestM = 0
        var best = -1
        for (m in 0..minOf(j, t, p, 2)) {
            val s = MARRIAGE[m] + POPLU_JHIPLU[j - m] + POPLU_JHIPLU[p - m] + TIPLU[t - m]
            if (s > best) {
                best = s
                bestM = m
            }
        }
        if (bestM > 0) items.add(PointItem(PointLabel.MARRIAGE, bestM, MARRIAGE[bestM]))
        if (t - bestM > 0) items.add(PointItem(PointLabel.TIPLU, t - bestM, TIPLU[t - bestM]))
        if (p - bestM > 0) items.add(PointItem(PointLabel.POPLU, p - bestM, POPLU_JHIPLU[p - bestM]))
        if (j - bestM > 0) items.add(PointItem(PointLabel.JHIPLU, j - bestM, POPLU_JHIPLU[j - bestM]))
        if (a > 0) items.add(PointItem(PointLabel.ALTER, a, ALTER[a]))
        return items
    }

    /**
     * Each player's net gain for the hand (negative: they lose that much). Every
     * other player pays the winner T + w − n×S; a negative amount means the winner
     * pays them. [points] and [seen] are indexed by player.
     */
    fun settle(points: List<Int>, seen: List<Boolean>, winner: Int, dubleeWin: Boolean): List<Int> {
        val n = points.size
        val total = points.sum()
        val net = MutableList(n) { 0 }
        for (i in 0 until n) {
            if (i == winner) continue
            val w = (if (seen[i]) SEEN_PAYMENT else UNSEEN_PAYMENT) + (if (dubleeWin) DUBLEE_BONUS else 0)
            net[i] = -(total + w - n * points[i])
        }
        net[winner] = -net.sum()
        return net
    }
}
