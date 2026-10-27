"""Shared helpers for tests that drive the real app with Streamlit's AppTest."""

import base64
import json
import re
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_FILE = str(Path(__file__).parent.parent / "app.py")


def start_app():
    """A fresh AppTest is a fresh app process: no session state carries over."""
    return AppTest.from_file(APP_FILE, default_timeout=10).run()


def click(at, key):
    at.button(key=key).click().run()
    assert not at.exception


def button_keys(at):
    return [button.key for button in at.button]


def svg_screen(at, name):
    """The data a clickable graffiti screen ("home", "intro") gets, or None if it is not shown."""
    for element in at.get("bidi_component"):
        if element.proto.id.endswith(f"-{name}"):
            return json.loads(element.proto.json)
    return None


def home_screen(at):
    return svg_screen(at, "home")


def intro_screen(at):
    return svg_screen(at, "intro")


def choose(at, choice, screen="home"):
    """Click a graffiti button (home: start / resume / menu, intro: go).

    AppTest cannot click inside a custom component, so this hands the app the same
    value the component sends when the player clicks. Everything after that is the
    real app code.
    """
    assert svg_screen(at, screen) is not None, f"the {screen} screen is not shown"
    at.session_state[f"{screen}_choice"] = choice
    at.run()
    assert not at.exception


def start_new_game(at):
    """START on the train, LET'S GO after the story intro, then Portals' escape: the player is in hq."""
    choose(at, "start")
    choose(at, "go", screen="intro")
    choose(at, "arrive", screen="escape")  # changed: the escape through the portal comes before the basement


def shown_svgs(at):
    """The SVG source of every picture currently on the page.

    Pictures are drawn inline by the svg_screen component (st.image would not animate them),
    so this collects the SVGs the component gets, plus any st.image SVGs.
    """
    svgs = [json.loads(e.proto.json)["svg"] for e in at.get("bidi_component")]
    for element in at.get("image"):
        for img in element.proto.imgs:
            if img.url.startswith("data:image/svg+xml;base64,"):
                svgs.append(base64.b64decode(img.url.split(",", 1)[1]).decode())
    return svgs


def shows_picture(at, svg_id):
    return any(f'id="{svg_id}"' in svg for svg in shown_svgs(at))


def picture(at):
    """The data of the scene picture (its clickable parts and what it shows), or None."""
    return svg_screen(at, "picture")


def offered(at):
    """Every action the player can choose right now: Streamlit buttons plus the picture's buttons."""
    shown = picture(at)
    return button_keys(at) + (shown["enabled"] if shown else [])


def act(at, action_id):
    """Choose an action, as a Streamlit button or as a graffiti button in the scene picture.

    changed: a walk that goes on by itself when it's over (between the basement and the block)
    is passed through afterwards, as it would be in the game; the test lands in the next scene.
    Walks that wait for a click (ENTER RICO'S) stay up.
    changed (specs/battle-preparation.md): Needle's first try at the turntables goes on by itself
    too (he gets behind the decks, about 15 s of the break always off), as in the game.
    changed (specs/the-dj-battle.md): so does Needle's set at the DJ battle (about 41 s), on the
    way to Legends of the Bronx; the test lands on the ending."""
    if action_id in button_keys(at):
        click(at, action_id)
    else:
        assert action_id in picture(at)["enabled"], f"{action_id} is not offered"
        choose(at, action_id, screen="picture")
    if action_id == "try_practice" and (at.session_state["practicing"] or {}).get("trying"):
        choose(at, "decks_ready", screen="picture")
        choose(at, "tried", screen="picture")
    if action_id == "start_battle" and svg_screen(at, "dj_set") is not None:
        choose(at, "set_over", screen="dj_set")
    if walks_on_by_itself(at):
        choose(at, "enter", screen="picture")


def walks_on_by_itself(at):
    shown = picture(at)
    return bool(shown) and re.search(r'<svg[^>]*id="walk-[^"]*"[^>]*data-auto-action="enter"', shown["svg"]) is not None
