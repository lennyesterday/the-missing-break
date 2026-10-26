# Eighth feature: story line fixes 2 — coming back to the block

## Why

The block's conversation ("LOOK AT ALL THESE FRESH TAGS…", "…ONLY AN MTA KEY OPENS IT", "THEN WE GET THAT KEY…") is the crew finding the trail. Coming back from Rico's with the key, they said it all over again, as if they'd never been there.

## What

- Like the basement (`specs/story-line-fixes.md`): once the crew has left the block, its first conversation never comes back.
- Coming back to the block **with Rico's key** (`service_key`) and **before winning the record back** (`vinyl`), a short new conversation plays (`SCENES["block"]["dialogue_back"]`, speech bubbles `data-overlay="back-<n>"`):
  - Portals: "WE GOT RICO'S KEY! THAT GATE AIN'T STOPPING US NOW."
  - Needle: "NOW WE CAN WALK UP TO THE STATION. LET'S GET MY RECORD BACK!"
  It plays each time the crew comes back in that part of the story.
- Coming back **without the key**, the crew stays quiet. If the player walks to the station anyway, the gate stays chained shut as before (A1: nothing changes, nothing is saved).
- With the record back, the crew stays quiet on the block too.
- A return conversation can now say when it plays: `when_has` (an item the crew must carry) and `unless_has` (an item it must not carry).
- The new lines have no recordings yet: they stay silent until `static/audio/voices/block/back/<number>_<speaker>.mp3` exist.

## Done when

1. First time on the block: the first conversation.
2. Block → Rico's (take the key) → block: the new conversation, about walking up to the station.
3. Block → Rico's (without the key) → block: no conversation; the gate still doesn't open.
4. With the record back: no conversation on the block.
5. The basement's return conversation works as before.

## Addition: trying the gate without the key

- When the player tries **OPEN THE GATE** without the key, the rules still turn it down (A1: nothing changes, nothing is saved) and the "chained shut" sign shows, and **Reekz** says: "WE REALLY SHOULD HAVE TAKEN THE KEY FROM RICO'S!" (a speech bubble, `data-overlay="locked-0"`; the line is the action's `locked_says` in `logic.py`). The next click puts both away.
- Then **◀ BACK TO THE BLOCK**: right on arriving, **Bible** says: "REEKZ WAS RIGHT. LET'S GET THAT KEY FROM RICO'S!" (`SCENES["block"]["dialogue_after"]["enter_station"]`, bubble `data-overlay="after-0"`). Only on that arrival; coming back later, the crew is quiet again.
- That the crew just tried the gate is not a move: the app remembers it only until the next place (not saved).
- Recordings, when they exist: `static/audio/voices/gate/locked/00_reekz.mp3` and `static/audio/voices/block/after/00_bible.mp3`.

Done when:

6. Gate without the key → OPEN THE GATE: rejected, the sign and Reekz's line show, the save is unchanged.
7. Then BACK TO THE BLOCK: Bible's line; after it, and on later returns without the key, no conversation.
8. With the key the gate opens as before, nobody says Reekz's line.
