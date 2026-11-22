package com.astha.marriage

import android.os.Looper
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.test.core.app.ApplicationProvider
import com.astha.marriage.engine.Phase
import com.github.takahirom.roborazzi.captureRoboImage
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.time.Duration

@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [35], qualifiers = "w393dp-h851dp-xxhdpi")
class ScreenshotTest {
    @get:Rule
    val compose = createComposeRule()

    private val out = System.getProperty("screenshots.dir") ?: "build/screenshots"

    private fun newVm(language: Language = Language.EN, players: Int = 4): GameViewModel {
        val vm = GameViewModel(ApplicationProvider.getApplicationContext())
        vm.updateLanguage(language)
        vm.updatePlayerCount(players)
        return vm
    }

    /** Runs the bots until it is the human's turn or the hand is over. */
    private fun waitForHuman(vm: GameViewModel) {
        repeat(200) {
            if (vm.isHumanTurn || vm.game?.phase == Phase.ROUND_OVER) return
            shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(1500))
            compose.waitForIdle()
        }
    }

    private fun shoot(name: String) {
        compose.waitForIdle()
        compose.onRoot().captureRoboImage("$out/$name.png")
    }

    @Test
    fun home() {
        val vm = newVm()
        compose.setContent { MarriageRoot(vm) }
        shoot("01_home_en")
        vm.updateLanguage(Language.NE)
        shoot("02_home_ne")
    }

    @Test
    fun rules() {
        val vm = newVm(Language.NE)
        vm.screen = Screen.RULES
        compose.setContent { MarriageRoot(vm) }
        shoot("03_rules_ne")
    }

    @Test
    fun gameTurn() {
        val vm = newVm()
        compose.setContent { MarriageRoot(vm) }
        vm.startMatch()
        waitForHuman(vm)
        shoot("04_game_draw")
        vm.tapStock()
        val hand = vm.humanHand()
        vm.tapCard(hand[hand.size / 2])
        shoot("05_game_select")
    }

    @Test
    fun gameAfterSeeing() {
        val vm = newVm()
        compose.setContent { MarriageRoot(vm) }
        vm.startMatch()
        var reached = false
        for (attempt in 0 until 400) {
            waitForHuman(vm)
            val g = vm.game!!
            if (g.phase == Phase.ROUND_OVER) {
                shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(2))
                vm.nextHand()
                continue
            }
            if (vm.humanSeen) {
                vm.tapStock()
                reached = true
                break
            }
            vm.autoPlayHumanTurn()
        }
        assertTrue(reached)
        shoot("06_game_seen")
    }

    @Test
    fun handResult() {
        val vm = newVm(Language.NE)
        compose.setContent { MarriageRoot(vm) }
        vm.startMatch()
        for (attempt in 0 until 400) {
            waitForHuman(vm)
            if (vm.game!!.phase == Phase.ROUND_OVER) break
            vm.autoPlayHumanTurn()
            compose.waitForIdle()
        }
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(2))
        compose.waitForIdle()
        assertTrue(vm.showResult)
        shoot("07_result_ne")
    }
}
