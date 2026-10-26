# The Missing Break — story content

South Bronx, summer 1977. Two days before the borough DJ battle at Disco Fever, the Sopranos Family break into the basement of the **GoodFellas** crew and steal their secret weapon: the record **Lyn Collins – "Think About It"**. DJ Fantastic Needle saved this unheard break for the final: it's his secret joint. Without it, the crew can't win.

## The crew (GoodFellas) and their part in the story

| Member | Element | Hook | What they do in the game |
|---|---|---|---|
| Fantastic Needle | DJ | On point like a needle | Drops "Think About It" in the final battle and wins it |
| MC Bible | MC | Never runs out of verses, the lyrical genius | Wins the rap battle against King Krete, but only with his rhyme book (without it he chokes) |
| Portals | Graffiti | His pieces take you to another dimension | Reads the Sopranos' tags (the right choice) or paints over them (the wrong choice) |
| Reekz | B-boy | Only goes down to the real breaks | Only goes down when Needle drops the real break, and the crowd goes wild |

**Rival crew:** the Sopranos Family, with their MC, King Krete.

## Items (PT03, PT R2)

| ID | Item | Where | Unlocks |
|---|---|---|---|
| `rhyme_book` | MC Bible's rhyme book | On the couch in `hq` | Bible's turn in the rap battle |
| `service_key` | Old MTA service key | Drawer behind Rico's counter (`record_shop`) | Opening the gate from `gate` → `station` |
| `vinyl` | Lyn Collins – "Think About It" | Prize for winning the rap battle (`station`) | The winning ending |

Each item can be collected once and is not used up.

## Decision (PT04)

| ID | Where | Options | Effect later |
|---|---|---|---|
| `tag_choice` | `block` | `read`: Portals decodes the Sopranos' tags: *"Krete holds the break. He only gives it up on the mic."*<br>`bomb`: Portals paints a huge piece over their tags. It looks amazing, but it disrespects the Sopranos | In `station`, the Sopranos refuse the rap battle if `tag_choice = bomb` |

The choice is final: once it's made, the other option is gone.

## Scenes

Between the places the crew walks (`assets/walks/`). They come out of the door of the place they leave and go in through the door of the place they get to, one after the other: Reekz first, then Needle, Portals and Bible. At Rico's door and the open station gate the player clicks the door, and the crew walks in (into the station: down the stairs). Coming up out of the station with the record won back, Needle holds it up high: *WE GOT IT BACK!*

**1. `hq` — The Basement (start)**
The crate is empty, and the Sopranos Family crossed out the GoodFellas piece on the wall (you can still read GOODFELLAS underneath). Needle is furious.

The crew talks (speech bubbles in the picture):
> **Needle:** Who took my secret joint?!
> **MC Bible:** What happened, Needle?
> **Needle:** Yo! That shit is crazy, dawg. The crate is empty!
> **Reekz:** Look at the wall! The Sopranos crossed out our name!
> **Portals:** They went over our piece. That's disrespectful, son!
> **Needle:** They took "Think About It", my secret break for the final!
> **Reekz:** No break. No battle. We gotta get it back!
> **MC Bible:** First I need my rhyme book to write a diss for Krete. It's on the couch.
> **Portals:** Rico hears everything. Let's hit the record shop!

- Take MC Bible's rhyme book → collects `rhyme_book` (only while it's still on the couch)
- Hit the block → `block` (the only way out: the block leads everywhere else)

**2. `record_shop` — Rico's Record Shop**
The crew walks there from HQ and enters the shop. Rico talks to them (speech bubbles in the picture):
> **Rico:** Yo, GoodFellas! Why the long faces?
> **Needle:** The Sopranos stole my secret joint, Rico.
> **Rico:** The Sopranos were in here yesterday, asking about the old 149th St station.
> **Portals:** The abandoned one? That's been chained up for years.
> **Rico:** My cousin used to work for the MTA. His old service key is in my drawer.
> **Reekz:** That key gets us into the station!
> **Rico:** Take it, and go get that record back!

