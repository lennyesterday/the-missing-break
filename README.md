# The Missing Break

A hip-hop inspired text adventure built with Python and Streamlit. The game follows a crew through a night in the neighborhood, with choices, music, scenes, and rap battles.

## The story

South Bronx, summer 1977. Two days before the Borough DJ Battle, the Sopranos Family steal the GoodFellas' secret break, Lyn Collins – "Think About It". The crew has to get it back from King Krete and still be ready for the final.

The GoodFellas:

| Member | Element | In the game |
|---|---|---|
| Fantastic Needle | DJ | Can't loop "Think About It" at his turntables at first; with Grandmaster Flash's crayon secret he practices it and drops it in the final |
| MC Bible | MC | Takes on King Krete in the rap battle, alone; without his rhyme book he chokes |
| Portals | Graffiti | Reads the Sopranos' tags; his spray cans open a portal to Grandmaster Flash |
| Reekz | B-boy | Wins the cypher on the block and goes down to the real break |

The game is point and click: the crew talks in speech bubbles (click for the next line), and you travel and act by clicking things in the picture: the street signs and doors, Needle's turntables, Portals' spray cans, the records on the floor. Progress is saved after every move.

The full story, every scene and the walkthrough are in [docs/story.md](docs/story.md).

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
- `art/` — scripts that make the game's pictures and sounds: `uv run python -m art.build` rebuilds `assets/`, `uv run python -m art.ambience` the background sounds, `uv run python -m art.off_break` Needle's off-beat try at the break
- `assets/` — scene and interface illustrations
- `static/audio/` and `static/fonts/` — audio, sound effects, and fonts used by the app (the crew's spoken lines are in `static/audio/voices/`; lines without a recording stay silent)
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
