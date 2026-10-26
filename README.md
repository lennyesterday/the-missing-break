# The Missing Break

A hip-hop inspired text adventure built with Python and Streamlit. The game follows a crew through a night in the neighborhood, with choices, music, scenes, and rap battles.

## Get started

Requirements: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run streamlit run app.py
```

Then open the local URL printed by Streamlit (usually `http://localhost:8501`). To stop the app, press `Ctrl+C` in the terminal.

## Project layout

- `app.py` — Streamlit interface and screens
- `logic.py` — game rules and story state transitions
- `db.py` — local SQLite save data
- `art/` — scripts used to build the game's artwork
- `assets/` — scene and interface illustrations
- `static/audio/` and `static/fonts/` — audio, sound effects, and fonts used by the app
- `docs/` — product brief and story
- `specs/` — feature specifications
- `tests/` — automated tests

## Working on the project

1. Create a branch for your change.
2. Install dependencies with `uv sync`.
3. Run the app with `uv run streamlit run app.py`.
4. Run checks with `uv run pytest`.
5. Open a pull request describing the change and how you checked it.

See [CONTRIBUTING.md](CONTRIBUTING.md) for collaboration notes and [static/audio/CREDITS.md](static/audio/CREDITS.md) for audio credits.