Rico says the Sopranos were asking about the abandoned 149th St station. His cousin used to work for the MTA, and there's an old key in the drawer.
- Take the service key → collects `service_key` (only while it's still in the drawer)
- Back to the block → `block`

**3. `block` — The Basketball Court**
A wall full of fresh Sopranos Family tags. Portals studies them.

The crew talks (speech bubbles in the picture):
> **Portals:** Look at all these fresh tags. The Sopranos were here last night.
> **Needle:** And their tags all lead one way: the old 149th St station.
> **Portals:** That's where the Sopranos are hiding out!
> **MC Bible:** But the gate is chained up. Only an MTA key opens it.
> **Reekz:** Then we get that key and take back our break!
- Portals reads the tags → `tag_choice = read` (only while undecided)
- Portals bombs over their tags → `tag_choice = bomb` (only while undecided)
- Enter the abandoned station → `station` **(locked: requires `service_key`)**
- Back to the Basement → `hq`
- Go to Rico's Record Shop → `record_shop` (the crew walks down the block, then enters the shop)
- Head to Disco Fever → `battle` (the crew walks up to the club at night; the bouncer lifts the velvet rope: *"GoodFellas! Go on in."*)
- The corner store → `corner_store` (along the court wall, in through the bodega's door)

**4. `station` — Abandoned 149th St Station (the Sopranos' hideout)**
King Krete is sitting on a crate with "Think About It" under his arm.

The crew talks with Krete (speech bubbles in the picture):
> **King Krete:** Well, well... the GoodFellas. Lost something?
> **Needle:** That's my record, Krete. Give it back.
> **King Krete:** This? "Think About It"? Finders keepers.
> **Portals:** You broke into our HQ and went over our piece.
> **King Krete:** You want it back? Then take it on the mic.
> **MC Bible:** A rap battle? Bet.
- If `tag_choice = bomb`: *"You burned our wall? No battle. Get out."* The rap battle isn't offered.
- **Rap battle** (click Bible or the mic): MC Bible steps up to the mic alone, with or without his rhyme book (nobody reminds the player of it here).
  - With his `rhyme_book`: his verses finish Krete → collects `vinyl` (remembered: `rap_battle = won`).
  - Without it: he chokes, forgets his bars, the crowd boos him off: game over (`ending_lost_battle`).
- Back to the block → `block`

**5. `battle` — Disco Fever, battle night**
The Sopranos Family are on the decks. Fantastic Needle steps up.

The crew talks (speech bubbles in the picture):
> **The host:** Disco Fever! The borough final! The Sopranos Family versus the GoodFellas!
> **King Krete:** You really think you can beat the Sopranos, Needle?
> **Needle:** Step aside, Krete. These are my decks now.
> **Reekz:** When the real break drops, I'm going down.
- Start the battle → ending depends on `vinyl`

## Endings (PT05)

- **`ending_legends` — Legends of the Bronx** (has `vinyl`): Needle cuts in "Think About It", and Reekz goes down to the real break. Bible tears up the mic, and Portals' backdrop pulls the whole room into another dimension. The crown is yours.
- **`ending_static` — Lost in the Static** (no `vinyl`): Needle plays the usual records and Reekz stays standing, because that's no real break. The crowd shrugs and the Sopranos Family take the crown.

Once an ending is reached, story actions stop. The player can only review the ending or start a new game.

## Paths (PT R4: both endings reachable from a new game)

- **Win:** hq (take rhyme book) → block → record_shop (take key) → block (read tags) → gate (open it) → station (rap battle: Bible wins the record) → block → hq (tries to practice: can't) → flash (through Portals' portal: "the secret lies in the crayon") → hq → block (win the cypher: $10) → corner_store (buy crayons) → block → hq (mark the break, practice it) → block → battle
- **Lose:** hq → block (bomb tags) → battle
- **`ending_lost_battle` — Krete Keeps the Crown** (game over, the rap battle is lost: Bible choked without his rhyme book): Krete keeps the record. RESTART starts the game again from the beginning.
- **Plot twist: practice first.** Winning "Think About It" back isn't enough. Before Disco Fever the crew has to go back to the basement, where Needle goes behind the decks and practices the break (PRACTICE THE BREAK, once the record is back): the minigame *Keep the break going*, spinning the break back from one copy of the record to the other, three clean switches in a row, each harder than the one before (only then remembered and saved). With the record but without practice, the DJ battle ends in **`ending_out_of_practice` — Out of Practice**: Needle's cuts are off, the break skips, the crowd walks off and the Sopranos Family take the crown. Hint: when Bible wins the record, *"Needle hasn't touched it in days..."*
- **Grandmaster Flash and the crayon.** With the record back, Needle tries to practice in the basement (PRACTICE THE BREAK) and can't catch the break: *"Only one man can help me now: Grandmaster Flash."* Portals sprays a portal on the wall of his graffiti corner (◎ PORTAL TO FLASH), and the crew steps through into Flash's realm (`flash`): a starry nebula, a giant record turning as the floor, records floating in orbit, the guru in a golden halo behind his floating decks. His advice: *"Stop listening. Look. The secret lies in the crayon. Mark where the break starts over."* From then on the **b-boy cypher** shows up on the block: winning it pays **$10** (each time Reekz wins). The **corner store** (`corner_store`) is always open, but without money nothing can be bought: crayons $1.00, chips 50¢, soda 25¢, candy 10¢. With crayons, PRACTICE THE BREAK in the basement: Needle marks the break with the crayon (MARK right when the drum loop starts over, three marks), then keeps the break going (three clean switches): practiced.
