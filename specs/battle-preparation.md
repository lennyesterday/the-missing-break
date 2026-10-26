# Thirteenth feature: battle preparation — back on the block after the rap battle

## Why

After Bible wins "Think About It" back at the station, the crew comes back to the block without a word. They should celebrate Bible, and Needle should point the player to what comes next: practicing for the DJ battle.

## What

- Coming to the block **from the station with the record** (`vinyl`), the crew talks (speech bubbles, clicked through, kind `won`):
  > **Reekz:** Bible, you killed that one!
  > **MC Bible:** They call me Bible 'cause I never run out of verses.
  > **Needle:** Now that we got my record back, we're ready for the DJ battle. We just need to practice.
- In the rules: the block's `dialogue_won` (`from`: the station, `when_has`: `vinyl`); `logic.conversation(state, tried, came_from)` gives `("won", those lines)` when the crew has just come from there with the record. It comes before the block's other return conversation.
- Where the crew just came from is only remembered while the game runs (like what was just turned down): not saved. After a restart the crew is simply back on the block (no bubble).
- Voices go in `static/audio/voices/block/won/<NN>_<speaker>.mp3`; until they're recorded the lines are silent.
- Nothing else about the rules or the saves changes.

## Done when

1. Winning the rap battle and walking back to the block shows the three bubbles, one after the other.
2. Coming to the block any other way (from the station without the record, from anywhere else, after a restart) doesn't.
3. The block picture has the three bubbles (`won-0` … `won-2`).

---

## Part 2: Needle tries the break, Portals sprays the portal

### Why

In the basement, with the record back, two graffiti buttons (PRACTICE THE BREAK, ◎ PORTAL TO FLASH) carry the story's turning point. The player should play it instead: click Needle's turntables, see and hear him fail to loop the break, hear the crew decide to find Grandmaster Flash, and click Portals' spray cans to open the portal.

### What

- **The turntables** (with the record, before Needle is stuck): clicking them starts the try (the rule `try_practice`, unchanged). There's no PRACTICE THE BREAK button for it any more; the turntables glow while they can be clicked.
- **The try** (about 15 s, played by the app, nothing saved yet): Needle picks up the record, goes behind the turntables and tries to loop the break of "Think About It". It's always off: the break is cut too early or too late, he spins it back, it stumbles, and at the end the record stops. (A sound made from the drum break: `static/audio/records/think_about_it_off.wav`, made with `art/off_break.py`.) In the picture: the record jumps back each time and a red **OFF!** pops up. When it's over, the rule `try_practice` is taken (the crew is `stuck`) and saved.
- **The conversation** (speech bubbles, clicked through, kind `stuck`), in the basement while the crew is stuck and hasn't met Flash yet (the hq's `dialogue_stuck`):
  > **MC Bible:** That takes too long. We'll never make it in time for the battle!
  > **Needle:** There's only one man who can help us loop the break.
  > **Reekz:** And who's that?
  > **Needle:** The grandmaster: Grandmaster Flash.
  > **Portals:** Does he even exist? I thought he was a legend.
  > **MC Bible:** If we can find him, you must spray a portal!

  It plays once while the game runs (like the first conversation); after a restart while still stuck it plays again, as a reminder. Voices go in `static/audio/voices/hq/stuck/<NN>_<speaker>.mp3`; silent until recorded.
- **The spray cans:** while the crew is stuck, Portals' bag of spray cans glows and can be clicked: that's `go_flash` (unchanged), instead of the ◎ PORTAL TO FLASH button.
- **The walk to Flash** (`hq__flash`): Portals sprays the ring on the wall, it opens into the portal, Reekz says **"YOU DID IT!"**, and the crew walks into the portal one after the other (Portals first, Needle last). Then the camera dives through, to Flash, as before.
- **Later, after Flash:** practicing for real (`practice`, with the crayons) is also started by clicking the turntables, not a button (the same rule, the same crayon and loop games).
- Nothing else about the rules or the saves changes. During the try nothing can be clicked; the try isn't a move until it's over.

### Done when

4. With the record (not stuck), the turntables can be clicked; there's no PRACTICE THE BREAK or PORTAL TO FLASH button in the basement.
5. Clicking them plays the try with the off-loop break; only after it the crew is stuck and that is saved.
6. Then the six bubbles come, one after the other; then Portals' spray cans can be clicked and lead through the portal walk (Reekz: YOU DID IT!, the crew going in) to Flash.
7. After Flash, with crayons, clicking the turntables starts the real practice.
