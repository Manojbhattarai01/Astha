package com.astha.marriage.engine

enum class MeldType(val isPure: Boolean) {
    TUNNELA(true),
    PURE_SEQUENCE(true),
    TRIPLET(false),
    DIRTY_SEQUENCE(false),
    DIRTY_TRIPLET(false),

    /** Three wild cards that form nothing on their own. */
    JOKERS(false),
}

data class Meld(val cards: List<Card>, val type: MeldType) {
    init {
        require(cards.size == 3)
    }
}

/** A pair of identical cards. */
data class Dublee(val first: Card, val second: Card) {
    init {
        require(first.face == second.face && first != second)
    }

    val cards: List<Card> get() = listOf(first, second)
}

object Melds {

    /** Values a rank can take in a sequence: the ace is low (1) or high (14). */
    private fun seqValues(rank: Int): IntArray =
        if (rank == Ranks.ACE) intArrayOf(1, 14) else intArrayOf(rank)

    /** The type of three cards without using any card as wild, or null. */
    fun naturalType(a: Card, b: Card, c: Card): MeldType? {
        if (a.face == b.face && b.face == c.face) return MeldType.TUNNELA
        if (a.rank == b.rank && b.rank == c.rank) {
            return if (a.suit != b.suit && b.suit != c.suit && a.suit != c.suit) MeldType.TRIPLET else null
        }
        if (a.suit == b.suit && b.suit == c.suit && isRun(a.rank, b.rank, c.rank)) return MeldType.PURE_SEQUENCE
        return null
    }

    /** Three distinct ranks that are consecutive, with the ace at one end only. */
    private fun isRun(r1: Int, r2: Int, r3: Int): Boolean {
        for (v1 in seqValues(r1)) for (v2 in seqValues(r2)) for (v3 in seqValues(r3)) {
            val lo = minOf(v1, v2, v3)
            val hi = maxOf(v1, v2, v3)
            if (hi - lo == 2 && v1 != v2 && v2 != v3 && v1 != v3) return true
        }
        return false
    }

    /** Two natural cards that a single wild card can turn into a sequence. */
    fun isSequencePartial(a: Card, b: Card): Boolean {
        if (a.suit != b.suit || a.rank == b.rank) return false
        for (va in seqValues(a.rank)) for (vb in seqValues(b.rank)) {
            val d = kotlin.math.abs(va - vb)
            if (d in 1..2) return true
        }
        return false
    }

    /** Two natural cards that a single wild card can turn into a triplet. */
    fun isTripletPartial(a: Card, b: Card): Boolean = a.rank == b.rank && a.suit != b.suit

    /**
     * The type of three cards for a player with joker knowledge [ctx], or null if
     * they are not a valid combination. Wild cards may also count as themselves.
     */
    fun type(cards: List<Card>, ctx: JokerContext): MeldType? {
        if (cards.size != 3) return null
        val (a, b, c) = cards
        if (a == b || b == c || a == c) return null
        naturalType(a, b, c)?.let { return it }
        if (ctx.tiplu == null) return null
        val wild = cards.filter { ctx.isWild(it) }
        if (wild.isEmpty()) return null
        // Any wild card plus at least one more wild card makes a combination.
        if (wild.size >= 2) {
            return if (wild.size == 3) MeldType.JOKERS else {
                val natural = cards.first { it !in wild }
                // Prefer describing it by what the cards could be: two wilds make any card a set.
                if (wild.any { isSequencePartial(it, natural) }) MeldType.DIRTY_SEQUENCE else MeldType.DIRTY_TRIPLET
            }
        }
        val joker = wild[0]
        val (x, y) = cards.filter { it != joker }
        return when {
            isSequencePartial(x, y) -> MeldType.DIRTY_SEQUENCE
            isTripletPartial(x, y) -> MeldType.DIRTY_TRIPLET
            else -> null
        }
    }

    fun meldOrNull(cards: List<Card>, ctx: JokerContext): Meld? = type(cards, ctx)?.let { Meld(cards, it) }

    fun isPure(cards: List<Card>): Boolean =
        cards.size == 3 && cards.distinct().size == 3 && naturalType(cards[0], cards[1], cards[2])?.isPure == true

