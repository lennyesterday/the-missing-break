"""The block's sounds: in the background the street and cars passing
(changed: no music, no chatter, no horns). Things that happen in the picture have their
own sound, right when they happen: the basketball only when somebody plays with it (bounces, the
rim, the chain net), and the el train each time it passes."""

import json
import re
import wave
from pathlib import Path

import numpy as np
import pytest

from art import ambience, build

ROOT = Path(__file__).parent.parent
SHOTS = ("shot-dunk-needle", "shot-three-bible", "shot-three-needle")


def wav(rel):
    with wave.open(str(ROOT / rel)) as w:
        rate = w.getframerate()
        return rate, np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768


def loudness(a, rate, t, width=0.06):
    s = int(t * rate)
    part = a[max(0, s - int(0.01 * rate)):s + int(width * rate)]
    return float(np.sqrt(np.mean(part ** 2))) if len(part) else 0.0


@pytest.fixture(scope="module")
def block():
    return build.block_scene()


def overlay(svg, name):
    m = re.search(rf'<g data-overlay="{name}" ([^>]*)>', svg)
    assert m, name
    return m.group(1)


# --- the basketball: only when somebody plays with it --------------------------------------------

@pytest.mark.parametrize("shot", SHOTS)
def test_each_shot_comes_with_its_own_sound(block, shot):
    attrs = overlay(block, shot)
    src = re.search(r'data-sound="app/static/([^"]+)"', attrs).group(1)
    rate, a = wav(f"static/{src}")
    secs = float(re.search(r'data-auto-delay="([\d.]+)"', attrs).group(1))
    assert abs(len(a) / rate - secs) < 0.5                  # as long as the shot


@pytest.mark.parametrize("shot", SHOTS)
def test_the_ball_sounds_when_it_hits_the_ground_and_the_net(block, shot):
    events = build.SHOT_SOUNDS[shot]
    rate, a = wav(f"static/audio/block/{shot}.wav")
    quiet = loudness(a, rate, 0.02, 0.03)                   # before anyone touches the ball
    assert events["bounces"]                                # it bounces
    for t in events["bounces"] + [events["swish_at"]]:
        assert loudness(a, rate, t) > 4 * quiet + 0.02, t   # you hear it right then


def test_the_bounces_are_where_the_ball_is_on_the_ground():
    # the three by Needle dribbles to the line: down at 0.9 s and 1.3 s, and after the swish
    bounces = build.SHOT_SOUNDS["shot-three-needle"]["bounces"]
    assert 0.9 in bounces and 1.3 in bounces and 3.1 in bounces


def test_the_dunk_rattles_the_rim_and_he_lands():
    dunk = build.SHOT_SOUNDS["shot-dunk-needle"]
    assert dunk["dunk"] and dunk["lands"] == 5.6            # he drops down from the rim


def test_no_ball_in_the_background():
    text = (ROOT / "art" / "ambience.py").read_text()
    block_code = text[text.index("def block_samples"):text.index("\ndef ", text.index("def block_samples"))]
    assert "bounce" not in block_code and "dribbl" not in block_code


def test_the_page_plays_a_part_s_sound_when_it_comes_up():
    js = (ROOT / "app.py").read_text()
    assert "overlay.dataset.sound" in js


# --- the train: each time it passes ----------------------------------------------------------------

def test_the_train_on_the_block_passes_now_and_then(block):
    m = re.search(r'values="820 0;-900 0;-900 0" keyTimes="0;([\d.]+);1" dur="([\d.]+)s"', block)
    assert m
    passing, every = float(m.group(1)) * float(m.group(2)), float(m.group(2))
    assert passing == pytest.approx(build.BLOCK_TRAIN[0], abs=0.01) and every == build.BLOCK_TRAIN[1]
    assert every > passing + 5                              # with a quiet while in between


def test_the_train_sound_goes_with_the_train(block):
    cues = json.loads(re.search(r"data-cues='([^']+)'", block).group(1))
    train = next(c for c in cues if "train" in c["src"])
    passing, every = build.BLOCK_TRAIN
    assert train["every"] == every and train["on"] == [[0, passing]]
    rate, a = wav(train["src"].removeprefix("app/"))
    assert abs(len(a) / rate - passing) < 0.3
    assert loudness(a, rate, passing / 2, 0.3) > 3 * loudness(a, rate, 0.05, 0.1)   # loudest when it's in front


def test_repeating_cues_follow_the_picture_s_clock():
    js = (ROOT / "app.py").read_text()
    assert "cue.every" in js


# --- the background: chatter, cars, a horn now and then (no music) -------------------------------

def test_no_stereo_on_the_block(block):
    # changed: the player didn't want music on the block, so the stereo is gone (the cypher's
    # boombox, once it's there, is only a picture)
    assert 'id="block-stereo"' not in block


def test_the_background_is_just_the_street():
    # changed: no _stereo, no chatter, and (changed again) no horns: they sounded like a weird
    # trumpet; the block's background is the street's rumble and the cars passing
    text = (ROOT / "art" / "ambience.py").read_text()
    block_code = text[text.index("def block_samples"):text.index("\ndef ", text.index("def block_samples"))]
    assert "_street(m" in block_code and "horns=False" in block_code
    for part in ("_stereo", "_beat", "_chatter", "_horns("):
        assert part not in block_code, part


def test_no_horns_on_the_block():
    # changed: was test_only_a_few_horns (at most 3); now none at all
    m = ambience._Mix(3)
    ambience._street(m, 1.0, horns=False)
    quiet = m.out.copy()
    m2 = ambience._Mix(3)
    ambience._street(m2, 1.0)
    assert not np.array_equal(quiet, m2.out)                 # the other places keep their far-off horns


def test_the_train_does_not_squeal():
    # changed: the rails' high squeal (a squeaky tone) is gone from the train; rumble and clacks stay
    rate, a = wav("static/audio/block/train.wav")
    spectrum = np.abs(np.fft.rfft(a))
    f = np.fft.rfftfreq(len(a), 1 / rate)
    band = spectrum[(f > 2700) & (f < 3100)].mean()
    around = spectrum[(f > 2000) & (f < 2600)].mean()
    assert band < 1.5 * around                               # no tone sticking out up there


def test_the_swish_is_a_soft_net_sound():
    # the ball through the net: a soft swish of noise (not a jingle of pings), quick in, fading out
    m = ambience._Mix(2)
    swish = ambience._swish(m)
    rate = ambience.SR
    assert 0.25 <= len(swish) / rate <= 0.6
    peak = np.argmax(np.abs(swish)) / rate
    assert peak < 0.12                                       # it comes at once
    assert loudness(swish, rate, len(swish) / rate - 0.06, 0.05) < 0.2 * loudness(swish, rate, peak, 0.05)  # and dies away
    spectrum = np.abs(np.fft.rfft(swish))
    f = np.fft.rfftfreq(len(swish), 1 / rate)
    assert spectrum[(f > 1000) & (f < 8000)].sum() > 0.7 * spectrum.sum()   # airy: a "shh", no thump


def test_no_voices_in_the_background():
    # changed: was test_the_chatter_sounds_like_voices; the player didn't want the distant
    # chattering, so the voices are gone from the block (and the code that made them)
    assert not hasattr(ambience, "_chatter")
