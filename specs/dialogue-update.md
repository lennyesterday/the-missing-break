# Fourteenth feature: dialogue update — the new recordings

## Why

The product owner recorded the lines of the station, the block after the win, the basement after Needle's failed try, the walk through Portals' portal and Grandmaster Flash's realm (`Audio Sources/Conversations/`). Until now these bubbles were silent.

## What

The recordings go into the game the usual way, `static/audio/voices/<scene>[/<kind>]/<NN>_<speaker>.mp3`:

| Recording | File |
|---|---|
| Station: Bible, "A rap battle? Bet." | `station/05_bible.mp3` |
| Block (back from the station): Reekz, "Bible, you killed that one!" | `block/won/00_reekz.mp3` |
| Block: Bible, "They call me Bible 'cause I never run out of verses." | `block/won/01_bible.mp3` |
| Block: Needle, "Now that we got my record back…" | `block/won/02_needle.mp3` |
| Basement (stuck): Bible, "That takes too long…" | `hq/stuck/00_bible.mp3` |
| Basement: Needle, "There's only one man who can help us loop the break." | `hq/stuck/01_needle.mp3` |
| Basement: Reekz, "And who's that?" | `hq/stuck/02_reekz.mp3` |
| Basement: Needle, "The grandmaster: Grandmaster Flash." | `hq/stuck/03_needle.mp3` |
| Basement: Portals, "Does he even exist? I thought he was a legend." | `hq/stuck/04_portals.mp3` |
| Basement: Bible, "If we can find him, you must spray a portal!" | `hq/stuck/05_bible.mp3` |
| Flash's realm: Needle, "Grandmaster Flash! I can't catch the break…" | `flash/00_needle.mp3` |
| Flash: "You're listening for the break, young blood. Stop listening. Look." | `flash/01_flash.mp3` |
| Flash: "The secret lies in the crayon." | `flash/02_flash.mp3` |
| Flash's realm: Needle, "The crayon?" | `flash/03_needle.mp3` |
| Flash: "Mark where the break starts over. Then the record tells you when." | `flash/04_flash.mp3` |
| Flash's realm: Portals, "The corner store sells crayons. But we're broke…" | `flash/05_portals.mp3` |
| Flash's realm: Reekz, "Then I'll break for it. That cypher on the block pays!" | `flash/06_reekz.mp3` |
| The walk through the portal: Reekz, "You did it!" | `walks/hq__flash/00_reekz.mp3` |

- **A line in a walk:** Reekz's "YOU DID IT!" is said during the walk through the portal (`hq__flash`), not in a bubble the player clicks. The walk's lines are in the rules (`logic.WALK_LINES`: the walk, then who says what and when, in seconds into the walk). The picture shows the bubble then, and the page speaks it then: a voice can wait (`delay`, in seconds) before it plays. Voices for walks go in `static/audio/voices/walks/<walk>/<NN>_<speaker>.mp3`.
- Still silent until recorded: Bible coming back to the basement (`hq/back/01_bible.mp3`).
- Credits in `static/audio/CREDITS.md`. Nothing about the rules or the saves changes.

## Done when

1. Each of these lines is spoken when its bubble comes up (the walk's line when its bubble shows).
2. Every recording belongs to a line with the same speaker.
3. All earlier tests still pass.
