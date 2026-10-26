# Tenth feature: remove MC Meyhem

## Why

MC Meyhem doesn't add anything to the story and makes the rap battle complicated (who goes first). The crew is four now: Fantastic Needle (DJ), MC Bible (MC), Portals (graffiti), Reekz (b-boy).

## What

- **Meyhem is gone** from every picture, walk and screen (the crew, the street on the home screen, the battle at Disco Fever, the endings, Grandmaster Flash, the corner store, the cypher's circle, his tag on the basement wall) and from the speakers.
- **His lines go to someone else** (same words):

  | Where | Line | Now says it |
  |---|---|---|
  | Basement | "LOOK AT THE WALL! THE SOPRANOS CROSSED OUT OUR NAME!" | Reekz |
  | Basement | "RICO HEARS EVERYTHING. LET'S HIT THE RECORD SHOP!" | Portals |
  | Basement, coming back | "WE REALLY SHOULD GO TO RICO'S AND ASK HIM ABOUT THE SOPRANOS." | Bible |
  | Rico's | "THAT KEY GETS US INTO THE STATION!" | Reekz |
  | Block | "THAT'S WHERE THE SOPRANOS ARE HIDING OUT!" | Portals |
  | Station | "A RAP BATTLE? BET. I'LL GO FIRST." + Bible's "AND I'LL FINISH HIM…" | one line, Bible: "A RAP BATTLE? BET." (he doesn't mention his rhyme book: the player has to remember it) |

- **The rap battle is Bible alone** (no "who goes first"): one choice, **RAP BATTLE** (`rap_battle`): click Bible (a ring pulses round him) or the mic. He takes the battle with or without his rhyme book. With it he raps his verse and wins the record (`vinyl`, `rap_battle = "won"`); without it he chokes, the crowd boos, game over (`ending_lost_battle`), as before. The "wrong order" game over is gone; the game-over screen only says why Bible choked.
- `GameState.rap_battle`: `None`, `"won"` or `"lost"`. A save from before with `"meyhem_went_first"` loads as `None` (the battle is open again).
- **Recordings:** Meyhem's recordings are removed (his verse and his five lines). The lines he gave away are silent until they are recorded in the new speaker's voice, at the same place (`static/audio/voices/hq/03_reekz.mp3`, `hq/08_portals.mp3`, `hq/back/01_bible.mp3`, `record_shop/05_reekz.mp3`, `block/02_portals.mp3`).
- `docs/story.md`, `README.md` and `AGENTS.md` tell the story with the four of them.

## Done when

1. No picture, speaker, line or action has Meyhem in it.
2. His lines are said by Reekz, Portals and Bible as in the table.
3. The station offers RAP BATTLE (and the way back); with the rhyme book it wins the record, without it Bible chokes and it's game over.
4. An old save in the middle of the battle (`meyhem_went_first`) loads with the battle open.
5. The docs tell the story with four crew members.
