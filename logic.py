"""Game rules: scenes, items, conditions, actions. Pure functions, no Streamlit, no DB."""

from dataclasses import dataclass, field

START_SCENE = "hq"
LOCKED_STATION_MESSAGE = "The gate is chained shut. You need a key."
GAME_OVER_MESSAGE = "The battle is over. Start a new game to play again."
CRAYON_MESSAGE = "Flash said the secret lies in the crayon. The corner store sells crayons."
NO_MONEY_MESSAGE = "You don't have enough money. The b-boy cypher out on the block pays the winner."
CHOKED_MESSAGE = ("Without his rhyme book Bible chokes: he forgets his bars, and the crowd boos him off the mic. "
                  'Krete keeps "Think About It". The rap battle is lost.')

ITEMS = {
    "rhyme_book": "MC Bible's rhyme book",
    "service_key": "Old MTA service key",
    "vinyl": 'Lyn Collins – "Think About It"',
    "crayons": "A box of crayons",
    "chips": "A bag of chips",
    "soda": "A cold soda",
    "candy": "Candy",
}

# Songs that can be played in the game (files in static/, see static/audio/CREDITS.md).
SONGS = {
    "mc_bible_verse": {"title": "MC Bible – Rap Verse", "file": "audio/mc_bible_verse.mp3"},
    "mc_bible_chokes": {"title": "MC Bible chokes", "file": "audio/mc_bible_chokes.mp3"},  # made with Suno
    "apache": {"title": "Apache", "file": "audio/records/apache.mp3"},
    "funky_drummer": {"title": "Funky Drummer", "file": "audio/records/funky_drummer.mp3"},
    "its_just_begun": {"title": "It's Just Begun", "file": "audio/records/its_just_begun.mp3"},
    "impeach_the_president": {"title": "Impeach the President", "file": "audio/records/impeach_the_president.mp3"},
    "vitamin_c": {"title": "Vitamin C", "file": "audio/records/vitamin_c.mp3"},
    "the_mexican": {"title": "The Mexican", "file": "audio/records/the_mexican.mp3"},
    "think_about_it": {"title": "Think (About It)", "file": "audio/records/think_about_it.mp3"},
    # the drum break of it, on a loop: what Needle practices to behind the decks. It starts right
    # on the first drum hit and is 8 times its 2-bar loop (loop_secs, about 114 BPM) long, so it
    # wraps around right on a loop boundary.
    "think_about_it_break": {"title": "Think (About It) – drum break", "file": "audio/records/think_about_it_break.wav",
                             "loop": True, "loop_secs": 4.199},
    # Needle's first try at looping it: always off (cut too early or too late, spun back), then the
    # record stops. Made from the drum break (art/off_break.py); played once, about 15 s.
    "think_about_it_off": {"title": "Think (About It) – the break, always off", "file": "audio/records/think_about_it_off.wav"},
    # background sounds and music (loop while their screen is shown; volume 0..1)
    # the other places' background sounds, made like the basement's (art/ambience.py)
    "street_ambience": {"title": "The street (footsteps, cars, the el train, a siren far off)",
                        "file": "audio/ambience/street.wav", "volume": 0.4},
    "station_gate_ambience": {"title": "Outside the old station (the street, a train rumbling underground, wind up the stairs)",
                              "file": "audio/ambience/station_gate.wav", "volume": 0.4},
    "block_ambience": {"title": "The block (the street, cars passing)",
                       "file": "audio/ambience/block.wav", "volume": 0.45},
    "record_shop_ambience": {"title": "Rico's (a funky groove, vinyl crackle, flipping records, the register)",
                             "file": "audio/ambience/record_shop.wav", "volume": 0.45},
    "corner_store_ambience": {"title": "The corner store (the fridge, the lights, the door bell, the register)",
                              "file": "audio/ambience/corner_store.wav", "volume": 0.4},
    "flash_ambience": {"title": "Grandmaster Flash's realm (a cosmic pad, sparkles, a slow break far away)",
                       "file": "audio/ambience/flash.wav", "volume": 0.5},
    "basement_ambience": {"title": "The basement (hum, a muffled beat, dripping, street, trains)",
                          "file": "audio/ambience/basement.wav", "volume": 0.45},
    "dont_sweat_the_technique": {"title": "Don't Sweat the Technique", "file": "audio/music/dont_sweat_the_technique.mp3",
                                 "volume": 0.7},
}

