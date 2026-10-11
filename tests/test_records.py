"""Records on a turntable spin flat on the platter: seen at an angle, the disc keeps its outline
and only its grooves and label turn (they used to tip over like a flipped coin)."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SPINNING = {
    "assets/scenes/record_shop.svg": 1,       # Rico's listening deck
    "assets/scenes/station.svg": 2,           # the battle DJ's two turntables
    "assets/endings/ending_legends.svg": 1,   # Needle cuts in "Think About It"
}


@pytest.mark.parametrize("path, count", SPINNING.items())
def test_records_spin_flat_on_the_platter(path, count):
    svg = (ROOT / path).read_text()
    records = svg.split('class="spinning-record"')[1:]
    assert len(records) == count
    for record in records:
        record = record[:record.index("<!-- end record -->")]
        # the disc is tilted by squashing it (scale), and turns inside that (rotate around its own centre)
        assert re.search(r'scale\(1 0\.\d+\)', record)
        assert 'type="rotate" from="0" to="360"' in record
        assert "<ellipse" not in record  # a real disc, not a flat ellipse turned around


@pytest.mark.parametrize("path", SPINNING)
def test_no_record_tips_over_like_a_coin(path):
    svg = (ROOT / path).read_text()
    # the old way: an ellipse (or its label) turned or squeezed around a point
    assert not re.search(r'values="0 \d+ \d+;360 \d+ \d+"[^>]*>\s*<ellipse', svg)
    assert 'attributeName="rx" values="6;2;6"' not in svg
