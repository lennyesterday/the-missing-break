# AGENTS.md — The Missing Break

A Plot Twist text-adventure game (see `docs/product-brief.md`). The story content is in `docs/story.md`.

## Stack
Python, Streamlit, SQLite, pytest, managed with uv.

## Commands
- Install: `uv sync`
- Run the app: `uv run streamlit run app.py`
- Run the tests: `uv run pytest`

## Structure
- `app.py`: Streamlit screens only, no game rules
- `logic.py`: game rules (scenes, items, conditions, actions). Pure functions, no Streamlit, no DB
- `db.py`: SQLite storage (load/save progress)
- `art/`: scripts that draw the pictures (`build.py` for scenes/screens, `crew.py` for the figures); rebuild with `uv run python -m art.build`. Generated sounds: `ambience.py` (background sounds), `off_break.py` (Needle's off-beat try, `think_about_it_off.wav`)
- `assets/`: the generated SVGs (don't edit by hand; change `art/` and rebuild)
- `static/audio/`: music, sounds and voices; credits in `static/audio/CREDITS.md`
- `static/audio/voices/<scene>/<NN>_<speaker>.mp3`: a spoken line (NN = its place in the conversation, from 00; the speaker must match). Subfolders `back/` (coming back), `after/` (right after being turned down), `locked/` (when turned down), `won/` (the block, back from the station with the record), `stuck/` (the basement, after Needle can't loop the break). A line said during a walk (`logic.WALK_LINES`) goes in `static/audio/voices/walks/<walk>/` and plays when its bubble shows. Lines without a file stay silent.
- `tests/`: pytest tests
- `docs/`: product brief and story content
- `specs/`: task specs (one per feature)

## Story
- The crew (GoodFellas) is four: Fantastic Needle (DJ), MC Bible (MC), Portals (graffiti), Reekz (b-boy). MC Meyhem was removed (`specs/remove-meyhem.md`); don't bring him back.
- The rap battle is MC Bible alone; he joins with or without his rhyme book (and doesn't mention it): with it he wins the record, without it he chokes (game over, RESTART).
- Back in the basement with the record (`specs/battle-preparation.md`): clicking Needle's turntables plays his try (about 15 s, always off), then the crew decides to find Grandmaster Flash; clicking Portals' spray cans opens the portal. No graffiti buttons for these: they're things in the picture.

## Rules
- Work on a feature branch (e.g. `first-feature`), never directly on `main`.
- Work only on the current spec in `specs/`.
- Tests come first. Once reviewed, don't weaken, skip, or delete them to get green. If a test is wrong, fix it explicitly against the BRD and say so.
- Rejected actions must not change the state or the saved data.
- Save progress after every accepted action.
- Never commit `*.db` files, `.env`, or secrets.
- When you're done: run `uv run pytest`, show the output, list the changed files, and explain how to check the feature manually in the app (including stopping and restarting it).
