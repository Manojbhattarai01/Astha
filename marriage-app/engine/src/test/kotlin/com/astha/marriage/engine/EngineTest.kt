package com.astha.marriage.engine

import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

private fun c(text: String, copy: Int = 0): Card {
    val suit = when (text.last()) {
        's' -> Suit.SPADES
        'h' -> Suit.HEARTS
        'c' -> Suit.CLUBS
        'd' -> Suit.DIAMONDS
        else -> error(text)
    }
    val rank = when (val r = text.dropLast(1)) {
        "A" -> 1
        "J" -> 11
        "Q" -> 12
        "K" -> 13
        else -> r.toInt()
    }
    return Card.of(suit, rank, copy)
}

class MeldTest {
    private val unseen = JokerContext.UNSEEN

    // Tiplu J♥: jokers are every jack, Q♥ (poplu) and 10♥ (jhiplu).
    private val seen = JokerContext(Face(Suit.HEARTS, 11))

    @Test
    fun naturalCombinations() {
        assertEquals(MeldType.TUNNELA, Melds.type(listOf(c("6s"), c("6s", 1), c("6s", 2)), unseen))
        assertEquals(MeldType.PURE_SEQUENCE, Melds.type(listOf(c("3d"), c("5d"), c("4d")), unseen))
        assertEquals(MeldType.PURE_SEQUENCE, Melds.type(listOf(c("Qc"), c("Kc"), c("Ac")), unseen))
        assertEquals(MeldType.PURE_SEQUENCE, Melds.type(listOf(c("Ac"), c("2c"), c("3c")), unseen))
        assertEquals(MeldType.TRIPLET, Melds.type(listOf(c("Ks"), c("Kh"), c("Kd")), unseen))
    }

    @Test
    fun invalidCombinations() {
        assertNull(Melds.type(listOf(c("Kc"), c("Ac"), c("2c")), unseen), "K-A-2 is not a sequence")
        assertNull(Melds.type(listOf(c("9s"), c("9s", 1), c("9h")), unseen), "triplet suits must differ")
        assertNull(Melds.type(listOf(c("3d"), c("4d"), c("6d")), unseen))
        // Two identical cards plus a joker is not valid.
        assertNull(Melds.type(listOf(c("5s"), c("5s", 1), c("Js")), seen))
        // Without having seen, jokers are not wild.
        assertNull(Melds.type(listOf(c("6s"), c("Js"), c("8s")), unseen))
    }

    @Test
    fun dirtyCombinations() {
        assertEquals(MeldType.DIRTY_SEQUENCE, Melds.type(listOf(c("6s"), c("Qh"), c("8s")), seen))
        assertEquals(MeldType.DIRTY_TRIPLET, Melds.type(listOf(c("Jc"), c("2s"), c("2d")), seen))
        assertNotNull(Melds.type(listOf(c("Jc"), c("Js"), c("4d")), seen), "two jokers and any card")
        assertNull(Melds.type(listOf(c("Kc"), c("Js"), c("2c")), seen), "joker cannot fill K-?-2")
    }

    @Test
    fun marriageIsAPureSequence() {
        assertTrue(Melds.isPure(listOf(c("10h"), c("Jh"), c("Qh"))))
    }

    @Test
    fun partitionUsesJokers() {
        val hand = listOf(c("2s"), c("3s"), c("Jc"), c("9d"), c("9c"), c("9h"), c("5h"), c("6h"), c("7h"), c("Kd"), c("Qd"), c("Js"))
        val melds = Melds.partition(hand, seen)
        assertNotNull(melds)
        assertEquals(4, melds.size)
        assertNull(Melds.partition(hand, unseen))
    }

    @Test
    fun maalKinds() {
        assertEquals(MaalKind.TIPLU, seen.kind(c("Jh")))
        assertEquals(MaalKind.POPLU, seen.kind(c("Qh")))
        assertEquals(MaalKind.JHIPLU, seen.kind(c("10h")))
        assertEquals(MaalKind.ALTER, seen.kind(c("Jd")))
        assertEquals(MaalKind.ORDINARY_JOKER, seen.kind(c("Js")))
        assertEquals(MaalKind.NONE, seen.kind(c("Qs")))
        // Wrapping: tiplu K → poplu A, tiplu A → jhiplu K.
        val k = JokerContext(Face(Suit.SPADES, 13))
        assertEquals(MaalKind.POPLU, k.kind(c("As")))
        val a = JokerContext(Face(Suit.SPADES, 1))
        assertEquals(MaalKind.JHIPLU, a.kind(c("Ks")))
        assertEquals(MaalKind.POPLU, a.kind(c("2s")))
    }
}

class ScoringTest {
    private val tiplu = Face(Suit.HEARTS, 11)

    @Test
    fun marriageAndSingles() {
        val cards = listOf(c("10h"), c("Jh"), c("Qh"), c("Qh", 1), c("2s"))
        val items = Scoring.points(cards, emptyList(), tiplu)
        assertEquals(12, items.sumOf { it.points }, "marriage 10 + poplu 2")
    }

