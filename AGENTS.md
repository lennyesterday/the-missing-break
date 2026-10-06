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
- `tests/`: pytest tests
- `docs/`: product brief and story content
- `specs/`: task specs (one per feature)

## Rules
- Work on a feature branch (e.g. `first-feature`), never directly on `main`.
- Work only on the current spec in `specs/`.
- Tests come first. Once reviewed, don't weaken, skip, or delete them to get green. If a test is wrong, fix it explicitly against the BRD and say so.
- Rejected actions must not change the state or the saved data.
- Save progress after every accepted action.
- Never commit `*.db` files, `.env`, or secrets.
- When you're done: run `uv run pytest`, show the output, list the changed files, and explain how to check the feature manually in the app (including stopping and restarting it).
