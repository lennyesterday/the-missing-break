# Twelfth feature: additional scenes — through the doors

## Why

The crew walks between the places, but they never go through a door: the picture cuts when they reach one, and when they leave somewhere they are already out on the street. The player should see them go in and come out, and there should be walks to the two places that have none yet (the corner store and Disco Fever).

## What

- **Coming out:** when the crew leaves a place, they come out of its door one after the other (Reekz first, then Needle, Portals and Bible), the door standing open until the last one is out, and walk on.
- **Going in:** at the end of a walk they walk up to the door and go in one after the other; the door stands open while they go through.
- Per walk:
  - **Basement → block** (`hq__block`): out of the HQ door, down the street, in through the court's gate.
  - **Block → basement** (`block__hq`): out of the court's gate, up the street, in through the HQ door.
  - **Block → Rico's** (`block__record_shop`): they walk up to Rico's door as before. Clicking the door (ENTER RICO'S) now makes them walk in one after the other, then the shop comes up.
  - **Rico's → block** (`record_shop__block`): out of Rico's door, back to the court.
  - **Gate → station** (`gate__station`): the gate opens as before. Clicking the open gate (ENTER THE STATION) makes them walk into the arch and down the stairs, one after the other, then the station comes up.
  - **Station → block** (`station__block`): up the stairs and out of the arch, one after the other. Once they have won "Think About It" back, Needle holds the record up high and the caption says **WE GOT IT BACK!** (otherwise OUT OF THE STATION).
  - **Block → corner store** (`block__corner_store`, new): along the court wall to the bodega, in through its door.
  - **Corner store → block** (`corner_store__block`, new): out of the bodega's door, back along the court wall.
  - **Block → Disco Fever** (`block__battle`, new): a street at night with the club: the neon sign, BOROUGH FINAL TONIGHT on the marquee, a line of people behind a velvet rope, a bouncer at the door. The crew walks up, the bouncer lifts the rope ("GOODFELLAS! GO ON IN."), and they go in one after the other. (There is no way back from Disco Fever, so no walk back.)
- As before: the walks that go on by themselves still do (now once the last one is in, or out); SKIP still goes straight there; the doors that are clicked still are (point and click), only now the crew walks through before the next place comes up.
- In the page: a part that is clicked can play its animation first (`data-plays`: the id of the animation to start) and only then do its action (`data-action-delay`: after so many seconds). A second click doesn't play it again; if the player has moved on in the meantime (SKIP), nothing more happens.
- Nothing about the rules or the saves changes.

## Done when

1. Every walk out of a place starts with the crew coming out of its door, every walk into a place ends with the crew going in through its door.
2. Clicking Rico's door or the open station gate plays the crew going in, then the place comes up.
3. Coming out of the station with the record, Needle holds it up and the caption says WE GOT IT BACK!
4. Going to the corner store and coming back, and going to Disco Fever, show a walk.
5. All earlier tests still pass (same actions, same rules).
