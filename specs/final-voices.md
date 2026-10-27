# Sixteenth feature: final voices — the block before the final, the walk to the club, battle night

## Why

The product owner recorded the last silent lines before the DJ battle (`Audio Sources/Conversations/`: `Hit the Block`, `Walk to Dj Battle`, `Dj Battle`). Until now these bubbles were silent.

## What

The recordings go into the game the usual way, `static/audio/voices/<scene>[/<kind>]/<NN>_<speaker>.mp3`:

| Recording | File |
|---|---|
| Block, before the final: Reekz, "This is it, GoodFellas. The borough final." | `block/final/00_reekz.mp3` |
| Block, before the final: Needle, "The Sopranos took my break. Tonight I take their crown." | `block/final/01_needle.mp3` |
| Block, before the final: Bible, "Let's go show the Bronx who we are." | `block/final/02_bible.mp3` |
| Walk to the club: King Krete, "Back for more, GoodFellas? Didn't learn the first time?" | `walks/block__battle/00_krete.mp3` |
| Walk to the club: the bouncer, "GoodFellas! Go on in!" | `walks/block__battle/01_bouncer.mp3` |
| Battle night: the host, "The Borough DJ Battle! The final! …" | `battle/00_host.mp3` |
| Battle night: King Krete, "You really think you can beat the Sopranos, Needle?" | `battle/01_krete.mp3` |
| Battle night: Needle, "Step aside, Krete. These are my decks now." | `battle/02_needle.mp3` |
| Battle night: Reekz, "When the real break drops, I'm going down!" | `battle/03_reekz.mp3` |

- **Two lines in one walk.** The bouncer's "GOODFELLAS! GO ON IN." becomes a walk line too (`logic.WALK_LINES["block__battle"]`, after Krete's), so a walk can now have more than one line. The page speaks each one when its bubble shows (a walk's voice is a list of lines, each with its own `delay`).
- **One after the other.** Krete's line takes about 4.3 s, so the bouncer speaks after it (4.8 s into the walk). The crew waits by Krete's crate while he talks, then walks up to the door. The bouncer lifts the rope just as Reekz reaches it, and Krete's bubble stays up as long as he speaks.
- Credits in `static/audio/CREDITS.md`. Nothing about the rules or the saves changes.

## Done when

1. Each of these lines is spoken when its bubble comes up (the walk's lines when their bubbles show, Krete's first, then the bouncer's).
2. Every recording belongs to a line with the same speaker.
3. All earlier tests still pass (changed explicitly where the walk to the club had only Krete's line, and where `block/final/` was still listed as not recorded).
