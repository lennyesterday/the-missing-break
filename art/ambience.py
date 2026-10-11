"""Generates the background sounds, made from scratch, so they are free of copyright. The
basement's (a 40 s seamless loop): the hum of the sound system, a muffled boom-bap beat (96 BPM)
from a record playing, water dripping every 2.5 s, muffled street noise and a train rumbling past
twice. And the other places' (30 s loops, AMBIENCES): the street for the walks, the block,
Rico's Record Shop, the corner store and Grandmaster Flash's realm.

    uv run python -m art.ambience

It is written as a plain WAV file: it plays in every browser and needs no extra tools.
"""

import math
import random
import struct
import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent.parent / "static" / "audio" / "ambience" / "basement.wav"
SR, SECS, XF = 22050, 40.0, 1.0
BPM = 96


def basement_samples():
    random.seed(7)
    n = int(SR * (SECS + XF))
    out = [0.0] * n

    def add(start, samples):
        s0 = int(start * SR)
        for k, v in enumerate(samples):
            if 0 <= s0 + k < n:
                out[s0 + k] += v

    # the hum: 60 Hz and 120 Hz, wobbling a little
    for i in range(n):
        t = i / SR
        out[i] += 0.035 * math.sin(2 * math.pi * 60 * t) + 0.02 * math.sin(2 * math.pi * 120 * t + 0.3 * math.sin(2 * math.pi * 0.2 * t))
    # muffled street: brown noise, low-passed
    b = lp = 0.0
    for i in range(n):
        b = 0.995 * b + random.uniform(-1, 1) * 0.02
        lp += 0.05 * (b - lp)
        out[i] += 0.5 * lp
    # a muffled boom-bap beat: kick on 1 and 3, snare on 2 and 4
    beat = 60 / BPM
    kick = [0.22 * math.sin(2 * math.pi * (55 + 60 * math.exp(-k / 400)) * k / SR) * math.exp(-k / 2500)
            for k in range(int(0.3 * SR))]
    sn = 0.0
    snare = []
    for k in range(int(0.2 * SR)):
        sn += 0.15 * (random.uniform(-1, 1) - sn)
        snare.append(0.12 * sn * math.exp(-k / 1200))
    for k in range(int((SECS + XF) / beat) + 1):
        add(k * beat, kick if k % 2 == 0 else snare)
        if k % 4 == 3:
            add(k * beat + beat / 2, [v * 0.6 for v in kick])
    # water dripping every 2.5 s: a short falling "plip"
    plip = [0.08 * math.sin(2 * math.pi * (1400 - 600 * j / 900) * j / SR) * math.exp(-j / 500) for j in range(900)]
    for k in range(int((SECS + XF) / 2.5) + 1):
        add(0.9 + k * 2.5, plip)
    # a train rumbling past: a low swelling roar with a rattle
    for start in (8.0, 28.0):
        r = 0.0
        length = int(6 * SR)
        roar = []
        for j in range(length):
            r += 0.02 * (random.uniform(-1, 1) - r)
            rattle = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(2 * math.pi * 7 * j / SR))
            roar.append(0.9 * math.sin(math.pi * j / length) ** 2 * r * rattle)
        add(start, roar)
    # seamless loop: blend the extra second at the end into the start
    loop_len, x = int(SR * SECS), int(SR * XF)
    loop = out[:loop_len]
    for i in range(x):
        a = i / x
        loop[i] = loop[i] * a + out[loop_len + i] * (1 - a)
    peak = max(abs(v) for v in loop)
    return [0.8 * v / peak for v in loop]


# --- the other places' background sounds (numpy: much faster than the basement's plain loops) ---

LOOP_SECS = 30.0  # each of these is a seamless loop about this long (whole bars where there is a beat)


