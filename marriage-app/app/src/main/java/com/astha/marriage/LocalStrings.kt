package com.astha.marriage

import androidx.compose.runtime.staticCompositionLocalOf

/** The text of the current language; the strings themselves live in the engine module. */
val LocalStrings = staticCompositionLocalOf<Strings> { English }
