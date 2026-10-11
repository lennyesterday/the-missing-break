"""Sound effects in the story intro: the spray can while Portals paints, the siren, the officer
shouting and the dog barking during the chase, all quieter than the intro song."""

import json
import re
from pathlib import Path

import pytest

from art.build import _painter_route
from logic import SONGS, INTRO_MUSIC

ROOT = Path(__file__).parent.parent
INTRO = (ROOT / "assets" / "screens" / "intro.svg").read_text()
END = float(re.search(r'data-end="([\d.]+)"', INTRO).group(1))
CUES = {c["src"].split("/")[-1]: c for c in json.loads(
    re.search(r"data-cues='([^']*)'", INTRO).group(1).replace("&#39;", "'"))}


def spray_phases():
    frames, _, _ = _painter_route()
    return [(frames[i - 1][0], frames[i][0]) for i in range(1, len(frames)) if frames[i][5]]


def test_the_four_sounds_ship_with_the_game():
    for name in ("spray.mp3", "police_shout.mp3", "siren.mp3", "police_dog.mp3"):
        assert (ROOT / "static" / "audio" / "intro" / name).is_file()
        assert f"intro/{name}" in (ROOT / "static" / "audio" / "CREDITS.md").read_text()
    assert set(CUES) == {"spray.mp3", "police_shout.mp3", "siren.mp3", "police_dog.mp3"}


def test_the_spray_sounds_exactly_while_portals_sprays():
    phases = [(round(a, 2), round(b, 2)) for a, b in spray_phases()]
    assert [tuple(p) for p in CUES["spray.mp3"]["on"]] == phases
    assert len(phases) == 8  # one per line of the story


def test_the_spray_mist_shows_while_he_sprays():
    # fixed: the mist used to come out after each line instead of while spraying it
    frames, _, total = _painter_route()
    values = re.search(r'<animate attributeName="opacity" values="([01;]+)" keyTimes="([\d.;]+)" dur="[\d.]+s" calcMode="discrete"',
                       INTRO)
    on, times = values.group(1).split(";"), [float(t) * total for t in values.group(2).split(";")]
    for a, b in spray_phases():
        k = min(range(len(times)), key=lambda i: abs(times[i] - a))
        assert on[k] == "1", (a, b)


def test_the_chase_sounds_come_with_the_chase():
    painting_done = _painter_route()[2]
    for name in ("police_shout.mp3", "siren.mp3", "police_dog.mp3"):
        for start, stop in CUES[name]["on"]:
            assert painting_done - 0.01 <= start < stop <= END + 0.01, name
    # the shout when the officer with the STOP! POLICE! bubble comes in (the chase: Portals, dog, officer, officer)
    chase = INTRO[INTRO.index('id="police-chase"'):INTRO.index("<!-- end police-chase -->")]
    officer_in = float(re.findall(r'<set attributeName="visibility" to="visible" begin="([\d.]+)s"/>', chase)[2])
    assert "STOP! POLICE!" in chase
    assert abs(CUES["police_shout.mp3"]["on"][0][0] - officer_in) < 0.3

def test_they_sit_in_the_background_of_the_song():
    music = SONGS[INTRO_MUSIC]["volume"]
    for cue in CUES.values():
        assert 0 < cue["vol"] < music


def test_the_page_plays_the_cues_and_stops_them_on_skip():
    app = (ROOT / "app.py").read_text()
    assert "dataset.cues" in app and "clearCues" in app
    # the picture sits in a shadow root, where document.contains() is always false: that stopped
    # every sound right after it started
    cues = app[app.index("const clearCues"):app.index("// the sound switch")]
    assert "document.contains" not in cues and "isConnected" in cues
