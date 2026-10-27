# Seventeenth feature: the DJ battle — Needle's set

## Why

Until now START THE BATTLE goes straight to an ending screen: the battle the whole story leads up to is never seen or heard. When the crew has done everything right (the record is back and Needle has practiced), the player should see and hear Needle win it: a mix of the classics, then "Think About It" drops and the club goes off.

## What

### When

Only on the way to **Legends of the Bronx** (the crew has `vinyl` and `practiced`). START THE BATTLE is still one action in the rules and is saved right away, as before (the ending is set). The app plays **Needle's set** first, then shows the ending. SKIP jumps to the ending. After a restart during the set, the game goes straight to the ending (it's saved). The other endings (Out of Practice, Lost in the Static) stay as they are: no set.

### The mix (about 41 s)

`static/audio/records/needle_mix.wav`, made from the records on the basement floor by `art/needle_mix.py` (`uv run python -m art.needle_mix`, macOS: it decodes the mp3s with `afconvert`). Needle cuts from break to break: two bars of each (8 beats, at its own tempo, starting on a beat), a quick scratch between them, all at the same loudness:

| # | Record | From |
|---|---|---|
| 1 | Apache | the break, 2:12 |
| 2 | Funky Drummer | the break, 2:12 |
| 3 | It's Just Begun | the break, 2:15 |
| 4 | The Mexican | 1:17 |
| 5 | Vitamin C | 1:49 |
| 6 | Impeach the President | the drums at the start |

Then he spins the record back (a rewind, a beat of silence) and **"Think About It" drops** (about 28.4 s in): the drum break, three times round its 2-bar loop (about 12.6 s). The timing is in `art/needle_mix.py` (`timeline()`); the rules know when the drop comes and how long the set is (`logic.DJ_SET`), and a test checks they match.

### The picture (`assets/screens/dj_set.svg`)

The club, battle night. Needle is behind the decks (the Soprano has stepped aside, arms crossed, next to King Krete on his speaker stack). A sign over the booth says what's spinning (APACHE, FUNKY DRUMMER, …, THINK ABOUT IT) and changes at each cut; SCRATCH! pops up at every scratch. The crowd nods along, the crew stands at the front.

When "Think About It" drops:
- the lights flash, the spots speed up, a big THINK ABOUT IT! piece comes up;
- **the crowd** goes wild (jumping, arms up), and someone in it says **"YOO! I NEVER HEARD THIS ONE!"**;
- **the b-boys in the crowd** come out onto the dance floor and toprock;
- **Reekz** goes down and breaks (headspin, 1990);
- **Bible and Portals** are hype men: they jump around, arms up; Bible: **"SAY HO!"**, the crowd: **"HO!"**;
- **Portals snatches King Krete's crown**: he runs over to the speaker stack, takes the crown off Krete's head, runs to the booth and puts it on Needle's head. Krete: **"HEY! MY CROWN!"** (and he shakes, angry);
- at the end, the host: **"THE GOODFELLAS WIN THE BOROUGH DJ BATTLE!"**

Then the page goes on to the ending by itself (`set_over`); SKIP does that at once. On the Legends of the Bronx ending, Needle wears the crown.

The lines are in the rules (`logic.DJ_SET["lines"]`: who, the line, when in seconds into the set), like a walk's lines; voices go in `static/audio/voices/battle/set/<NN>_<speaker>.mp3` and stay silent until recorded.

Credits in `static/audio/CREDITS.md`. Nothing about the rules' outcomes or the saves changes.

## Done when

1. With the record and practice, START THE BATTLE saves the Legends ending, plays the set (the mix, the picture), and the ending comes up when it's over or on SKIP.
2. Without the record or without practice, START THE BATTLE goes straight to its ending, as before.
3. The mix is about 41 s; the drop comes when the rules say; the picture's changes (the sign, the crowd, Reekz, the b-boys, the crown) happen at the drop or after it.
4. All earlier tests still pass.