# The music on the home screen and through the story intro.
INTRO_MUSIC = "dont_sweat_the_technique"
# whose recording plays when he raps (Bible without his rhyme book: he chokes)
RAPPERS = {"bible": "mc_bible_verse", "bible_chokes": "mc_bible_chokes"}
# Bible at the mic without his rhyme book: he chokes, forgets his bars, the crowd boos. Lost for good.
BIBLE_CHOKES = {"battle": "lost", "ending": "ending_lost_battle", "raps": ["bible_chokes"], "done": "bible_chokes",
                "message": CHOKED_MESSAGE}

# The classic breaks lying on the basement floor. Needle can put them on the turntable (only for
# show: it changes nothing in the game). "song" connects a record to a sound file later.
RECORDS = {
    "apache": {"title": "Apache", "artist": "Incredible Bongo Band", "year": 1973, "song": "apache"},
    "funky_drummer": {"title": "Funky Drummer", "artist": "James Brown", "year": 1970, "song": "funky_drummer"},
    "its_just_begun": {"title": "It's Just Begun", "artist": "Jimmy Castor Bunch", "year": 1972, "song": "its_just_begun"},
    "impeach_the_president": {"title": "Impeach the President", "artist": "The Honey Drippers", "year": 1973,
                              "song": "impeach_the_president"},
    "vitamin_c": {"title": "Vitamin C", "artist": "CAN", "year": 1972, "song": "vitamin_c"},
    "the_mexican": {"title": "The Mexican", "artist": "Babe Ruth", "year": 1972, "song": "the_mexican"},
    # Needle's secret joint: playable only once the crew has won it back from King Krete
    "think_about_it": {"title": "Think (About It)", "artist": "Lyn Collins", "year": 1972, "song": "think_about_it",
                       "requires": "vinyl"},
}

# MC Bible's verse, handwritten in his rhyme book (the player can read it in the basement).
RHYME_BOOK_VERSE = [
    "Book of Bible, chapter one, verse one:",
    "Thou shalt not steal from the GoodFellas, son.",
    "King Krete? More like cracked concrete,",
    "One verse from the Bible and you crumble in the street.",
    "My pen writes gospel, your pen writes lies,",
    "You got the ten commandments? I got ten more rhymes.",
    "Sitting on a crate like you're king of the scene,",
    "But you're just a crate digger who never dug what it means.",
    "You crossed out our name, put an X on our wall,",
    "Thanks for the map: X marks where you fall.",
    "I got Old and New Testament, chapter and verse,",
    "You got stolen records, a crown and a curse.",
    "You stole Think About It, but you never could think,",
    "You got the record but you're missing the link.",
    "You turned the page when you came for our crate,",
    "Now I'm closing the book and I'm sealing your fate.",
]

# The two endings (PT05): which one depends on whether the crew won the record back.
ENDINGS = {
    "ending_legends": {
        "title": "Legends of the Bronx",
        "text": ('Needle cuts in "Think About It", and Reekz goes down to the real break. Bible tears '
                 "up the mic, and Portals' backdrop pulls the whole room into another dimension. "
                 "The crown is yours."),
    },
    "ending_lost_battle": {
        "title": "Krete Keeps the Crown",
        "text": ('Game over: the rap battle is lost and Krete keeps "Think About It". Without the record '
                 "there's no break for the final. Start again from the beginning."),
    },
    "ending_out_of_practice": {
        "title": "Out of Practice",
        "text": ('Needle has "Think About It" back, but he hasn\'t touched it in days. His cuts are off, the '
                 "break skips, the crowd walks off the floor and the Sopranos Family take the crown. He should "
                 "have gone back to the basement to practice first."),
    },
    "ending_static": {
        "title": "Lost in the Static",
        "text": ("Needle plays the usual records and Reekz stays standing, because that's no real break. "
                 "The crowd shrugs and the Sopranos Family take the crown."),
    },
}

# What the crew says during a walk (between two places): the walk ("<from>__<to>"), then (who,
# the line, when: seconds into the walk). Shown as a bubble then, and spoken then.
WALK_LINES = {
    "hq__flash": [("reekz", "YOU DID IT!", 2.7)],  # Portals' portal is open
}