    /** All pure combinations (tunnelas and pure sequences) that can be made from [cards]. */
    fun allPure(cards: List<Card>): List<Meld> {
        val out = ArrayList<Meld>()
        val n = cards.size
        for (i in 0 until n) for (j in i + 1 until n) {
            val a = cards[i]
            val b = cards[j]
            // Quick filter: pure melds are all one suit.
            if (a.suit != b.suit) continue
            for (k in j + 1 until n) {
                val c = cards[k]
                if (c.suit != a.suit) continue
                val t = naturalType(a, b, c)
                if (t != null && t.isPure) out.add(Meld(listOf(a, b, c), t))
            }
        }
        return out
    }

    /** All natural combinations (pure or triplet) in [cards]. */
    fun allNatural(cards: List<Card>): List<Meld> {
        val out = ArrayList<Meld>()
        val n = cards.size
        for (i in 0 until n) for (j in i + 1 until n) for (k in j + 1 until n) {
            val t = naturalType(cards[i], cards[j], cards[k]) ?: continue
            out.add(Meld(listOf(cards[i], cards[j], cards[k]), t))
        }
        return out
    }

    /**
     * Finds [count] disjoint pure combinations in [cards], or null. Among the
     * possibilities it returns one that [prefer] scores highest (default: first found).
     */
    fun findDisjointPure(
        cards: List<Card>,
        count: Int,
        prefer: ((List<Meld>) -> Double)? = null,
    ): List<Meld>? {
        if (count <= 0) return emptyList()
        val candidates = allPure(cards)
        var best: List<Meld>? = null
        var bestScore = Double.NEGATIVE_INFINITY
        var explored = 0
        fun dfs(start: Int, chosen: ArrayList<Meld>, used: HashSet<Card>): Boolean {
            if (chosen.size == count) {
                explored++
                if (prefer == null) {
                    best = chosen.toList()
                    return true
                }
                val s = prefer(chosen)
                if (s > bestScore) {
                    bestScore = s
                    best = chosen.toList()
                }
                return explored > 400
            }
            for (i in start until candidates.size) {
                val m = candidates[i]
                if (m.cards.any { it in used }) continue
                chosen.add(m)
                used.addAll(m.cards)
                val stop = dfs(i + 1, chosen, used)
                chosen.removeAt(chosen.size - 1)
                used.removeAll(m.cards.toSet())
                if (stop) return true
            }
            return false
        }
        dfs(0, ArrayList(), HashSet())
        return best
    }

    /**
     * Splits all of [cards] into valid three-card combinations, or returns null.
     * [cards] must have a multiple of 3 cards.
     */
    fun partition(cards: List<Card>, ctx: JokerContext): List<Meld>? {
        if (cards.size % 3 != 0) return null
        // Put wild cards last so the search fixes natural cards first.
        val sorted = cards.sortedWith(compareBy({ if (ctx.isWild(it)) 1 else 0 }, { it.suit }, { it.rank }))
        val result = ArrayList<Meld>()
        val remaining = sorted.toMutableList()
        val failed = HashSet<List<Int>>()
        fun key(list: List<Card>): List<Int> = list.map { it.face.suit.ordinal * 13 + it.rank }.sorted()
        fun solve(): Boolean {
            if (remaining.isEmpty()) return true
            val k = key(remaining)
            if (k in failed) return false
            val first = remaining.removeAt(0)
            val n = remaining.size
            val tried = HashSet<Pair<Face, Face>>()
            for (i in 0 until n) for (j in i + 1 until n) {
                val b = remaining[i]
                val c = remaining[j]
                if (!tried.add(b.face to c.face)) continue
                val t = type(listOf(first, b, c), ctx) ?: continue
                remaining.removeAt(j)
                remaining.removeAt(i)
                result.add(Meld(listOf(first, b, c), t))
                if (solve()) return true
                result.removeAt(result.size - 1)
                remaining.add(i, b)
                remaining.add(j, c)
            }
            remaining.add(0, first)
            failed.add(k)
            return false
        }
        return if (solve()) result.toList() else null
    }

    /** Disjoint pairs of identical cards, as many as possible. */
    fun dublees(cards: List<Card>): List<Dublee> =
        cards.groupBy { it.face }.values.flatMap { same -> same.chunked(2).filter { it.size == 2 }.map { Dublee(it[0], it[1]) } }
}
