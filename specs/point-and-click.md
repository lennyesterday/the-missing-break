# Ninth feature: point and click — travel by clicking the places in the picture

## Why

The player should be able to play without pressing buttons. The crew already clicks things in the pictures (records, the rhyme book, the ball, the cypher); only travelling still used graffiti buttons at the bottom.

## What

- The graffiti buttons that lead to other places (◀ HIT THE BLOCK, RICO'S RECORDS ▶, …) are gone. Instead every way out is **a place in the picture** (an "exit", `class="exit"` with the same `data-action` as before, so the game rules don't change):
  - the thing itself where it is in the picture: a door, a street sign, the gate, the portal;
  - or, where the way out is off the picture, a strip along the picture's edge with a small pulsing arrow (◀), the way the crew walks off.
- Under the pointer an exit lights up and a label shows where it leads (the old button text, e.g. "◀ HIT THE BLOCK"). On a touch screen (no pointer) the labels show all the time.
- Per place:
  - **Basement (`hq`)**: the left edge → the block.
  - **Block (`block`)**: a New York street sign pole on the corner of the court with four green signs: ◀ GOODFELLAS HQ, RICO'S RECORDS ▶, DISCO FEVER ▶, 149 ST STATION ▶; the corner store's door → the store (no STORE ▶ tag any more).
  - **Rico's (`record_shop`)**: the front door → the block.
  - **Station gate (`gate`)**: the gate itself → open it (without the key: turned down as before, Reekz's line); the left edge → the block.
  - **Station (`station`)**, **corner store (`corner_store`)**: the left edge → the block.
  - **Grandmaster Flash (`flash`)**: the portal → back to the basement.
  - **Walks** that wait at a door: Rico's door (ENTER RICO'S) and the open station stairs (ENTER THE STATION) are clicked instead of a button; once the crew is there, the door glows so the player sees it.
- Not travel, so they stay as they are: SKIP on the walks and the intro, the rap battle's choices, the signs' buttons (TAKE IT, …), the 🎒 and 🔊.
- Nothing about the rules or the saves changes.

## Done when

1. No scene picture has a graffiti button for travelling; every way out of a scene is an exit with its label.
2. The block has a street sign for each of its four destinations, and the store's door.
3. The walks to Rico's and into the station end at a door that is clicked.
4. Labels show under the pointer, and always on touch screens.
5. All earlier tests still pass (same actions, same rules).