# Story content (docs/story.md).
SCENES = {
    "hq": {
        "title": "The Basement",
        "text": (
            "The crate is empty, and the Sopranos Family crossed out the GoodFellas piece on the wall. "
            "Needle is furious."
        ),
        "actions": [
            {
                "id": "take_rhyme_book",
                "label": "Take MC Bible's rhyme book",
                "collects": "rhyme_book",
                "message": "Bible grabs his rhyme book from the couch.",
            },
            # the plot twist: with the record back, Needle has to practice the break here before
            # Disco Fever. First he tries and can't catch the break: he needs Grandmaster Flash.
            # (Clicking his turntables: the app plays the try out first, then this is taken.)
            {
                "id": "try_practice",
                "label": "Practice the break",
                "when_has": "vinyl",
                "unless_flag": "stuck",
                "sets": "stuck",
                "message": ('Needle runs the record again and again, but he can\'t catch the break: it keeps slipping away. '
                            '"Only one man can help me now: Grandmaster Flash."'),
            },
            # Portals sprays a portal on the wall of his corner: through it to Grandmaster Flash
            # (clicking his spray cans)
            {"id": "go_flash", "label": "Portals opens a portal to Grandmaster Flash", "when_flag": "stuck",
             "target": "flash", "sets": "met_flash"},
            # After Flash, with crayons, he practices for real (once). The app plays it out first: he
            # marks the break with the crayon and has to keep the break going (the minigames); only
            # then is this action taken.
            {
                "id": "practice",
                "label": "Practice the break",
                "when_has": "vinyl",
                "when_flag": "met_flash",
                "requires": "crayons",
                "locked_message": CRAYON_MESSAGE,
                "practices": True,
                "message": "Needle runs the break again and again until it's back in his hands. Now the crew is ready for Disco Fever.",
            },
            {"id": "go_block", "label": "Hit the block", "target": "block"},
        ],
        # What the crew says when they find the basement turned over (shown as speech bubbles).
        "dialogue": [
            ("needle", "WHO TOOK MY SECRET JOINT?!"),
            ("bible", "WHAT HAPPENED, NEEDLE?"),
            ("needle", "YO! THAT SHIT IS CRAZY, DAWG. THE CRATE IS EMPTY!"),
            ("reekz", "LOOK AT THE WALL! THE SOPRANOS CROSSED OUT OUR NAME!"),
            ("portals", "THEY WENT OVER OUR PIECE. THAT'S DISRESPECTFUL, SON!"),
            ("needle", 'THEY TOOK "THINK ABOUT IT", MY SECRET BREAK FOR THE FINAL!'),
            ("reekz", "NO BREAK. NO BATTLE. WE GOTTA GET IT BACK!"),
            ("bible", "FIRST I NEED MY RHYME BOOK TO WRITE A DISS FOR KRETE. IT'S ON THE COUCH."),
            ("portals", "RICO HEARS EVERYTHING. LET'S HIT THE RECORD SHOP!"),
        ],
        # What the crew says when it comes back (the first conversation doesn't come back): until
        # it has Rico's key, a reminder to go to Rico's; with the key, nothing.
        "dialogue_back": {
            "unless_has": "service_key",
            "lines": [
                ("needle", "WE'RE BACK HERE? MY RECORD AIN'T GONNA FIND ITSELF!"),
                ("bible", "WE REALLY SHOULD GO TO RICO'S AND ASK HIM ABOUT THE SOPRANOS."),
            ],
        },
        # What the crew says once Needle has tried the break and can't loop it, until they've met
        # Flash (once while the game runs; again after a restart, as a reminder).
        "dialogue_stuck": {
            "when_flag": "stuck",
            "unless_flag": "met_flash",
            "lines": [
                ("bible", "THAT TAKES TOO LONG. WE'LL NEVER MAKE IT IN TIME FOR THE BATTLE!"),
                ("needle", "THERE'S ONLY ONE MAN WHO CAN HELP US LOOP THE BREAK."),
                ("reekz", "AND WHO'S THAT?"),
                ("needle", "THE GRANDMASTER: GRANDMASTER FLASH."),
                ("portals", "DOES HE EVEN EXIST? I THOUGHT HE WAS A LEGEND."),
                ("bible", "IF WE CAN FIND HIM, YOU MUST SPRAY A PORTAL!"),
            ],
        },
        # The background sound while the basement is shown (fades out when a record goes on).
        "ambience": "basement_ambience",
        # The classics on the floor that Needle can put on (see RECORDS).
        "records": ["apache", "funky_drummer", "its_just_begun", "impeach_the_president", "vitamin_c", "the_mexican",
                    "think_about_it"],
        # Things the player can click on to look at. "song" will connect them to a song later.
        "things": {
            "rhyme_book": {
                "name": "MC BIBLE'S RHYME BOOK",
                "text": "Every verse Bible ever wrote is in here. He needs it to finish the rap battle in round 2.",
                "take": "take_rhyme_book",
                "read": True,  # READ IT opens the book (RHYME_BOOK_VERSE); the verse can't be listened to here
            },
            "empty_sleeve": {
                "name": 'LYN COLLINS – "THINK ABOUT IT"',
                "text": "Needle's secret joint. The sleeve is still here, but the record is gone.",
                "song": None,
                "unless": "vinyl",  # once the record is back, the sleeve isn't empty any more
            },
        },
    },
    "record_shop": {
        "title": "Rico's Record Shop",
        "ambience": "record_shop_ambience",
        "text": (
            "Rico says the Sopranos were asking about the abandoned 149th St station. "
            "His cousin used to work for the MTA, and there's an old key in the drawer."
        ),
        # Inside the shop, Rico tells the crew what he knows (speech bubbles, clicked through).
        "dialogue": [
            ("rico", "YO, GOODFELLAS! WHY THE LONG FACES?"),
            ("needle", "THE SOPRANOS STOLE MY SECRET JOINT, RICO."),
            ("rico", "THE SOPRANOS WERE IN HERE YESTERDAY, ASKING ABOUT THE OLD 149TH ST STATION."),
            ("portals", "THE ABANDONED ONE? THAT'S BEEN CHAINED UP FOR YEARS."),
            ("rico", "MY COUSIN USED TO WORK FOR THE MTA. HIS OLD SERVICE KEY IS IN MY DRAWER."),
            ("reekz", "THAT KEY GETS US INTO THE STATION!"),
            ("rico", "TAKE IT, AND GO GET THAT RECORD BACK!"),
        ],
        "actions": [
            {
                "id": "take_service_key",
                "label": "Take the service key",
                "collects": "service_key",
                "message": "You take the old MTA service key from Rico's drawer.",
            },
            {"id": "go_block", "label": "Back to the block", "target": "block"},
        ],
    },
    "block": {
        "title": "The Basketball Court",
        "ambience": "block_ambience",
        "text": "A wall full of fresh Sopranos Family tags. Portals studies them.",
        # Portals reads the Sopranos' tags (speech bubbles, clicked through).
        "dialogue": [
            ("portals", "LOOK AT ALL THESE FRESH TAGS. THE SOPRANOS WERE HERE LAST NIGHT."),
            ("needle", "AND THEIR TAGS ALL LEAD ONE WAY: THE OLD 149TH ST STATION."),
            ("portals", "THAT'S WHERE THE SOPRANOS ARE HIDING OUT!"),
            ("bible", "BUT THE GATE IS CHAINED UP. ONLY AN MTA KEY OPENS IT."),
            ("reekz", "THEN WE GET THAT KEY AND TAKE BACK OUR BREAK!"),
        ],
        # Coming back (the first conversation doesn't come back): with Rico's key, and until the
        # record is won back, the crew heads for the station; otherwise it stays quiet.
        "dialogue_back": {
            "when_has": "service_key",
            "unless_has": "vinyl",
            "lines": [
                ("portals", "WE GOT RICO'S KEY! THAT GATE AIN'T STOPPING US NOW."),
                ("needle", "NOW WE CAN WALK UP TO THE STATION. LET'S GET MY RECORD BACK!"),
            ],
        },
        # Right after something was turned down elsewhere (by its action id): what the crew says on
        # arriving here, e.g. back from the gate they couldn't open.
        "dialogue_after": {
            "enter_station": [("bible", "REEKZ WAS RIGHT. LET'S GET THAT KEY FROM RICO'S!")],
        },
        # Coming from the station with the record won back: they celebrate Bible, and Needle says
        # what's next (specs/battle-preparation.md).
        "dialogue_won": {
            "from": "station",
            "when_has": "vinyl",
            "lines": [
                ("reekz", "BIBLE, YOU KILLED THAT ONE!"),
                ("bible", "THEY CALL ME BIBLE 'CAUSE I NEVER RUN OUT OF VERSES."),
                ("needle", "NOW THAT WE GOT MY RECORD BACK, WE'RE READY FOR THE DJ BATTLE. WE JUST NEED TO PRACTICE."),
            ],
        },
        # Just for fun: click the ball and pick a shot (nothing changes, nothing is saved).
        "things": {
            "basketball": {
                "name": "THE BASKETBALL",
                "text": "Somebody left it on the court. Shoot some hoops?",
                "shots": {"dunk": "DUNK", "three": "3-POINTER"},
            },
            "cypher": {
                "when_flag": "met_flash",  # it only shows up after Needle has been to Grandmaster Flash
                "name": "THE CYPHER",
                "text": "A breaking crew from the block, cyphering in front of the corner store. Reekz is itching to get in.",
                "join": True,  # JOIN IN: close up on the cypher, Reekz breaks (only for show)
            },
        },
        "actions": [
            {"id": "go_gate", "label": "Walk to the 149th St station", "target": "gate"},
            {"id": "go_store", "label": "Into the corner store", "target": "corner_store"},
            # the cypher pays $10 to the winner (as often as Reekz wins it); the app gives it after a won battle
            {"id": "win_cypher", "label": "Win the cypher", "by_app": True, "when_flag": "met_flash", "gives_money": 1000,
             "message": "The crowd's hat goes round for Reekz: $10 for the crew!"},
            {"id": "go_hq", "label": "Back to the Basement", "target": "hq"},
            {"id": "go_record_shop", "label": "Go to Rico's Record Shop", "target": "record_shop"},
            {"id": "go_battle", "label": "Head to Disco Fever", "target": "battle"},
        ],
    },
    # Grandmaster Flash's realm, through Portals' portal: the guru of the wheels of steel.
    "flash": {
        "title": "Grandmaster Flash",
        "ambience": "flash_ambience",
        "text": "Somewhere between the stars and the grooves, Grandmaster Flash is spinning.",
        "dialogue": [
            ("needle", "GRANDMASTER FLASH! I CAN'T CATCH THE BREAK. IT KEEPS SLIPPING AWAY."),
            ("flash", "YOU'RE LISTENING FOR THE BREAK, YOUNG BLOOD. STOP LISTENING. LOOK."),
            ("flash", "THE SECRET LIES IN THE CRAYON."),
            ("needle", "THE CRAYON?"),
            ("flash", "MARK WHERE THE BREAK STARTS OVER. THEN THE RECORD TELLS YOU WHEN."),
            ("portals", "THE CORNER STORE SELLS CRAYONS. BUT WE'RE BROKE..."),
            ("reekz", "THEN I'LL BREAK FOR IT. THAT CYPHER ON THE BLOCK PAYS!"),
        ],
        "actions": [
            {"id": "go_hq", "label": "Back through the portal", "target": "hq"},
        ],
    },
    # The corner store on the block: always open, but nothing to do without money.
    "corner_store": {
        "title": "The Corner Store",
        "ambience": "corner_store_ambience",
        "text": "Chips, soda, candy, a little bit of everything. And crayons.",
        "dialogue": [
            ("clerk", "WHAT'LL IT BE, FELLAS? CASH ONLY."),
        ],
        "actions": [
            {"id": "buy_crayons", "label": "Crayons ($1.00)", "costs": 100, "collects": "crayons",
             "message": "A box of crayons. Needle grins: the secret lies in the crayon."},
            {"id": "buy_chips", "label": "Chips (50¢)", "costs": 50, "collects": "chips",
             "message": "A bag of chips. Reekz crunches on them between his power moves."},
            {"id": "buy_soda", "label": "Soda (25¢)", "costs": 25, "collects": "soda",
             "message": "A cold soda. Reekz drinks it in one go: \"Now I could break all night.\""},
            {"id": "buy_candy", "label": "Candy (10¢)", "costs": 10, "collects": "candy",
             "message": "Candy for the crew. Portals keeps the wrapper for a sticker."},
            {"id": "go_block", "label": "Back to the block", "target": "block"},
        ],
    },
    # Outside the old station: the crew follows the Sopranos' tags here. The gate is chained:
    # only Rico's MTA key opens it; without it, back to the block (and on to Rico's).
    "gate": {
        "title": "Outside the 149th St Station",
        "ambience": "station_gate_ambience",  # (no footsteps: the crew stands at the gate)
        "text": "The old subway stairs, behind a gate chained shut with a padlock.",
        "actions": [
            {
                "id": "enter_station",
                "label": "Open the gate",
                "target": "station",
                "requires": "service_key",
                "locked_message": LOCKED_STATION_MESSAGE,
                # what the crew says when it's turned down (a speech bubble, nothing changes)
                "locked_says": [("reekz", "WE REALLY SHOULD HAVE TAKEN THE KEY FROM RICO'S!")],
            },
            {"id": "go_block", "label": "Back to the block", "target": "block"},
        ],
    },
    "station": {
        "title": "Abandoned 149th St Station",
        "text": 'King Krete is sitting on a crate with "Think About It" under his arm.',
        # King Krete challenges the crew (speech bubbles, clicked through).
        "dialogue": [
            ("krete", "WELL, WELL... THE GOODFELLAS. LOST SOMETHING?"),
            ("needle", "THAT'S MY RECORD, KRETE. GIVE IT BACK."),
            ("krete", 'THIS? "THINK ABOUT IT"? FINDERS KEEPERS.'),
            ("portals", "YOU BROKE INTO OUR HQ AND WENT OVER OUR PIECE."),
            ("krete", "YOU WANT IT BACK? THEN TAKE IT ON THE MIC."),
            ("bible", "A RAP BATTLE? BET."),
        ],
        "things": {
            "stolen_record": {
                "name": 'LYN COLLINS – "THINK ABOUT IT"',
                "text": "Needle's secret joint, under King Krete's arm. So close.",
                "song": None,
            },
        },
        "actions": [
            # The rap battle: Bible on the mic. "when_battle": how far the battle has to be for it
            # to be offered, "battle": how far it is afterwards, "raps": who raps.
            {
                "id": "rap_battle",
                "label": "Rap battle",
                "when_battle": None,
                "requires": "rhyme_book",
                "without_it": BIBLE_CHOKES,
                "collects": "vinyl",
                "battle": "won",
                "raps": ["bible"],
                "message": 'Bible\'s verses finish Krete. He hands over "Think About It". Needle hasn\'t touched it in days...',
            },
            {"id": "go_block", "label": "Back to the block", "target": "block"},
        ],
    },
    "battle": {
        "title": "Disco Fever, battle night",
        "text": "The Sopranos Family are on the decks. Fantastic Needle steps up.",
        "dialogue": [
            ("host", "DISCO FEVER! THE BOROUGH FINAL! THE SOPRANOS FAMILY VERSUS THE GOODFELLAS!"),
            ("krete", "YOU REALLY THINK YOU CAN BEAT THE SOPRANOS, NEEDLE?"),
            ("needle", "STEP ASIDE, KRETE. THESE ARE MY DECKS NOW."),
            ("reekz", "WHEN THE REAL BREAK DROPS, I'M GOING DOWN."),
        ],
        "actions": [
            {
                "id": "start_battle",
                "label": "Start the battle",
                # the ending depends on whether the crew won the record back, and (the plot twist)
                # whether Needle practiced with it in the basement
                "ends": {"with": "vinyl", "then": "ending_legends", "unpracticed": "ending_out_of_practice",
                         "otherwise": "ending_static"},
            },
        ],
    },
}


