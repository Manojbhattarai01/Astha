# Sip Happens 🍸

A funny cocktail app (web version 1). It works fully offline: open `index.html` (it loads `data.js` from the same folder).

- **Cocktails:** about 60 classics, searchable by name, ingredient or brand. Each has a drawn glass, ABV, calories, taste bars, step-by-step method and suggested bottles.
- **Bottles:** about 85 brands, including Nepali bottles like Khukri, 8848 and Ruslan. Each lists type, country, ABV, maker, year founded, price tier, tasting notes, trivia and the cocktails it goes in.
- **Build:** pour your own drink and see live ABV, calories, taste and roasts. **Review** tells you whether you reinvented a classic, made a close "twist", or invented something new, which you then name and save.
- **My bar:** your saved creations, with edit, share (copies the recipe) and delete.

All numbers are estimates and include ice dilution (shake +25%, stir +20%, build +10%, blend +35%). Calories = alcohol (7 kcal/g) + sugars/fats. Brand facts are from an offline shelf list; strengths vary by market.

Data lives in `data.js` (`ING`, `BRANDS`, `COCKTAILS`), so add more cocktails or bottles there.
