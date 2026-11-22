# Marriage (Android)

The Nepali card game Marriage, played offline against 1–4 computer players.
English and Nepali, switchable on the home screen. Rules: [RULES.md](RULES.md).

## Layout
- `engine/` – pure Kotlin game rules: cards, combinations, turns, seeing the joker,
  dublees, scoring, settlement, and the computer players. No Android dependency.
- `app/` – Jetpack Compose user interface.

## Build
Needs JDK 17+ and the Android SDK (platform 36). Open the folder in Android Studio,
or from the command line:

```
./gradlew :engine:test           # rule tests + 300 simulated bot games
./gradlew :app:assembleDebug     # APK in app/build/outputs/apk/debug/
./gradlew :app:testDebugUnitTest # screenshots in app/build/screenshots/
```