@dataclass
class GameState:
    current_scene: str = START_SCENE
    inventory: list[str] = field(default_factory=list)
    ending: str | None = None  # set once the battle is played; then the game is over
    rap_battle: str | None = None  # None, "won" or "lost" (Bible choked)
    practiced: bool = False  # Needle practiced the break in the basement (needed to win at Disco Fever)
    money: int = 0  # the crew's cash, in cents (the cypher pays; the corner store takes it)
    stuck: bool = False  # Needle tried to practice and can't catch the break: he needs Grandmaster Flash
    met_flash: bool = False  # ... and has been to him, through Portals' portal
    left_scenes: list[str] = field(default_factory=list)  # the places the crew has left at least once


@dataclass
class ActionResult:
    accepted: bool
    state: GameState
    message: str = ""


# --- the cypher battle on the block (only for show: nothing here is saved) ---
# Reekz against Kid Cyclone. Each round Kid Cyclone goes first; then the player picks Reekz's
# moves one by one until a freeze ends the set (or CYPHER_SET_MOVES moves). A move scores its
# points, +1 flow when it steps up from the move before (toprock -> footwork -> power -> freeze),
# -2 for the same move twice in a row, -1 for a move shown in an earlier round, and a set without
# a freeze loses 2. "base": the pose the move ends in, which the next move starts from.
CYPHER_MOVES = {
    "toprock": {"label": "TOPROCK", "points": 1, "rank": 0, "base": "stand"},
    "helicopter": {"label": "HELICOPTER", "points": 2, "rank": 1, "base": "helicopter"},  # the coffee grinder
    "headspin": {"label": "HEADSPIN", "points": 3, "rank": 2, "base": "headspin"},
    "nineteen_ninety": {"label": "1990", "points": 3, "rank": 2, "base": "nineteen_ninety"},
    "freeze": {"label": "FREEZE", "points": 2, "rank": 3, "base": "freeze"},
}
# The pose Reekz is in when a move is over ("base"): standing after toprock, otherwise the move's
# own last pose (upside down after the headspin, in the handstand after the 1990, ...). The next
# move goes straight on from there. A freeze ends the set, so nothing starts from it.
CYPHER_BASES = ("stand", "helicopter", "headspin", "nineteen_ninety")
CYPHER_SET_MOVES = 4
CYPHER_ROUNDS = 3
RIVAL = "KID CYCLONE"
RIVAL_SETS = [  # Kid Cyclone's set, round by round
    ["toprock", "helicopter", "freeze"],
    ["toprock", "headspin", "freeze"],
    ["toprock", "helicopter", "nineteen_ninety", "freeze"],
]


