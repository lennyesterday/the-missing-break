"""The graffiti fonts, and how wide a text set in them is (read from the font files).

Sedgwick Ave Display (pieces) and Sedgwick Ave (tags), SIL Open Font License, see static/fonts/OFL.txt.
"""

from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts"
FILES = {"piece": "SedgwickAveDisplay-Regular.ttf", "tag": "SedgwickAve-Regular.ttf"}
LETTER_SPACING = 1


@lru_cache(maxsize=None)
def _metrics(kind):
    font = TTFont(FONT_DIR / FILES[kind])
    cmap = font.getBestCmap()
    advances = font["hmtx"].metrics
    return cmap, advances, font["head"].unitsPerEm


def text_width(text, size, kind="piece"):
    """Width in px of text at this font size, letter spacing included."""
    cmap, advances, upm = _metrics(kind)
    units = sum(advances[cmap.get(ord(ch), cmap[ord("?")])][0] for ch in text)
    return units / upm * size + LETTER_SPACING * max(len(text) - 1, 0)
