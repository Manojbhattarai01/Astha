# Marriage — Final Rules for the App

Based on https://www.pagat.com/rummy/marriage.html, with the house choices agreed below.

## App scope
- One human player against 1–4 computer bots (2–5 players total), works offline.
- Native Android: Kotlin + Jetpack Compose.
- Interface in English and Nepali, switchable in settings.

## Players and cards
- 2–5 players, three standard 52-card decks (156 cards), no printed jokers.
- Play and deal pass **clockwise**: the player to the dealer's left starts, and the next deal goes to the left.

## Deal
- 21 cards to each player. The next card is turned face up to start the discard pile; the rest form the face-down stock.
- A player dealt a tunnela may expose it immediately. Only these exposed tunnelas can score.

## Combinations (always exactly 3 cards)
| Name | Definition |
|---|---|
| Tunnela | 3 identical cards (same rank and suit). No jokers allowed. |
| Pure sequence | 3 consecutive cards of one suit. Ace can be high (Q-K-A) or low (A-2-3), never in the middle (K-A-2 invalid). |
| Triplet | 3 cards of the same rank, all different suits. |
| Dirty sequence / dirty triplet | A sequence or triplet in which one or two cards are jokers. |

Invalid example: two identical cards plus a joker (5♠ 5♠ + joker).

## Turn
1. Draw either the top card of the stock or **only the card just discarded by the previous player**. Older discards stay visible but cannot be taken.
2. Discard one card. You may not discard the card you just took from the discard pile.

## Seeing the joker (tiplu)
- To "see", lay down 3 pure sequences and/or tunnelas (any mix). Exposed starting tunnelas count.
- The first player to see picks a random card from the middle of the stock. That card is the **tiplu**; it is placed face down at the bottom of the stock, and only seen players know it.
- Later players who lay down 3 pure sequences or tunnelas may also look at the tiplu.
- Wild cards (jokers) once the tiplu is known:
  - **Tiplu**: the other cards identical to the tiplu.
  - **Poplu**: the card one rank above the tiplu, same suit.
  - **Jhiplu**: the card one rank below the tiplu, same suit.
  - **Alter**: same rank and same colour as the tiplu, other suit (e.g. tiplu J♥ → alter J♦).
  - **Ordinary jokers**: every other card of the tiplu's rank.
  - Rank order for poplu and jhiplu wraps around: …Q, K, A, 2, 3…
- A seen player may **not** take a joker from the discard pile.

## Dublees (alternative route)
- A dublee is a pair of identical cards. Jokers cannot stand in for anything here.
- With 7 dublees you may lay them down and see the tiplu.
- After seeing, a dublee player may take a discard only if it completes the 8th dublee.

## Ending the hand
- **Normal win**: a seen player draws, completes 4 more valid combinations (jokers allowed) for 21 cards in sets, lays them down and discards the 22nd card.
- **Dublee win**: a player with 8 dublees after drawing lays them down. The other 5 cards and the discard can be anything.
- Apart from starting tunnelas and the 3 combinations needed to see, sets stay in hand until the end.
- Drawing, seeing and winning can all happen in a single turn.
- If the stock runs out (only the tiplu left), the discard pile except its top card is shuffled to form a new stock, with the tiplu staying at the bottom.

## Points (only players who have seen the tiplu score)
Each card counts toward one item only.

| | single | double | triple | tunnela |
|---|---|---|---|---|
| Ordinary card | – | – | – | 5 |
| Ordinary joker | – | – | – | 10 |
| Poplu or jhiplu | 2 | 5 | 10 | 20 |
| Tiplu | 3 | 7 | – | – |
| Alter | 5 | 15 | 35 | – |
| Marriage (jhiplu + tiplu + poplu) | 10 | 30 | – | – |

- Tunnela points apply only to tunnelas exposed right after the deal.
- Three identical alters form a tunnela; they score 35 in total, and the ordinary-joker tunnela 10 does not also apply.

## Settlement
- Each opponent pays the winner **3** if they have seen the tiplu, or **10** if they have not.
- If the winner finished with 8 dublees, every opponent pays the winner **5** more.
- Every pair of players settles the difference between their points.
- Short form used by the app. With n players, T the sum of all scores, S a player's own score, and w = (3 if seen, else 10) + (5 if dublee win), that player pays the winner `T + w − n×S`. If the amount is negative, the winner pays the player.
