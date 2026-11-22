package com.astha.marriage.engine

import kotlin.random.Random

/**
 * A computer player. It only uses what its seat may know: its own hand, the
 * table, and the tiplu once it has seen it.
 */
class Bot(private val random: Random = Random.Default) {

    /** Plays one full turn for the current player of [game]. */
    fun playTurn(game: MarriageGame) {
        val me = game.current
        val p = game.players[me]
        if (!p.hasPlayed) game.exposeTunnelas(me)

        // 1. Draw.
        if (game.canDrawDiscard(me) && wantsDiscard(game, me)) game.drawDiscard(me) else game.drawStock(me)

        // 2. See the joker if possible.
        if (!p.hasSeen) {
            val dubleeMode = prefersDublees(p)
            if (dubleeMode && game.canShowDublees(me)) {
                game.showDublees(me)
            } else {
                val show = game.findShow(me) { melds ->
                    val used = melds.flatMap { it.cards }.toSet()
                    evaluate(p.hand.filter { it !in used }, JokerContext.UNSEEN, p, dubleeMode = false)
                }
                if (show != null) game.show(me, show)
                else if (game.canShowDublees(me)) game.showDublees(me)
            }
        }

        // 3. Finish if possible.
        if (game.canWin(me)) {
            game.declareWin(me)
            return
        }

        // 4. Discard.
        game.discard(me, chooseDiscard(game, me))
    }

    private fun prefersDublees(p: PlayerState): Boolean {
        if (p.seen == SeenVia.DUBLEES) return true
        if (p.seen == SeenVia.MELDS || p.startTunnelas.isNotEmpty()) return false
        val pairs = Melds.dublees(p.hand).size
        val pure = Melds.findDisjointPure(p.hand, 2) != null
        return pairs >= 6 || (pairs >= 5 && !pure)
    }

    private fun wantsDiscard(game: MarriageGame, me: Int): Boolean {
        val p = game.players[me]
        val top = game.topDiscard ?: return false
        // A dublee player who may take it is completing the winning pair.
        if (p.seen == SeenVia.DUBLEES) return true
        val ctx = game.contextFor(me)
        val dublee = prefersDublees(p)
        val now = evaluate(p.hand, ctx, p, dublee)
        val with = p.hand + top
        val best = with.filter { it != top }.distinctBy { it.face }
            .maxOf { x -> evaluate(with - x, ctx, p, dublee) }
        return best > now + 4.0
    }

    fun chooseDiscard(game: MarriageGame, me: Int): Card {
        val p = game.players[me]
        val ctx = game.contextFor(me)
        val dublee = prefersDublees(p)
        val options = p.hand.filter { game.canDiscard(me, it) }
        var best = options.first()
        var bestScore = Double.NEGATIVE_INFINITY
        for (c in options.distinctBy { it.face }.shuffled(random)) {
            var s = evaluate(p.hand - c, ctx, p, dublee)
            // Keep point cards when they are known.
            if (ctx.isWild(c)) s -= 6.0
            if (s > bestScore) {
                bestScore = s
                best = c
            }
        }
        return best
    }

    /** Higher is better: how close [hand] is to finishing. */
    fun evaluate(hand: List<Card>, ctx: JokerContext, p: PlayerState, dubleeMode: Boolean): Double {
        if (dubleeMode) return evaluateDublees(hand)
        return if (ctx.tiplu == null) evaluateUnseen(hand, p) else evaluateSeen(hand, ctx)
    }

    private fun evaluateDublees(hand: List<Card>): Double {
        val pairs = Melds.dublees(hand).size
        // Cards in a group of three are only one pair; the third is spare.
        return pairs * 10.0
    }

    /** Before seeing: build pure combinations first, then anything natural. */
    private fun evaluateUnseen(hand: List<Card>, p: PlayerState): Double {
        val need = (3 - p.startTunnelas.size).coerceAtLeast(0)
        val (pure, rest) = maxDisjoint(Melds.allPure(hand), hand)
        var score = 100.0 * minOf(pure.size, need) + 40.0 * (pure.size - minOf(pure.size, need)).coerceAtLeast(0)
        val (naturals, rest2) = maxDisjoint(Melds.allNatural(rest), rest)
        score += 15.0 * naturals.size
        score += partialScore(rest2, pureOnly = true) * 8.0
        score += partialScore(rest2, pureOnly = false) * 2.0
        return score
    }