def score_set(moves: list[str], earlier: list[str]) -> tuple[int, list[str]]:
    """The crowd's points for a set (never below 0), and why: "flow", "repeat", "seen",
    "finish" (it ends in a freeze) or "no_freeze"."""
    points, notes = 0, []
    for i, move in enumerate(moves):
        points += CYPHER_MOVES[move]["points"]
        if i and CYPHER_MOVES[move]["rank"] > CYPHER_MOVES[moves[i - 1]]["rank"]:
            points, notes = points + 1, notes + ["flow"]
        if i and move == moves[i - 1]:
            points, notes = points - 2, notes + ["repeat"]
        if move in earlier:
            points, notes = points - 1, notes + ["seen"]
    if moves and moves[-1] == "freeze":
        notes.append("finish")
    else:
        points, notes = points - 2, notes + ["no_freeze"]
    return max(points, 0), list(dict.fromkeys(notes))


def set_is_over(moves: list[str]) -> bool:
    return bool(moves) and (moves[-1] == "freeze" or len(moves) >= CYPHER_SET_MOVES)


def cypher_result(rounds: list[tuple[int, int]]) -> str | None:
    """"won" or "lost" once one side has two rounds (a tie goes to Kid Cyclone: it's his block),
    or after the last round; None while it's still open."""
    reekz = sum(1 for a, b in rounds if a > b)
    rival = len(rounds) - reekz
    if reekz >= 2 or (len(rounds) >= CYPHER_ROUNDS and reekz > rival):
        return "won"
    if rival >= 2 or len(rounds) >= CYPHER_ROUNDS:
        return "lost"
    return None


