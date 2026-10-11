"""MC Bible's rhyme book: take it, leave it, or read it (his view of the open book, the verse
handwritten over several pages, crossed-out bars, notes and tags)."""

import re
from pathlib import Path

import pytest

from art import build
from db import load_game
from logic import RHYME_BOOK_VERSE
from tests.apphelpers import choose, picture, start_app, start_new_game, svg_screen

ROOT = Path(__file__).parent.parent
SPREADS = [ROOT / "assets" / "screens" / f"rhymebook_{n}.svg" for n in (1, 2)]


@pytest.fixture
def db_file(tmp_path, monkeypatch):
    path = tmp_path / "game.db"
    monkeypatch.setenv("MISSING_BREAK_DB", str(path))
    return path


def open_sign(at):
    start_new_game(at)
    choose(at, "inspect:rhyme_book", screen="picture")


def test_the_sign_offers_take_read_and_leave():
    svg = (ROOT / "assets" / "scenes" / "hq.svg").read_text()
    sign = svg[svg.index('data-overlay="inspect-rhyme_book"'):]
    sign = sign[:sign.index("<!-- end sign -->")]
    for action, label in (("take_rhyme_book", "TAKE IT"), ("read:rhyme_book", "READ IT"), ("close", "LEAVE IT")):
        assert f'data-action="{action}"' in sign and label in sign


def test_leave_it_keeps_it_on_the_couch(db_file):
    at = start_app()
    open_sign(at)
    choose(at, "close", screen="picture")
    shown = picture(at)
    assert "inspect-rhyme_book" not in shown["show"]
    assert "offer-take_rhyme_book" in shown["show"]
    assert at.session_state["game"].inventory == []


def test_take_it_puts_it_in_the_inventory(db_file):
    at = start_app()
    open_sign(at)
    choose(at, "take_rhyme_book", screen="picture")
    assert at.session_state["game"].inventory == ["rhyme_book"]
    assert load_game(db_file).inventory == ["rhyme_book"]


def test_read_it_flips_through_the_book_and_closes_it(db_file):
    at = start_app()
    open_sign(at)
    saved = load_game(db_file)

    choose(at, "read:rhyme_book", screen="picture")
    book = svg_screen(at, "rhymebook")
    assert picture(at) is None
    assert 'id="rhymebook-1"' in book["svg"] and book["enabled"] == ["page_next", "close_book"]

    choose(at, "page_next", screen="rhymebook")
    book = svg_screen(at, "rhymebook")
    assert 'id="rhymebook-2"' in book["svg"] and book["enabled"] == ["page_prev", "close_book"]

    choose(at, "page_prev", screen="rhymebook")
    assert 'id="rhymebook-1"' in svg_screen(at, "rhymebook")["svg"]

    choose(at, "close_book", screen="rhymebook")
    assert svg_screen(at, "rhymebook") is None
    shown = picture(at)
    assert "inspect-rhyme_book" not in shown["show"] and "offer-take_rhyme_book" in shown["show"]
    assert load_game(db_file) == saved  # reading is not a move


def test_every_bar_of_the_verse_is_in_the_book():
    assert len(RHYME_BOOK_VERSE) == 16
    pages = "".join(p.read_text() for p in SPREADS)
    for bar in RHYME_BOOK_VERSE:
        label = bar.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
        assert f'aria-label="{label}"' in pages, bar


def test_it_looks_like_a_real_rhyme_book():
    pages = "".join(p.read_text() for p in SPREADS)
    assert pages.count('class="crossed"') >= 3       # bars crossed out
    assert pages.count('class="margin-note"') >= 4   # notes, tags and doodles
    assert 'id="coffee-ring"' in pages and "Bible 1" in pages
    for spread in SPREADS:
        svg = spread.read_text()
        assert 'id="bible-hands"' in svg              # his view: his hands hold the book
        assert 'id="page-turn"' in svg                # a page flips over when you get there
        assert "Sedgwick Ave" in svg                  # handwriting
        assert "♪" not in svg                         # no listening, only reading


@pytest.mark.parametrize("n", [1, 2])
def test_spreads_match_their_source(n):
    assert SPREADS[n - 1].read_text() == build.rhymebook_spread(n)
