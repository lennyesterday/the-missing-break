"""The crew doesn't always stand side-on: each of them can face us too, with the same look as
from the side (specs/scene-art.md): both eyes, both ears, the right hat, the same props. Here
and there in the game someone faces us; the b-boys at the cypher face the dancer."""

import re
from pathlib import Path

import pytest

from art import crew

ROOT = Path(__file__).parent.parent

FRONT = {
    "needle": (lambda: crew.needle_front(100), ('class="kangol"', 'class="headphones"')),
    "bible": (lambda: crew.bible_front(100), ('class="short-hair"', "RHYME")),
    "meyhem": (lambda: crew.meyhem_front(100), ('class="short-hair"', 'class="mic"')),
    "portals": (lambda: crew.portals_front(100), ('class="afro"', 'class="headband"', 'class="spray-can"')),
    "reekz": (lambda: crew.reekz_front(100), ('class="bucket"', 'class="boombox"')),
}


@pytest.mark.parametrize("who", FRONT)
def test_each_of_them_can_face_us(who):
    make, parts = FRONT[who]
    svg = make()
    assert "(facing us)" in svg
    assert svg.count('class="eye"') == 2 and svg.count('class="ear"') == 2 and svg.count('class="brow"') == 2
    assert 'class="mouth"' in svg and 'class="sole"' in svg and 'class="belt"' in svg
    for part in parts:
        assert part in svg, part


def test_bible_faces_us_with_or_without_his_book():
    either = crew.bible_front_either(100)
    assert 'data-overlay="has-rhyme_book"' in either and 'data-overlay="lacks-rhyme_book"' in either
    assert "RHYME" not in crew.bible_front(100, book=False)


@pytest.mark.parametrize("picture", ["screens/home", "scenes/hq", "scenes/block", "scenes/record_shop",
                                     "scenes/corner_store", "scenes/flash", "scenes/station", "cypher/toprock_from_stand"])
def test_here_and_there_someone_faces_us(picture):
    svg = (ROOT / "assets" / f"{picture}.svg").read_text()
    assert "(facing us)" in svg


def test_the_b_boys_on_the_right_of_the_cypher_face_the_dancer():
    svg = (ROOT / "assets" / "cypher" / "toprock_from_stand.svg").read_text()
    for x, who, inner in re.findall(r'<g class="in-circle" data-x="([\d.]+)" data-feet="[\d.]+" data-scale="[\d.]+" data-who="(bboy[^"]*)"[^>]*>(.{0,80})', svg):
        if float(x) > 400:
            assert "scale(-1 1)" in inner, who                    # mirrored: facing left, to the middle
