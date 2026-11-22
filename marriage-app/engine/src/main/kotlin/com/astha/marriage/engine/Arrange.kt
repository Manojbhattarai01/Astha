package com.astha.marriage.engine

/** A hand split into finished sets, near-sets and loose cards, for display. */
data class Arrangement(
    val sets: List<Meld>,
    val partials: List<List<Card>>,
    val loose: List<Card>,
)

object Arrange {
    /**
     * Groups [hand] the way a player would lay it out: pure sets first, then (once
     * the joker is known) sets that use jokers, then pairs that need one card, then
     * the rest.
     */
    fun arrange(hand: List<Card>, ctx: JokerContext): Arrangement {
        val sets = ArrayList<Meld>()
        var rest = hand

        // Pure sets: the most that fit together.
        val pure = Melds.allPure(rest)
        val bestPure = maxDisjoint(pure)
        sets += bestPure
        rest = rest - bestPure.flatMap { it.cards }.toSet()

        // Natural triplets.
        val triplets = Melds.allNatural(rest).filter { it.type == MeldType.TRIPLET }
        val bestTriplets = maxDisjoint(triplets)
        sets += bestTriplets
        rest = rest - bestTriplets.flatMap { it.cards }.toSet()

        val partials = ArrayList<List<Card>>()
        if (ctx.tiplu != null) {
            // Use jokers to finish pairs.
            val jokers = rest.filter { ctx.isWild(it) }.toMutableList()
            var naturals = rest.filter { !ctx.isWild(it) }
            for (pair in pairs(naturals)) {
                if (jokers.isEmpty()) break
                if (pair.any { it !in naturals }) continue
                val cards = pair + jokers[0]
                val type = Melds.type(cards, ctx) ?: continue
                jokers.removeAt(0)
                sets += Meld(cards, type)
                naturals = naturals - pair.toSet()
            }
            rest = naturals + jokers
        }
        // Pairs that one more card would finish.
        var left = rest
        for (pair in pairs(rest.filter { !ctx.isWild(it) })) {
            if (pair.any { it !in left }) continue
            partials += pair
            left = left - pair.toSet()
        }
        val loose = left.sortedWith(compareBy({ if (ctx.isWild(it)) 1 else 0 }, { it.suit }, { if (it.rank == 1) 14 else it.rank }))
        return Arrangement(sets, partials, loose)
    }

    /** Candidate pairs, best kinds first: adjacent in suit, two apart, identical, same rank. */
    private fun pairs(cards: List<Card>): List<List<Card>> {
        val out = ArrayList<Pair<Int, List<Card>>>()
        for (i in cards.indices) for (j in i + 1 until cards.size) {
            val a = cards[i]
            val b = cards[j]
            val rank = when {
                Melds.isSequencePartial(a, b) && (kotlin.math.abs(a.rank - b.rank) == 1 || kotlin.math.abs(a.rank - b.rank) == 12) -> 0
                Melds.isSequencePartial(a, b) -> 1
                a.face == b.face -> 2
                Melds.isTripletPartial(a, b) -> 3
                else -> continue
            }
            out += rank to listOf(a, b).sortedBy { if (it.rank == 1 && b.rank > 3) 14 else it.rank }
        }
        return out.sortedBy { it.first }.map { it.second }
    }

    private fun maxDisjoint(candidates: List<Meld>): List<Meld> {
        var best: List<Meld> = emptyList()
        var nodes = 0
        fun dfs(start: Int, chosen: ArrayList<Meld>, used: HashSet<Card>) {
            nodes++
            if (chosen.size > best.size) best = chosen.toList()
            if (nodes > 5000) return
            for (i in start until candidates.size) {
                val m = candidates[i]
                if (m.cards.any { it in used }) continue
                chosen += m
                used += m.cards
                dfs(i + 1, chosen, used)
                chosen.removeAt(chosen.size - 1)
                used -= m.cards.toSet()
            }
        }
        dfs(0, ArrayList(), HashSet())
        return best
    }
}