    @Test
    fun alterCounts() {
        assertEquals(5, Scoring.points(listOf(c("Jd")), emptyList(), tiplu).sumOf { it.points })
        assertEquals(15, Scoring.points(listOf(c("Jd"), c("Jd", 1)), emptyList(), tiplu).sumOf { it.points })
        assertEquals(35, Scoring.points(listOf(c("Jd"), c("Jd", 1), c("Jd", 2)), emptyList(), tiplu).sumOf { it.points })
        // An exposed tunnela of alters also scores 35, not 35 + 10.
        val t = Meld(listOf(c("Jd"), c("Jd", 1), c("Jd", 2)), MeldType.TUNNELA)
        assertEquals(35, Scoring.points(t.cards, listOf(t), tiplu).sumOf { it.points })
    }

    @Test
    fun tunnelaPoints() {
        val ordinary = Meld(listOf(c("4s"), c("4s", 1), c("4s", 2)), MeldType.TUNNELA)
        assertEquals(5, Scoring.points(ordinary.cards, listOf(ordinary), tiplu).sumOf { it.points })
        val poplu = Meld(listOf(c("Qh"), c("Qh", 1), c("Qh", 2)), MeldType.TUNNELA)
        assertEquals(20, Scoring.points(poplu.cards, listOf(poplu), tiplu).sumOf { it.points })
        // Not exposed at the deal: only triple poplu points.
        assertEquals(10, Scoring.points(poplu.cards, emptyList(), tiplu).sumOf { it.points })
    }

    @Test
    fun doubleMarriageBeatsSingles() {
        val cards = listOf(c("10h"), c("10h", 1), c("Jh"), c("Jh", 1), c("Qh"), c("Qh", 1))
        assertEquals(30, Scoring.points(cards, emptyList(), tiplu).sumOf { it.points })
    }

    @Test
    fun settlementMatchesPairwisePayments() {
        val points = listOf(4, 12, 7, 0)
        val seen = listOf(true, true, true, false)
        val winner = 2
        val net = Scoring.settle(points, seen, winner, dubleeWin = false)
        assertEquals(0, net.sum())
        // Pairwise method from pagat.
        val expected = MutableList(4) { 0 }
        for (i in 0 until 4) {
            if (i != winner) {
                val w = if (seen[i]) 3 else 10
                expected[i] -= w
                expected[winner] += w
            }
            for (j in 0 until 4) if (i != j) expected[i] += points[i] - points[j]
        }
        assertEquals(expected, net)
    }
}

class GameTest {
    @Test
    fun dealGives21CardsEach() {
        val g = MarriageGame(4, 0, Random(1))
        g.players.forEach { assertEquals(21, it.hand.size) }
        assertEquals(156 - 84 - 1, g.stockSize)
        assertEquals(1, g.current)
    }

    @Test
    fun arrangeKeepsEveryCard() {
        for (seed in 0 until 50) {
            val g = MarriageGame(4, 0, Random(seed))
            val hand = g.players[1].hand
            for (ctx in listOf(JokerContext.UNSEEN, JokerContext(hand[0].face))) {
                val a = Arrange.arrange(hand, ctx)
                val all = a.sets.flatMap { it.cards } + a.partials.flatten() + a.loose
                assertEquals(hand.toSet(), all.toSet())
                assertEquals(hand.size, all.size)
                a.sets.forEach { assertNotNull(Melds.type(it.cards, ctx)) }
            }
        }
    }

    @Test
    fun showChosenDublees() {
        // Find a deal where the first player can be given seven pairs.
        val g = MarriageGame(2, 0, Random(3))
        val p = g.players[1]
        val pairs = Card.fullShoe().groupBy { it.face }.values.take(7).map { Dublee(it[0], it[1]) }
        p.hand.clear()
        p.hand.addAll(pairs.flatMap { it.cards } + Card.fullShoe().filter { c -> pairs.none { it.first.face == c.face } }.take(7))
        g.drawStock(1)
        g.showDublees(1, pairs.reversed())
        assertEquals(pairs.reversed(), p.shownDublees)
    }

    @Test
    fun cannotDiscardCardJustTaken() {
        val g = MarriageGame(3, 0, Random(2))
        val taken = g.drawDiscard(1)
        assertFalse(g.canDiscard(1, taken))
    }

    @Test
    fun botGamesFinishAndStayConsistent() {
        var wins = 0
        var dubleeWins = 0
        for (seed in 0 until 300) {
            val rnd = Random(seed)
            val n = 2 + seed % 4
            val g = MarriageGame(n, seed % n, rnd)
            val bot = Bot(rnd)
            var turns = 0
            while (g.phase != Phase.ROUND_OVER) {
                bot.playTurn(g)
                turns++
                check(turns < 3000) { "game $seed did not end" }
                val total = g.players.sumOf { it.allCards.size } + g.stockSize + g.discardPile.size + (if (g.tiplu != null) 1 else 0)
                assertEquals(156, total, "cards lost in game $seed")
            }
            val r = g.result!!
            assertEquals(0, r.net.sum())
            if (r.winner != null) {
                wins++
                if (r.byDublees) dubleeWins++
                val w = g.players[r.winner!!]
                assertTrue(w.hasSeen)
                if (!r.byDublees) {
                    assertEquals(7, w.laidMeldCount + r.winningMelds.size, "seven combinations in game $seed")
                }
            }
        }
        println("wins=$wins dubleeWins=$dubleeWins of 300")
        assertTrue(wins > 250)
    }
}