def next_base(move: str) -> str:
    return CYPHER_MOVES[move]["base"]


def cypher_clip(base: str, move: str) -> str:
    """Reekz's clip for this move, starting from the pose he is in (where the last move ended)."""
    return f"assets/cypher/{move}_from_{base}.svg"


def new_game() -> GameState:
    return GameState(current_scene=START_SCENE, inventory=[])


def _copy(state: GameState) -> GameState:
    return GameState(current_scene=state.current_scene, inventory=list(state.inventory), ending=state.ending,
                     rap_battle=state.rap_battle, practiced=state.practiced, money=state.money, stuck=state.stuck,
                     met_flash=state.met_flash, left_scenes=list(state.left_scenes))


def available_actions(state: GameState) -> list[dict]:
    """Actions offered in the current scene. Items already collected are no longer offered.
    Once an ending is reached, story actions stop (PT05)."""
    if state.ending:
        return []
    return [
        action
        for action in SCENES[state.current_scene]["actions"]
        if action.get("collects") not in state.inventory
        and ("when_battle" not in action or action["when_battle"] == state.rap_battle)
        and ("when_has" not in action or action["when_has"] in state.inventory)  # e.g. practice: once the record is back
        and not (action.get("practices") and state.practiced)  # ... and only once
        and ("when_flag" not in action or getattr(state, action["when_flag"]))  # e.g. only after Flash
        and ("unless_flag" not in action or not getattr(state, action["unless_flag"]))
    ]


