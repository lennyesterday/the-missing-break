# Fourth feature: the crew's backpack

## Why

The inventory sat in Streamlit's sidebar, outside the game. The player should open it inside the picture, the way games usually do it: a backpack to click.

## What

- Every scene picture and every walk has a **🎒 backpack button** top right, right next to the 🔊 switch and the same size. A small badge on it shows how many things the crew carries (no badge when it's empty).
- Clicking it opens the **backpack** over the picture: a dark panel with a graffiti "BACKPACK" title, every item the crew carries (an icon and its name from `logic.ITEMS`, in the order they were picked up), "EMPTY. NOTHING IN HERE YET." when there is nothing, and the crew's cash (`$0.00`).
- ✕, a click next to the panel, Escape or the 🎒 button again close it. It also closes when the picture changes (a new scene or walk).
- Looking into the backpack is not a move: it is drawn by the picture itself (no reload), nothing changes, nothing is saved.
- The sidebar with the inventory is gone.
- The app hands the picture `backpack = {"items": [{"id", "name", "icon"}], "cash": "$x.xx"}`; screens without the backpack (home, intro, endings, the rhyme book, the turntable, the minigames) get `None`.

## Out of scope

- Using or combining items from the backpack.

## Done when

1. The scene pictures and walks get the backpack with the carried items, in order, and the cash.
2. An empty backpack has no items; after taking an item it is in the backpack.
3. Screens outside the scenes (home, intro) get no backpack.
4. The sidebar shows no inventory any more.
5. Opening the backpack saves nothing.
