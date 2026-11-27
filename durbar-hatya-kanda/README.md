# दरबार हत्याकाण्ड (Durbar Hatya Kanda)

A Nepali-language murder-mystery deduction game for mobile: you vs 1–3 bots.
All characters and events are fictional.

**Play:** open `index.html` in a phone browser. It is a single file with no build step and works offline.

## How it plays
- Three hidden cards (killer, weapon, room) are the solution. All other cards are dealt to the players.
- On your turn you move to a neighbouring room on the 3×3 palace map, then ask about a suspect and a weapon in that room.
- Going around the table, the first player holding one of the asked cards secretly shows you one.
- Use the 📓 notebook (✗ / ? / ✓) to track what you know. Make your accusation when you're sure: right wins, wrong loses.

## Bots
- **सजिलो (easy):** remembers the cards shown to it and sometimes notices passes.
- **कठिन (hard):** full logical deduction. It tracks every "showed one of these three" event and each player's hand size, and it accuses as soon as it is certain.
