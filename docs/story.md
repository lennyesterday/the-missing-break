# The Missing Break — story content

South Bronx, summer 1977. Two days before the borough DJ battle at Disco Fever, the Concrete Kings break into the crew's basement and steal their secret weapon: an unheard Brazilian break, **Tom Zé – "Dor e Dor"**. Without it, the crew can't win.

## The crew and their part in the story

| Member | Element | Hook | What they do in the game |
|---|---|---|---|
| Fantastic Needle | DJ | On point like a needle | Drops "Dor e Dor" in the final battle and wins it |
| MC Bible | MC | Never runs out of verses, the lyrical genius | Finishes the rap battle in round 2, but only with his rhyme book |
| MC Meyhem | MC | Raps so fast he causes mayhem | Opens the rap battle in round 1, and the Kings' MC can't keep up |
| Portals | Graffiti | His pieces take you to another dimension | Reads the Kings' tags (the right choice) or paints over them (the wrong choice) |
| Reekz | B-boy | Only goes down to the real breaks | Only goes down when Needle drops the real break, and the crowd goes wild |

**Rival crew:** the Concrete Kings, with their MC, King Krete.

## Items (PT03, PT R2)

| ID | Item | Where | Unlocks |
|---|---|---|---|
| `rhyme_book` | MC Bible's rhyme book | On the couch in `hq` | Round 2 of the rap battle |
| `service_key` | Old MTA service key | Drawer behind Rico's counter (`record_shop`) | The route from `block` → `station` |
| `vinyl` | Tom Zé – "Dor e Dor" | Prize for winning the rap battle (`station`) | The winning ending |

Each item can be collected once and is not used up.

## Decision (PT04)

| ID | Where | Options | Effect later |
|---|---|---|---|
| `tag_choice` | `block` | `read`: Portals decodes the Kings' tags: *"Krete holds the break. He only gives it up on the mic."*<br>`bomb`: Portals paints a huge piece over their tags. It looks amazing, but it disrespects the Kings | In `station`, the Kings refuse the rap battle if `tag_choice = bomb` |

The choice is final: once it's made, the other option is gone.

## Scenes

**1. `hq` — The Basement (start)**
The crate is empty, and there's a Concrete Kings sticker on the turntable. Needle is furious.
- Take MC Bible's rhyme book → collects `rhyme_book` (only while it's still on the couch)
- Go to Rico's Record Shop → `record_shop`
- Hit the block → `block`

**2. `record_shop` — Rico's Record Shop**
Rico says the Kings were asking about the abandoned 149th St station. His cousin used to work for the MTA, and there's an old key in the drawer.
- Take the service key → collects `service_key` (only while it's still in the drawer)
- Back to the block → `block`

**3. `block` — The Handball Court**
A wall full of fresh Concrete Kings tags. Portals studies them.
- Portals reads the tags → `tag_choice = read` (only while undecided)
- Portals bombs over their tags → `tag_choice = bomb` (only while undecided)
- Enter the abandoned station → `station` **(locked: requires `service_key`)**
- Back to the Basement → `hq`
- Head to Disco Fever → `battle`

**4. `station` — Abandoned 149th St Station (the Kings' hideout)**
King Krete is sitting on a crate with "Dor e Dor" under his arm.
- If `tag_choice = bomb`: *"You burned our wall? No battle. Get out."* The rap battle isn't offered.
- Challenge Krete to a rap battle (round 1): Meyhem raps so fast that Krete stumbles. This is only text, nothing changes yet.
- Round 2 – MC Bible finishes him → collects `vinyl` (requires `rhyme_book`)
  - Without the rhyme book it's rejected with *"Bible's best verses are in his rhyme book back at the basement."*
- Back to the block → `block`

**5. `battle` — Disco Fever, battle night**
The Concrete Kings are on the decks. Fantastic Needle steps up.
- Start the battle → ending depends on `vinyl`

## Endings (PT05)

- **`ending_legends` — Legends of the Bronx** (has `vinyl`): Needle cuts in "Dor e Dor", and Reekz goes down to the real break. Bible and Meyhem tear up the mic, and Portals' backdrop pulls the whole room into another dimension. The crown is yours.
- **`ending_static` — Lost in the Static** (no `vinyl`): Needle plays the usual records and Reekz stays standing, because that's no real break. The crowd shrugs and the Concrete Kings take the crown.

Once an ending is reached, story actions stop. The player can only review the ending or start a new game.

## Paths (PT R4: both endings reachable from a new game)

- **Win:** hq (take rhyme book) → record_shop (take key) → block (read tags) → station (rap battle, rounds 1 + 2) → block → battle
- **Lose:** hq → block (bomb tags) → battle
