"""Every graffiti in the game is lettered like graffiti, but stays readable."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SVGS = ["assets/screens/home.svg", "assets/screens/intro.svg", "assets/scenes/hq.svg", "assets/scenes/record_shop.svg", "assets/scenes/block.svg", "assets/scenes/station.svg", "assets/scenes/battle.svg",
        "assets/endings/ending_legends.svg", "assets/endings/ending_static.svg",
        "assets/walks/block__record_shop.svg"]
PIECE_FONT = "Sedgwick Ave Display"
TAG_FONT = "'Sedgwick Ave'"


def test_graffiti_fonts_ship_with_the_game_and_their_licence():
    fonts = ROOT / "static" / "fonts"
    assert (fonts / "SedgwickAveDisplay-Regular.ttf").is_file()
    assert (fonts / "SedgwickAve-Regular.ttf").is_file()
    assert "SIL Open Font License" in (fonts / "OFL.txt").read_text()


def test_streamlit_serves_the_fonts():
    config = (ROOT / ".streamlit" / "config.toml").read_text()
    assert re.search(r"enableStaticServing\s*=\s*true", config)


def test_the_page_loads_the_fonts():
    app = (ROOT / "app.py").read_text()
    assert "@font-face" in app
    assert "app/static/fonts/SedgwickAveDisplay-Regular.ttf" in app
    assert "app/static/fonts/SedgwickAve-Regular.ttf" in app


@pytest.mark.parametrize("path", SVGS)
def test_every_piece_uses_the_graffiti_font_and_bounces(path):
    svg = (ROOT / path).read_text()
    # the coloured layer of a piece is the one with the outline painted under the fill
    # (small info lines in plain block letters are class="label", they are not graffiti)
    pieces = [t for t in re.findall(r"<text [^>]*paint-order=\"stroke\"[^>]*>", svg) if 'class="label"' not in t]
    assert pieces, "no pieces found"
    for main in pieces:
        assert PIECE_FONT in main, main[:120]
        assert 'rotate="' in main  # letters bounce
    # and every piece has the white outer outline and a 3D block (several shadow layers)
    assert svg.count('class="cloud"') >= len(pieces)
    assert svg.count('class="block"') >= 3 * len(pieces)


@pytest.mark.parametrize("path", SVGS)
def test_tags_use_the_handstyle_font(path):
    svg = (ROOT / path).read_text()
    tags = re.findall(r'<text [^>]*class="tag"[^>]*>', svg)
    for t in tags:
        assert TAG_FONT in t
