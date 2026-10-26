# Fifteenth feature: additional little conversations and scenes — from Flash to the DJ battle

## Why

Everything up to Grandmaster Flash has the crew talking. After Flash the game goes quiet: the crew comes back, wins the cypher, buys crayons, practices and goes to the Borough DJ Battle without a word. Short conversations should carry the player through it, each pointing to what comes next.

## What

### The moments

A place can have "moments" (`moments` in its scene): short conversations (speech bubbles, clicked through, like the others) that come when their conditions fit, each with its own name (`kind`). Conditions: `from` (the crew has just come from there), `when_has` / `unless_has` (an item), `when_flag` / `unless_flag` (`stuck`, `met_flash`, `practiced`), `money` (`"none"` or `"some"`), `just_did` (the action the crew has just done here, e.g. practicing). `logic.conversation(state, tried, came_from, just_did)` gives the first moment that fits as `(kind, lines)`; it comes after the conversation for being turned down, the "won" and the "stuck" ones and before coming back. What was just done, like where the crew came from, is only remembered while the game runs (not saved). Each moment is played once while the game runs.

| # | Where, when | Kind | Lines |
|---|---|---|---|
| 1 | Basement, just back from Flash, no crayons yet | `from_flash` | **Portals:** Yo... did that just happen? We were in outer space! · **Reekz:** Grandmaster Flash is real, and he put us on! · **Needle:** A crayon. All these years and the secret is a crayon. · **Bible:** Then let's get one. To the block! |
| 2 | Block, after Flash, no crayons, no money (not practiced) | `cypher` | **Reekz:** Look, the cypher's going on in front of the corner store! · **Portals:** They pass the hat for whoever wins. · **Reekz:** Hold my ghettoblaster. I'm getting us that crayon money. |
| 3 | Block, Reekz has just won the cypher | `cypher_won` | **Bible:** Reekz, you ate those b-boys alive! · **Reekz:** Windmill, freeze, done. Ten bucks, baby. · **Needle:** That's crayon money. Corner store, let's go! |
| 4a | Corner store, after Flash, with money (not practiced) | `buying` | **Clerk:** What'll it be, fellas? Cash only. · **Needle:** One box of crayons, please. · **Clerk:** Crayons? You boys going back to school? · **Portals:** Nah. We're going to the Borough DJ Battle. |
| 4b | Corner store, after Flash, no crayons, no money | `broke` | **Clerk:** No money, no crayons. Come back with cash. · **Reekz:** Bet. The cypher's right outside. |
| 5 | Block, just out of the corner store with the crayons (not practiced) | `crayons` | **Needle:** Got the crayons. Now back to the decks! |
| 6 | Basement with the crayons (not practiced) | `crayons` | **Needle:** Okay, Flash. Let's see if your crayon works. · **Portals:** Mark it like a tag, Needle. Right where it starts over. |
| 7 | Basement, Needle has just practiced (he loops the break) | `looped` | **Needle:** I got it! The break, it's looping! · **Reekz:** That's the one! I could break to that all night! · **Bible:** Flash was right. Stop listening, look. · **Portals:** Then what are we waiting for? The Borough DJ Battle! |
| 8 | Block, just come from the basement, practiced | `final` | **Reekz:** This is it, GoodFellas. The borough final. · **Needle:** The Sopranos took my break. Tonight I take their crown. · **Bible:** Let's go show the Bronx who we are. |

- Moment 7 takes the place of the READY FOR THE FINAL! sign after practicing.
- Voices: `static/audio/voices/<scene>/<kind>/<NN>_<speaker>.mp3`; silent until recorded.

### The little scenes

- **LOOPED!** Once Needle has practiced, Portals' fresh piece **LOOPED!** is on the basement wall, sprayed over the Sopranos' tag (it sprays in when it appears).
- **Crayola, baby!** On the walk from the corner store back to the block, when the crew has the crayons, Needle says **"CRAYOLA, BABY!"** (a bubble that walks with him).
- **King Krete outside the Borough DJ Battle.** On the walk to the Borough DJ Battle, King Krete sits on a crate by the club, under the Sopranos' tag: **"BACK FOR MORE, GOODFELLAS? DIDN'T LEARN THE FIRST TIME?"**
- Lines said during a walk are in `logic.WALK_LINES` as before; a walk's lines that need an item are in `logic.WALK_LINES_WHEN_HAS` (the crayons). Voices: `static/audio/voices/walks/<walk>/<NN>_<speaker>.mp3`.

Nothing about the rules or the saves changes.

## Done when

1. Each of the eight conversations comes at its moment, one bubble after the other, and not when its conditions don't fit (and not twice while the game runs).
2. The pictures have their bubbles (`<kind>-<n>`), the LOOPED! piece, Krete's and Needle's walk lines.
3. All earlier tests still pass (changed explicitly where the READY FOR THE FINAL! sign is replaced).

## Renamed: the Borough DJ Battle

The product owner renamed Disco Fever: it's called **the Borough DJ Battle** everywhere: in what the crew and the host say, on the flyers (BOROUGH / DJ BATTLE / THE FINAL / SATURDAY), on the street sign (BOROUGH DJ BATTLE ▶), on the club's neon sign, in the walk's caption (TO THE BOROUGH DJ BATTLE) and in the action's label (Head to the Borough DJ Battle). Earlier specs keep the old name as they were written.

## The recordings

The product owner recorded the conversations (`Audio Sources/Conversations/`); they go in the usual folders, one per moment: `hq/from_flash/`, `hq/looped/`, `hq/crayons/`, `corner_store/buying/`, `block/cypher/`, `block/cypher_won/`, `block/crayons/`. The clerk's "What'll it be, fellas? Cash only." is the same line as the corner store's first conversation, so it's used there too (`corner_store/00_clerk.mp3`). Still silent until recorded: the clerk without money (`corner_store/broke/`), the block before the final (`block/final/`), Needle's "Crayola, baby!" (`walks/corner_store__block/`) and King Krete outside the club (`walks/block__battle/`).
