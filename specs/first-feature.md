# First feature: get the service key, open the station, resume

## Why

The player should be able to grab the MTA service key at Rico's, use it to get into the abandoned station, and leave and come back later without losing progress.

## What

- Show the start scene `hq`. From there the player can reach `record_shop` and `block`.
  - **Changed later (by the product owner):** the basement only leads to `block`; the block leads everywhere else, including `record_shop`. The checks below still hold, with Rico's reached via the block.
- In `record_shop`, the player can take `service_key` from the drawer. It can be collected only once (PT03, PT R2). After that, the scene no longer offers it (PT R3).
- In `block`, "Walk to the 149th St station" leads to `gate` (outside the station); there, "Open the gate" leads to `station`. (Changed: the gate used to be on the block.)
  - **Without `service_key`:** the action is rejected with the message *"The gate is chained shut. You need a key."* The current scene and inventory stay unchanged (PT R1, A1).
  - **With `service_key`:** the player moves to `station`, and `service_key` stays in the inventory (A2).
- The player can look at their inventory at any time.
- After every accepted action, `current_scene` and `inventory` are saved to SQLite. Rejected actions write nothing.
- On startup with an existing save, "Resume" is offered and restores the scene and inventory (PT01, A4).

Implements parts of PT01–PT03, PT R1–R3, and A1–A4.

## Out of scope

The rhyme book, the vinyl, the rap battle, the tag decision (`tag_choice`), `battle`, the endings, the restart confirmation (A6), and any artwork or styling. These belong to later tasks.

## Done when

1. **Rejected (A1):** New game → `hq` → `block` → `gate` → "Open the gate". The message is shown, the scene is still `gate`, the inventory is `[]`, and the saved data is unchanged.
2. **Collect once (A3):** `record_shop` → take the key. The inventory is `["service_key"]`. Taking it again is not offered or is rejected, and the inventory still holds exactly one `service_key`.
3. **Accepted (A2):** With the key, `block` → `gate` → "Open the gate". The scene is `station` and the inventory is still `["service_key"]`.
4. **Restart (A4):** Take the key, go to `block`, stop the app (Ctrl+C) and start it again. Resume restores `block` and `["service_key"]`, the station route is open, and `record_shop` does not offer the key again.
