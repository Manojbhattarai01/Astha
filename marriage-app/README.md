# Marriage (Android)

The Nepali card game Marriage, played offline against 1–4 computer players.
English and Nepali, switchable on the home screen. Rules: [RULES.md](RULES.md).

Computer players come in two levels. Hard tracks which cards are still live, looks one
draw ahead and avoids feeding the next player; in simulation it beats Easy clearly
(see `BotStrengthTest`).

## Layout
- `engine/` – pure Kotlin game rules: cards, combinations, turns, seeing the joker,
  dublees, scoring, settlement, and the computer players. No Android dependency.
- `app/` – Jetpack Compose user interface.
- `web/` – the same game for phone browsers (iPhone included): the engine compiled to
  JavaScript with Kotlin/JS, plus a plain HTML page. `./gradlew :web:site` writes
  `web/build/site/` (index.html + marriage.js), which any static host can serve.

## Build
Needs JDK 17+ and the Android SDK (platform 36). Open the folder in Android Studio,
or from the command line:

```
./gradlew :engine:test           # rule tests + 300 simulated bot games
./gradlew :app:assembleDebug     # APK in app/build/outputs/apk/debug/
./gradlew :app:testDebugUnitTest # screenshots in app/build/screenshots/
```

## Release signing
Create a keystore once and keep it safe (every Play Store update must use it):

```
keytool -genkeypair -v -keystore marriage-release.jks -alias marriage -keyalg RSA -keysize 2048 -validity 10000
```

Then either put a `keystore.properties` next to this README (it is git-ignored):

```
storeFile=marriage-release.jks
storePassword=...
keyAlias=marriage
keyPassword=...
```

and run `./gradlew :app:assembleRelease` (APK) or `:app:bundleRelease` (Play Store bundle),
or add these GitHub repository secrets so CI builds it:
`MARRIAGE_KEYSTORE_BASE64` (output of `base64 -w0 marriage-release.jks`),
`MARRIAGE_KEYSTORE_PASSWORD`, `MARRIAGE_KEY_ALIAS`, `MARRIAGE_KEY_PASSWORD`.

CI (`.github/workflows/marriage-app.yml`) runs the tests and uploads the APKs and
screenshots as build artifacts on every push that touches `marriage-app/`.
