# Bot strength calibration

Bot difficulty is set in one place: the `Anchors` table in `Systems/EngineStrength.cs`.
A bot's `elo` (from its `BotProfile`) is interpolated between those rows into three dials:

| Dial | Meaning |
|---|---|
| Depth | How many plies the engine searches. 0 = judge each move by static evaluation only. |
| Margin (cp) | Choose randomly among moves within this many centipawns of the best. Bigger = sloppier. |
| Blunder chance | Probability of playing a random legal move (never one that walks into a mate it can see). |

Elos of 2400 and above (or 0 or less) play at full strength, limited only by the time the caller passes to `RequestAiMove`.

## What was measured

Self-play on the embedded engine (random 6-ply openings, colours alternated, 20-30 games per pairing),
with ratings fitted from the results. The numbers are **relative strength between our own levels**.
They are not human ratings and not CCRL ratings.

| Nominal ELO | Depth | Margin | Blunder | Fitted strength above ELO 100 |
|---:|---:|---:|---:|---:|
| 100 | 0 | 400 | 0.30 | 0 |
| 300 | 1 | 400 | 0.30 | 316 |
| 500 | 1 | 280 | 0.13 | 789 |
| 700 | 1 | 250 | 0.10 | 933 |
| 900 | 1 | 190 | 0.055 | 1170 |
| 1100 | 2 | 120 | 0.03 | 1460 |
| 1300 | 2 | 60 | 0 | 1779 |
| 1500 | 3 | 80 | 0 | 2046 |
| 1700 | 3 | 35 | 0 | 2268 |
| 1900 | 4 | 0 | 0 | 2432 |
| 2100 | 5 | 10 | 0 | 2654 |
| 2300 | 8 | 0 | 0 | 2847 |
| 2400+ | full | 0 | 0 | at least as strong as 2300 |

What this says: the ladder is monotonic (every level beats the one below it, usually by a wide margin),
and there are no cliffs larger than the steps around ELO 100-500. Engine-vs-engine self-play exaggerates gaps
compared to human play, so expect the steps to *feel* smaller to a person.
Real human strength for each level still needs playtesting. Treat the nominal ELO labels as ordering, not as truth.

Other findings that drove the table:

- Depth 0 is a floor. Extra noise barely changes it, so it is used only for the weakest bot.
- At depth 1-2 the margin is a smooth strength dial (about 50 cp is worth tens of Elo).
- Each extra ply from depth 2 upward is worth roughly 100-150 Elo.
- Move times in a Release build: under 400 ms at every level, under 100 ms for most. A Debug build
  (Godot editor with debug checks) is 3-6x slower per move; worst case measured about 1.4 s.
  The game also enforces a 500 ms minimum think time so moves never appear instantly.

## Not measured

- Full-strength play at the game's real time limit (800 ms) against the other levels. In test it was only run
  at 40-200 ms per move. At 800 ms it searches deeper, so it should sit above the 2300 level.
- Strength against real humans.

## Retuning

1. Play a bot yourself and decide if it feels too strong or weak.
2. Edit its row (or the rows around it) in `Anchors`. Changing *margin* is the gentlest adjustment, then
   blunder chance, then depth (a full step).
3. Keep rows ordered so strength rises with ELO. Re-run a self-play ladder if you change several rows.