    /** After seeing: how many cards are still missing, using known jokers. */
    private fun evaluateSeen(hand: List<Card>, ctx: JokerContext): Double {
        val jokers = hand.count { ctx.isWild(it) }
        val naturalsOnly = hand.filter { !ctx.isWild(it) }
        val groups = hand.size / 3
        val (complete, rest) = maxDisjoint(Melds.allNatural(naturalsOnly), naturalsOnly)
        val partials = greedyPartials(rest, ctx)
        val c = minOf(complete.size, groups)
        val q = minOf(partials.size, groups - c)
        val singles = rest.size - 2 * q
        val r = groups - c - q
        val fromSingles = minOf(r, singles)
        val need = q + 2 * fromSingles + 3 * (r - fromSingles)
        val missing = (need - jokers).coerceAtLeast(0)
        return -20.0 * missing + 2.0 * jokers + partials.size
    }

    /** Disjoint combinations covering as many cards as possible (pure ones count a bit more). */
    private fun maxDisjoint(candidates: List<Meld>, cards: List<Card>): Pair<List<Meld>, List<Card>> {
        var best: List<Meld> = emptyList()
        var bestScore = -1.0
        var nodes = 0
        fun dfs(start: Int, chosen: ArrayList<Meld>, used: HashSet<Card>, score: Double) {
            nodes++
            if (score > bestScore) {
                bestScore = score
                best = chosen.toList()
            }
            if (nodes > 3000) return
            for (i in start until candidates.size) {
                val m = candidates[i]
                if (m.cards.any { it in used }) continue
                chosen.add(m)
                used.addAll(m.cards)
                dfs(i + 1, chosen, used, score + if (m.type.isPure) 1.1 else 1.0)
                chosen.removeAt(chosen.size - 1)
                m.cards.forEach { used.remove(it) }
            }
        }
        dfs(0, ArrayList(), HashSet(), 0.0)
        val used = best.flatMap { it.cards }.toSet()
        return best to cards.filter { it !in used }
    }

    /** Pairs one wild card (or a natural third card) away from a combination. */
    private fun greedyPartials(cards: List<Card>, ctx: JokerContext): List<Pair<Card, Card>> {
        val left = cards.toMutableList()
        val out = ArrayList<Pair<Card, Card>>()
        // Adjacent-in-suit first, then two apart, then same rank.
        val tests: List<(Card, Card) -> Boolean> = listOf(
            { a, b -> a.suit == b.suit && Melds.isSequencePartial(a, b) && kotlin.math.abs(a.rank - b.rank) == 1 },
            { a, b -> Melds.isSequencePartial(a, b) },
            { a, b -> Melds.isTripletPartial(a, b) },
        )
        for (test in tests) {
            var i = 0
            while (i < left.size) {
                val a = left[i]
                val j = (i + 1 until left.size).firstOrNull { test(a, left[it]) }
                if (j != null) {
                    out.add(a to left[j])
                    left.removeAt(j)
                    left.removeAt(i)
                } else i++
            }
        }
        return out
    }

    /** Counts pairs that could grow into a combination. */
    private fun partialScore(cards: List<Card>, pureOnly: Boolean): Double {
        var s = 0.0
        for (i in cards.indices) for (j in i + 1 until cards.size) {
            val a = cards[i]
            val b = cards[j]
            s += when {
                a.face == b.face -> if (pureOnly) 1.0 else 0.0
                Melds.isSequencePartial(a, b) -> if (pureOnly) (if (kotlin.math.abs(a.rank - b.rank) == 1) 1.0 else 0.6) else 0.0
                Melds.isTripletPartial(a, b) -> if (pureOnly) 0.0 else 1.0
                else -> 0.0
            }
        }
        return s
    }
}
