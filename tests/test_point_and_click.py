"""Point and click: the ways out are places in the picture (doors, street signs, the gate, the
portal, the picture's edge), not graffiti buttons."""

import re
from pathlib import Path

import pytest

from logic import SCENES

ROOT = Path(__file__).parent.parent
APP = (ROOT / "app.py").read_text()

# every way out of a scene that has its own picture, and the label it shows
EXITS = {
    "hq": {"go_block": "HIT THE BLOCK"},
    "block": {"go_hq": "GOODFELLAS HQ", "go_record_shop": "RICO'S RECORDS", "go_battle": "DISCO FEVER",
              "go_gate": "149 ST STATION", "go_store": "CORNER STORE"},
    "record_shop": {"go_block": "BACK TO THE BLOCK"},
    "gate": {"go_block": "BACK TO THE BLOCK", "enter_station": "OPEN THE GATE"},
    "station": {"go_block": "BACK TO THE BLOCK"},
    "corner_store": {"go_block": "BACK TO THE BLOCK"},
    "flash": {"go_hq": "THROUGH THE PORTAL"},
}


def svg(scene):
    return (ROOT / "assets" / "scenes" / f"{scene}.svg").read_text()


def group(text, action):
    """The <g ...> that has this data-action, up to its title (its opening part)."""
    start = text.rindex("<g", 0, text.index(f'data-action="{action}"'))
    return text[start:text.index("</title>", start)]


def exit_part(text, action):
    """The whole exit group for this action, up to its end marker."""
    start = text.rindex("<g", 0, text.index(f'data-action="{action}"'))
    return text[start:text.index("<!-- end exit -->", start)]


def test_every_way_out_is_listed():
    for scene, exits in EXITS.items():
        targets = {a["id"] for a in SCENES[scene]["actions"] if "target" in a and not a.get("by_app")}
        if scene == "hq":
            targets.discard("go_flash")  # Portals' portal: already in the picture (the sprayed portal)
        assert targets == set(exits), scene


@pytest.mark.parametrize("scene", list(EXITS))
def test_the_ways_out_are_exits_in_the_picture(scene):
    text = svg(scene)
    for action, label in EXITS[scene].items():
        assert 'class="exit"' in group(text, action), (scene, action)
        part = exit_part(text, action)
        # a hover label, or the street sign that says it
        assert 'class="exit-label"' in part or 'class="street-sign"' in part, (scene, action)
        assert label in part.replace("&#39;", "'"), (scene, action)


@pytest.mark.parametrize("scene", list(EXITS))
def test_no_graffiti_buttons_for_travelling(scene):
    text = svg(scene)
    for action in EXITS[scene]:
        part = exit_part(text, action)
        assert 'y="406"' not in part, (scene, action)  # (where the old buttons sat)


def test_the_block_has_a_street_sign_pole():
    text = svg("block")
    assert 'id="street-signs"' in text
    signs = text[text.index('id="street-signs"'):text.index("<!-- end street-signs -->")]
    for action in ("go_hq", "go_record_shop", "go_battle", "go_gate"):
        assert f'data-action="{action}"' in signs
    assert ">STORE ▶</text>" not in text  # (the old tag over the store's door)


@pytest.mark.parametrize("walk, label", [("block__record_shop", "ENTER RICO'S"), ("gate__station", "ENTER THE STATION")])
def test_the_walks_end_at_a_door_to_click(walk, label):
    text = (ROOT / "assets" / "walks" / f"{walk}.svg").read_text()
    # (SKIP is data-action="enter" too: the door is the exit)
    door = text[text.rindex("<g", 0, text.index('class="exit"')):]
    door = door[:door.index("<!-- end exit -->")]
    assert 'data-action="enter"' in door and label in door.replace("&#39;", "'")
    assert 'y="398"' not in door  # no button at the bottom right any more


def test_labels_show_under_the_pointer_and_on_touch_screens():
    css = APP[APP.index("SVG_SCREEN_CSS"):]
    assert re.search(r"\.exit:hover \.exit-label", css)
    assert "(hover: none)" in css
