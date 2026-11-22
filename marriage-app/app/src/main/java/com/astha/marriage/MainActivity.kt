package com.astha.marriage

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import com.astha.marriage.ui.GameScreen
import com.astha.marriage.ui.HomeScreen
import com.astha.marriage.ui.MarriageTheme
import com.astha.marriage.ui.RulesScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val vm: GameViewModel = viewModel()
            MarriageRoot(vm)
        }
    }
}

@Composable
fun MarriageRoot(vm: GameViewModel) {
    CompositionLocalProvider(LocalStrings provides stringsFor(vm.language)) {
        MarriageTheme {
            when (vm.screen) {
                Screen.HOME -> HomeScreen(vm)
                Screen.RULES -> RulesScreen(vm)
                Screen.GAME -> if (vm.game != null) GameScreen(vm) else HomeScreen(vm)
            }
        }
    }
}
