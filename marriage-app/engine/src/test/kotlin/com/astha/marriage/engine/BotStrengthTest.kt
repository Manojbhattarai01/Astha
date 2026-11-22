package com.astha.marriage.engine

import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertTrue

/** Hard bots against Easy bots, swapping seats so neither side gets the better seats. */
class BotStrengthTest {
    @Test
    fun hardBeatsEasy() {
        val games = (System.getProperty("bot.games") ?: "600").toInt()
        var hardNet = 0L
        var easyNet = 0L
        var hardWins = 0
        var easyWins = 0
        for (seed in 0 until games) {
            val rnd = Random(10_000 + seed)
            val hardSeatsEven = seed % 2 == 0
            val bots = List(4) { i ->
                val hard = (i % 2 == 0) == hardSeatsEven
                Bot(Random(rnd.nextLong()), if (hard) BotLevel.HARD else BotLevel.EASY)
            }
            val g = MarriageGame(4, seed % 4, Random(rnd.nextLong()))
            var turns = 0
            while (g.phase != Phase.ROUND_OVER && turns < 3000) {
                bots[g.current].playTurn(g)
                turns++
            }
            val r = g.result ?: continue
            for (i in 0 until 4) {
                if (bots[i].level == BotLevel.HARD) hardNet += r.net[i] else easyNet += r.net[i]
            }
            r.winner?.let { if (bots[it].level == BotLevel.HARD) hardWins++ else easyWins++ }
        }
        println("HARD vs EASY over $games hands: wins $hardWins/$easyWins, net points $hardNet/$easyNet")
        assertTrue(hardNet > easyNet, "Hard bots should come out ahead")
    }
}