def conversation(state: GameState, tried: str | None = None, came_from: str | None = None) -> tuple[str, list]:
    """What the crew says in the current place: ("talk", its first conversation), or, coming back to
    a place it has left and that has a "dialogue_back", ("back", those lines), or ("back", []) when
    they don't fit: the crew lacks its "when_has" item or carries its "unless_has" item (e.g. back
    in the basement with Rico's key, or on the block without it).
    tried: the action that was just turned down before the crew came here (e.g. the gate): if the
    place answers it ("dialogue_after"), ("after", those lines).
    came_from: the place the crew has just come from: coming from the "dialogue_won"'s place with
    its "when_has" item (from the station with the record), ("won", those lines).
    A place's "dialogue_stuck" comes while its "when_flag" is set and its "unless_flag" isn't (Needle
    can't loop the break and the crew hasn't met Flash yet): ("stuck", those lines)."""
    scene = SCENES[state.current_scene]
    if tried in scene.get("dialogue_after", {}):
        return "after", scene["dialogue_after"][tried]
    won = scene.get("dialogue_won")
    if won and came_from == won["from"] and won["when_has"] in state.inventory:
        return "won", won["lines"]
    stuck = scene.get("dialogue_stuck")
    if stuck and getattr(state, stuck["when_flag"]) and not getattr(state, stuck["unless_flag"]):
        return "stuck", stuck["lines"]
    back = scene.get("dialogue_back")
    if back and state.current_scene in state.left_scenes:
        fits = (back.get("when_has", None) in (None, *state.inventory)
                and back.get("unless_has") not in state.inventory)
        return "back", back["lines"] if fits else []
    return "talk", scene.get("dialogue", [])