class _Mix:
    """A track to add sounds to, secs long plus XF, made into a seamless loop at the end. With a
    beat in it, secs is a whole number of bars, so the beat runs on round the loop."""

    def __init__(self, seed, secs=LOOP_SECS):
        self.rng = np.random.default_rng(seed)
        self.secs = secs
        self.n = int(SR * (secs + XF))
        self.out = np.zeros(self.n)
        self.t = np.arange(self.n) / SR

    def add(self, start, sound, gain=1.0):
        s0 = int(start * SR) % self.n
        end = min(self.n, s0 + len(sound))
        self.out[s0:end] += gain * sound[:end - s0]

    def noise(self, secs):
        return self.rng.uniform(-1, 1, int(secs * SR))

    def loop(self, peak=0.8):
        """Blend the extra XF seconds at the end into the start: the loop has no seam."""
        loop_len, x = int(SR * self.secs), int(SR * XF)
        a = np.linspace(0, 1, x)
        loop = self.out[:loop_len].copy()
        loop[:x] = loop[:x] * a + self.out[loop_len:loop_len + x] * (1 - a)
        return peak * loop / np.abs(loop).max()


def _filter(x, low=None, high=None):
    """Keep the frequencies between low and high (Hz), softly."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    gain = np.ones_like(f)
    if high:
        gain /= 1 + (f / high) ** 4
    if low:
        gain *= (f / low) ** 4 / (1 + (f / low) ** 4)
    return np.fft.irfft(np.fft.rfft(x) * gain, len(x))


def _tone(freq, secs, decay, harmonics=(1.0,)):
    t = np.arange(int(secs * SR)) / SR
    wave_ = sum(h * np.sin(2 * np.pi * freq * (k + 1) * t) for k, h in enumerate(harmonics))
    return wave_ * np.exp(-t / decay)


def _kick(m, gain=1.0):
    t = np.arange(int(0.3 * SR)) / SR
    return gain * np.sin(2 * np.pi * (50 + 70 * np.exp(-t * 30)) * t) * np.exp(-t * 12)


def _snare(m, gain=1.0):
    t = np.arange(int(0.2 * SR)) / SR
    return gain * (_filter(m.noise(0.2), low=1200) * 0.8 + 0.3 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 22)


def _hat(m, gain=1.0):
    t = np.arange(int(0.05 * SR)) / SR
    return gain * _filter(m.noise(0.05), low=6000) * np.exp(-t * 80)


def _beat(m, bpm, gain, muffle, kicks=(0, 2.5), snares=(1, 3), hats=True):
    """A drum beat over the whole loop: kicks and snares on these beats of each bar, 8th hats;
    muffle (Hz): as if it comes from somewhere else."""
    beat = 60 / bpm
    track = np.zeros(m.n)
    for bar in range(int((m.secs + XF) / (4 * beat)) + 1):
        for b in kicks:
            s = int((bar * 4 + b) * beat * SR)
            k = _kick(m)
            track[s:s + len(k)] += k[:max(0, m.n - s)]
        for b in snares:
            s = int((bar * 4 + b) * beat * SR)
            k = _snare(m, 0.7)
            track[s:s + len(k)] += k[:max(0, m.n - s)]
        if hats:
            for e in range(8):
                s = int((bar * 4 + e / 2) * beat * SR)
                h = _hat(m, 0.25 if e % 2 else 0.4)
                track[s:s + len(h)] += h[:max(0, m.n - s)]
    m.out += gain * _filter(track, high=muffle)


def _street(m, gain=1.0, horns=True):
    """The city: a low rumble, cars swelling past, now and then a horn (horns=False: none)."""
    m.out += gain * 0.6 * _filter(m.rng.standard_normal(m.n), high=180)
    for start in m.rng.uniform(0, m.secs, 7):  # cars passing
        secs = m.rng.uniform(2.5, 4.5)
        env = np.sin(np.linspace(0, np.pi, int(secs * SR))) ** 2
        m.add(start, _filter(m.noise(secs), low=120, high=1400) * env, gain * 0.5)
    for start in m.rng.uniform(2, m.secs - 2, 2 if horns else 0):  # a horn, far off
        horn = _tone(415, 0.35, 1.0, (1, 0.5, 0.3)) + _tone(523, 0.35, 1.0, (1, 0.5, 0.3))
        m.add(start, _filter(horn, high=2500) * np.minimum(1, np.arange(len(horn)) / 400), gain * 0.08)


def _train(m, start, secs=6.0, gain=1.0):
    """The el train rumbling past, its wheels rattling."""
    n = int(secs * SR)
    rattle = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * np.arange(n) / SR))
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    m.add(start, _filter(m.noise(secs), high=500) * rattle * env, gain)


def street_samples():
    """The walks between places: the street, the crew's footsteps, cars, the el train going by,
    a siren far away."""
    m = _Mix(11)
    _street(m)
    for k in range(int((m.secs + XF) / 0.5)):  # the crew walking: soft steps, two a second
        step = _filter(m.noise(0.06), high=400) * np.exp(-np.arange(int(0.06 * SR)) / SR * 60)
        m.add(k * 0.5 + m.rng.uniform(-0.02, 0.02), step, 0.9 if k % 2 else 0.6)
    _train(m, 12.0, gain=1.2)
    t = np.arange(int(5 * SR)) / SR  # a siren, far away
    siren = np.sin(2 * np.pi * np.cumsum(750 + 150 * np.sin(2 * np.pi * 0.5 * t)) / SR) * np.sin(np.linspace(0, np.pi, len(t)))
    m.add(22.0, _filter(siren, high=1800), 0.05)
    return m.loop()


def block_samples():
    """The block's background: the street, its low rumble and cars passing. (The basketball and the train have their
    own sounds, when they happen in the picture: shot_samples, train_samples.)"""
    m = _Mix(12)
    _street(m, 0.9, horns=False)
    return m.loop()


def _underground(m, start, secs=7.0, gain=1.0):
    """A subway train rumbling past underground, the sound coming up the stairs: deep and
    muffled, swelling and dying away, a faint screech of the wheels in the middle."""
    n = int(secs * SR)
    t = np.arange(n) / SR
    env = np.sin(np.pi * t / secs) ** 2
    rumble = _filter(m.noise(secs), high=140) * (0.7 + 0.3 * np.sin(2 * np.pi * 3.5 * t))
    screech = np.sin(2 * np.pi * np.cumsum(1900 + 80 * np.sin(2 * np.pi * 0.9 * t)) / SR) * np.sin(np.pi * np.clip((t - 2) / 3, 0, 1)) ** 2
    m.add(start, (rumble * 2.5 + 0.015 * _filter(screech, high=2400)) * env, gain)


def station_gate_samples():
    """Outside the old station: the street (no horns, the crew is standing still), a train
    rumbling past underground twice, the wind blowing up the stairwell, the broken globe buzzing,
    water dripping somewhere down the stairs, echoing."""
    m = _Mix(16)
    _street(m, 0.6, horns=False)
    _underground(m, 4.0)
    _underground(m, 19.0, gain=0.8)
    t = m.t
    m.out += 0.25 * _filter(m.rng.standard_normal(m.n), low=300, high=1200) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.5) ** 2)  # the wind
    m.out += 0.012 * sum(np.sin(2 * np.pi * 120 * k * t) / k for k in range(1, 6)) * (np.sin(2 * np.pi * t / 2.6) > -0.6)  # the globe
    for at in np.arange(1.3, m.secs - 1, 3.1):  # a drip down the stairs, and its echo
        for k, g in enumerate((0.12, 0.05, 0.02)):
            m.add(at + k * 0.18, _tone(1400 - 200 * k, 0.12, 0.03), g)
    return m.loop()


def unlock_samples(events, start, secs):
    """The gate opening (events from art/build.py's UNLOCK_SOUNDS, in the picture's time; the
    sound starts at start): the key turning in the padlock (click-clack), the padlock dropping on
    the pavement, the chain rattling down, the scissor gate folding open with a metal screech."""
    m = _Mix(41)
    n = int(secs * SR)
    out = np.zeros(n)

    def put(at, sound, g):
        s0 = int((at - start) * SR)
        out[s0:s0 + len(sound)] += g * sound[:max(0, n - s0)]

    click = lambda f: _filter(m.noise(0.03), low=2000, high=7000) * np.exp(-np.arange(int(0.03 * SR)) / SR * 150) + 0.3 * _tone(f, 0.03, 0.01)
    put(events["key"], click(3200), 0.7)
    put(events["key"] + 0.12, click(2600), 0.9)
    clank = sum(_tone(f, 0.5, d) for f, d in ((880, 0.12), (1960, 0.07), (3100, 0.05)))
    clank[:int(0.05 * SR)] += 0.4 * _filter(m.noise(0.05), low=500) * np.exp(-np.arange(int(0.05 * SR)) / SR * 60)
    put(events["padlock"], clank, 0.6)
    for k in range(9):  # the chain, link by link
        put(events["chain"] + k * 0.035 + m.rng.uniform(0, 0.01), _tone(m.rng.uniform(2500, 4200), 0.03, 0.015) + 0.5 * click(1800), 0.35 * (1 - k / 12))
    g_secs = 0.6
    tt = np.arange(int(g_secs * SR)) / SR
    screech = np.sin(2 * np.pi * np.cumsum(700 + 500 * tt / g_secs + 60 * np.sin(2 * np.pi * 9 * tt)) / SR) * np.sin(np.pi * tt / g_secs)
    rattle = _filter(m.noise(g_secs), low=1500, high=5000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 22 * tt)))
    put(events["gate"], 0.35 * _filter(screech, high=3000) + 0.5 * rattle * np.sin(np.pi * tt / g_secs), 0.6)
    put(events["gate"] + g_secs, clank, 0.35)  # it bangs open against the frame
    return 0.8 * out / np.abs(out).max()


def train_samples(secs=7.0):
    """The el train passing over the block (in the picture it takes secs): it rumbles in, the
    wheels clack over the rail joints (two by two, under each car), it rumbles off."""
    m = _Mix(21)
    n = int(secs * SR)
    t = np.arange(n) / SR
    env = np.sin(np.pi * t / secs) ** 1.5
    out = 1.2 * _filter(m.noise(secs), high=350) * env
    out += 0.3 * _filter(m.noise(secs), low=300, high=1800) * env * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * t))
    clack = _filter(m.noise(0.05), low=200, high=2500) * np.exp(-np.arange(int(0.05 * SR)) / SR * 70)
    at = 0.3
    while at < secs - 0.3:  # the wheels over the joints: clack-clack ... clack-clack
        for off in (0, 0.11):
            s0 = int((at + off) * SR)
            out[s0:s0 + len(clack)] += 1.5 * clack[:n - s0] * env[min(n - 1, s0)]
        at += 0.48
    out *= np.minimum(1, (secs - t) / 0.05)
    return 0.8 * out / np.abs(out).max()


def _bounce(m):
    t = np.arange(int(0.15 * SR)) / SR
    return (np.sin(2 * np.pi * (85 + 60 * np.exp(-t * 40)) * t) * np.exp(-t * 28)
            + 0.35 * _filter(m.noise(0.15), low=900, high=5000) * np.exp(-t * 90))


def _swish(m, secs=0.4, gain=1.0):
    """The ball through the net: a soft, airy "shhh", there at once and dying away, the bright
    part going first (so it sweeps down a little, like the net catching the ball)."""
    n = int(secs * SR)
    t = np.arange(n) / SR
    attack = np.minimum(1, t / 0.015)
    high = _filter(m.noise(secs), low=3500, high=8000) * np.exp(-t * 18)
    mid = _filter(m.noise(secs), low=1300, high=3500) * np.exp(-t * 9) * np.minimum(1, t / 0.04)
    out = attack * (high + 0.8 * mid) * np.minimum(1, (secs - t) / 0.03)
    return gain * out / np.abs(out).max()


def shot_samples(events):
    """One shot on the court (events from art/build.py's SHOT_SOUNDS): the ball bouncing whenever
    it comes down on the court, sneakers squeaking when the shooter turns, the net swishing
    when it goes in; for the dunk the rim clangs and rattles while he hangs on it, and he lands."""
    m = _Mix(31)
    n = int(events["secs"] * SR)
    out = np.zeros(n)

    def put(at, sound, g):
        s0 = int(at * SR)
        out[s0:s0 + len(sound)] += g * sound[:max(0, n - s0)]

    for at in events["bounces"]:
        put(at, _bounce(m), 0.9)
    for at in events["squeaks"]:
        tt = np.arange(int(0.13 * SR)) / SR
        put(at, np.sin(2 * np.pi * np.cumsum(2300 + 900 * tt / 0.13 + 150 * np.sin(2 * np.pi * 40 * tt)) / SR)
            * np.sin(np.pi * tt / 0.13), 0.12)
    put(events["swish_at"], _swish(m), 0.55)
    if events["dunk"]:
        at = events["swish_at"]
        clang = sum(_tone(f, 1.0, d) for f, d in ((620, 0.25), (1310, 0.15), (2150, 0.1)))
        put(at, clang, 0.45)
        put(at, _filter(m.noise(0.08), low=200, high=1500) * np.exp(-np.arange(int(0.08 * SR)) / SR * 40), 0.6)  # the slam
        hang = int(((events["lands"] or at + 1.5) - 0.3 - at) * SR)
        creak = _filter(m.noise(hang / SR), low=400, high=1600) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.5 * np.arange(hang) / SR)) * np.exp(-np.arange(hang) / SR * 1.2)
        put(at + 0.2, creak, 0.12)  # the rim rattling while he hangs on it
        if events["lands"]:
            tt = np.arange(int(0.2 * SR)) / SR
            put(events["lands"], np.sin(2 * np.pi * 60 * tt) * np.exp(-tt * 25) + 0.3 * _filter(m.noise(0.2), low=500, high=3000) * np.exp(-tt * 40), 0.7)
            put(events["lands"] - 0.25, _swish(m, 0.3), 0.2)  # the net swings as he lets go
    return 0.8 * out / np.abs(out).max()


def record_shop_samples():
    """Rico's: a funky groove on the shop's record player (made up here), the crackle of vinyl,
    records being flipped through in the bins, the cash register ringing now and then."""
    bpm = 100
    m = _Mix(13, secs=12 * 4 * 60 / bpm)  # 12 bars
    beat = 60 / bpm
    _beat(m, bpm, 0.55, muffle=5000, kicks=(0, 1.5, 2.5))
    bass = [41.2, 41.2, 49.0, 55.0, 61.7, 55.0, 49.0, 41.2]  # E1 G1 A1 B1, a little line
    for bar in range(int((m.secs + XF) / (4 * beat)) + 1):
        for k, f in enumerate(bass):
            m.add((bar * 4 + k / 2) * beat, _tone(f * 2, 0.4, 0.18, (1, 0.5, 0.25, 0.12)), 0.35)
        for b in (0.5, 1.5, 2.5, 3.5):  # organ stabs on the offbeats
            stab = sum(_tone(f, 0.25, 0.12, (1, 0.3)) for f in (329.6, 392.0, 493.9))
            m.add((bar * 4 + b) * beat, stab, 0.08)
    m.out = _filter(m.out, high=4500)  # from the shop's speakers
    clicks = np.zeros(m.n)
    clicks[m.rng.integers(0, m.n, 220)] = m.rng.uniform(-1, 1, 220)
    m.out += 0.25 * _filter(clicks, low=1500) + 0.01 * _filter(m.rng.standard_normal(m.n), low=3000)  # crackle and hiss
    for start in (3.0, 3.25, 3.5, 11.0, 11.2, 18.0, 18.3, 18.5):  # flipping through records
        t = np.arange(int(0.12 * SR)) / SR
        m.add(start, _filter(m.noise(0.12), low=900, high=4500) * np.exp(-t * 25), 0.25)
    for start in (8.0, 25.0):  # ka-ching
        m.add(start, _filter(m.noise(0.03), low=2000), 0.4)
        m.add(start + 0.05, _tone(1800, 0.8, 0.25, (1, 0.6)) + _tone(2700, 0.8, 0.2), 0.12)
    return m.loop()


def corner_store_samples():
    """The corner store: the fridge humming, the neon lights buzzing, the door bell, the register
    beeping, cans clinking, the street muffled outside."""
    m = _Mix(14)
    t = m.t
    m.out += 0.35 * (np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t))  # the fridge
    m.out += 0.08 * _filter(m.rng.standard_normal(m.n), high=300)
    buzz = sum(np.sin(2 * np.pi * 120 * k * t) / k for k in range(2, 7))  # the lights
    m.out += 0.03 * buzz * (1 + 0.3 * np.sin(2 * np.pi * 0.13 * t))
    _street(m, 0.25)
    m.out = _filter(m.out, high=2500)
    for start in (2.0, 21.0):  # the door bell
        m.add(start, _tone(1318.5, 1.2, 0.4, (1, 0.4)), 0.25)
        m.add(start + 0.25, _tone(1046.5, 1.4, 0.5, (1, 0.4)), 0.25)
    for start in (9.0, 9.2, 9.4, 15.0, 15.2):  # the register
        m.add(start, _tone(1000, 0.09, 1.0), 0.15)
    for start in (5.0, 12.5, 26.0):  # cans
        m.add(start, _tone(3100, 0.2, 0.05, (1, 0.5)) + _tone(4300, 0.2, 0.04), 0.1)
    return m.loop()


def flash_samples():
    """Grandmaster Flash's realm: a slow cosmic pad, a deep drone, sparkles echoing, a slow
    break far, far away."""
    m = _Mix(15, secs=8 * 4 * 60 / 70)  # 8 bars of the slow break
    t = m.t
    chord = (110.0, 164.8, 196.0, 246.9, 261.6)  # A2 E3 G3 B3 C4
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * t / 10)
    m.out += swell * sum(np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.004 * t + 1) for f in chord) * 0.12
    m.out += 0.35 * np.sin(2 * np.pi * 55 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * t / 7))
    notes = (880.0, 1046.5, 1174.7, 1318.5, 1568.0)
    for start in m.rng.uniform(0, m.secs, 22):  # sparkles, with an echo
        ping = _tone(float(m.rng.choice(notes)), 1.0, 0.25)
        for k in range(4):
            m.add(start + k * 0.37, ping, 0.12 * 0.5 ** k)
    for start in (4.0, 14.0, 24.0):  # a whoosh rising
        n = int(2.5 * SR)
        m.add(start, _filter(m.noise(2.5), low=400, high=3000) * np.linspace(0, 1, n) ** 3, 0.3)
    _beat(m, 70, 0.3, muffle=900, hats=False)
    return m.loop()


AMBIENCES = {"street": street_samples, "block": block_samples, "station_gate": station_gate_samples, "record_shop": record_shop_samples,
             "corner_store": corner_store_samples, "flash": flash_samples}


def _write(path, samples):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())
    print(f"wrote {path.relative_to(path.parents[3])}")



def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(32767 * v)) for v in basement_samples()))
    print(f"wrote {OUT.relative_to(OUT.parents[3])}")
    for name, make in AMBIENCES.items():
        _write(OUT.parent / f"{name}.wav", make())
    # the block's sounds for what happens in the picture: the train, each shot on the court
    from art import build
    block = OUT.parent.parent / "block"
    block.mkdir(exist_ok=True)
    _write(block / "train.wav", train_samples(build.BLOCK_TRAIN[0]))
    build.block_scene()
    for name, events in build.SHOT_SOUNDS.items():
        _write(block / f"{name}.wav", shot_samples(events))
    station = OUT.parent.parent / "station"
    station.mkdir(exist_ok=True)
    _write(station / "unlock.wav", unlock_samples(build.UNLOCK_SOUNDS, build.UNLOCK_AT, build.UNLOCK_SECS))


if __name__ == "__main__":
    main()
