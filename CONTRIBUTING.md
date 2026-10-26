# Contributing

Thanks for helping with The Missing Break. Small, focused pull requests are easiest to review.

## Setup

- Install Python 3.12 or newer and `uv`.
- From the project root, run `uv sync`.
- Start the game with `uv run streamlit run app.py`.
- Run the test suite with `uv run pytest`.

## Changes

- Create a feature branch from the current main branch.
- Check `specs/` for the relevant feature requirements before changing behavior.
- Keep game rules in `logic.py`, persistence in `db.py`, and Streamlit presentation in `app.py`.
- Add or update tests for behavior changes.
- Describe the change and the checks you ran in your pull request.
- Keep save databases, credentials, and local environment files out of commits. Audio and font credits are in `static/audio/CREDITS.md` and `static/fonts/OFL.txt`.
