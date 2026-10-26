# Sixth feature: story line fixes — coming back to the basement

## Why

The basement's first conversation ("WHO TOOK MY SECRET JOINT?!") is the crew finding the break-in. When the crew hits the block and comes back, they started it all over again, which doesn't make sense in the story.

## What

- The game remembers which places the crew has left at least once (`GameState.left_scenes`, saved with the game, also after a restart). Leaving a place is part of an accepted move, so it is saved with it; a rejected action changes nothing.
- Once the crew has left the basement, its first conversation never comes back.
- Instead, when the crew comes back to the basement **before it has Rico's key** (`service_key`), a short return conversation plays (`SCENES["hq"]["dialogue_back"]`), clicked through like the first one, in its own speech bubbles (`data-overlay="back-<n>"`):
  - Needle: "WE'RE BACK HERE? MY RECORD AIN'T GONNA FIND ITSELF!"
  - Meyhem: "WE REALLY SHOULD GO TO RICO'S AND ASK HIM ABOUT THE SOPRANOS."
- It plays each time the crew comes back without the key. With the key (later in the story: back with the record, back from Grandmaster Flash) the crew says nothing on coming back.
- The return lines are spoken like the first conversation: `static/audio/voices/hq/back/00_needle.mp3` and `01_meyhem.mp3` (listed in `static/audio/CREDITS.md`).
- The other places keep their conversations as before.

## Done when

1. A new game starts with the first basement conversation.
2. Basement → block → basement: the return conversation shows, not the first one; it mentions Rico's and the Sopranos.
3. The same after stopping and restarting the app (RESUME on the block, then back to the basement).
4. Coming back with the key: no conversation.
5. `left_scenes` is saved and loaded; a save from before it loads with nothing left.