def said_when_turned_down(state: GameState, action_id: str) -> list:
    """What the crew says when this action is turned down here (its "locked_says"), e.g. Reekz at
    the chained gate. Only words: the action still changes nothing."""
    action = next((a for a in SCENES[state.current_scene]["actions"] if a["id"] == action_id), {})
    return action.get("locked_says", [])


def what_happens(state: GameState, action_id: str) -> dict | None:
    """The action as it plays out from this state: without the item it requires, an action can
    turn out differently ("without_it", e.g. Bible chokes without his rhyme book). None if the
    action isn't offered here."""
    if state.ending:
        return None
    action = next((a for a in available_actions(state) if a["id"] == action_id), None)
    if action is None:
        return None
    required = action.get("requires")
    if required and required not in state.inventory and "without_it" in action:
        return {"id": action_id, **action["without_it"]}
    return action


def apply_action(state: GameState, action_id: str) -> ActionResult:
    """Return a new state. A rejected action returns an unchanged copy of the state."""
    if state.ending:
        return ActionResult(False, _copy(state), GAME_OVER_MESSAGE)
    action = what_happens(state, action_id)
    if action is None:
        return ActionResult(False, _copy(state), "You can't do that here.")

    required = action.get("requires")
    if required and required not in state.inventory:
        return ActionResult(False, _copy(state), action["locked_message"])
    if action.get("costs", 0) > state.money:  # the corner store: cash only
        return ActionResult(False, _copy(state), NO_MONEY_MESSAGE)

    new_state = _copy(state)
    new_state.money += action.get("gives_money", 0) - action.get("costs", 0)
    if "sets" in action:  # e.g. Needle is stuck, the crew has met Flash
        setattr(new_state, action["sets"], True)
    if "collects" in action:
        new_state.inventory.append(action["collects"])
    if "battle" in action:
        new_state.rap_battle = action["battle"]
    if "ending" in action:  # e.g. the rap battle is lost: game over, the player has to start again
        new_state.ending = action["ending"]
    if action.get("practices"):
        new_state.practiced = True
    if "target" in action:
        if state.current_scene not in new_state.left_scenes:
            new_state.left_scenes.append(state.current_scene)
        new_state.current_scene = action["target"]
    if "ends" in action:
        rule = action["ends"]
        if rule["with"] not in state.inventory:
            new_state.ending = rule["otherwise"]
        else:  # the plot twist: the record alone isn't enough without practice
            new_state.ending = rule["then"] if state.practiced else rule["unpracticed"]
        return ActionResult(True, new_state, ENDINGS[new_state.ending]["title"])
    return ActionResult(True, new_state, action.get("message", ""))


def home_choice(choice: str, has_save: bool, confirming: bool = False) -> str:
    """What a click on the home screen does.

    Starting over while a save exists must be confirmed first (PT01, A6): while the
    "start over?" sign is up, only its two answers count and the train's buttons wait.
    The menu is not built yet, so it does nothing for now.
    """
    if confirming:
        return {"restart_yes": "new_game", "restart_no": "cancel"}.get(choice, "ignore")
    if choice == "start":
        return "confirm_restart" if has_save else "new_game"
    if choice == "resume" and has_save:
        return "resume"
    return "ignore"
