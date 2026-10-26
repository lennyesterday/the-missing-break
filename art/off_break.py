"""Makes Needle's first try at looping the break of "Think (About It)": always off. It is cut
from the drum break (static/audio/records/think_about_it_break.wav): every take starts the break
again, but he lets it run too short or too long, or drops the needle a little late, spins the
record back with a scratch, and at the end the record winds down and stops.

    uv run python -m art.off_break

The picture (art/build.py) uses TAKES too: the record jumps back and OFF! pops up at every cut.
"""

import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "static" / "audio" / "records" / "think_about_it_break.wav"
OUT = ROOT / "static" / "audio" / "records" / "think_about_it_off.wav"
LOOP = 4.199  # one 2-bar loop of the break (logic.SONGS["think_about_it_break"]["loop_secs"])

# (where in the break he drops the needle, how long he lets it run): never one clean loop
TAKES = [(0.0, 3.25), (0.35, 4.45), (0.0, 2.55), (0.6, 2.2), (0.0, 1.5)]
SCRATCH = 0.22  # the spin back between two takes
STOP = 0.9  # the record winding down at the end


def takes_timeline():
    """When each cut comes, in seconds from the start: the record jumps back (and OFF!) then."""
    t, cuts = 0.0, []
    for _, secs in TAKES:
        t += secs
        cuts.append(round(t, 2))
        t += SCRATCH
    return cuts


def total_secs():
    return sum(secs for _, secs in TAKES) + SCRATCH * (len(TAKES) - 1) + STOP


def _read():
    with wave.open(str(SOURCE)) as w:
        rate, channels = w.getframerate(), w.getnchannels()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, channels)
    return rate, data.astype(np.float32) / 32768


def _fade(x, rate, ms=6):
    n = min(len(x) // 2, int(rate * ms / 1000))
    ramp = np.linspace(0, 1, n)[:, None]
    x = x.copy()
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x


def _resample(x, speeds):
    """x played at a speed that changes along the way (speeds: one per output sample)."""
    pos = np.cumsum(speeds)
    pos = pos[pos < len(x) - 1]
    i = pos.astype(int)
    f = (pos - i)[:, None]
    return x[i] * (1 - f) + x[i + 1] * f


def off_break():
    rate, data = _read()
    parts = []
    for k, (start, secs) in enumerate(TAKES):
        a, b = int(start * rate), int((start + secs) * rate)
        take = data[a:b]
        if k == len(TAKES) - 1:  # the last take: the record winds down and stops
            stop = data[b:b + int(STOP * 1.2 * rate)]
            n = int(STOP * rate)
            wound = _resample(stop, np.linspace(1.0, 0.0, n) ** 1.5)
            wound *= np.linspace(1, 0, len(wound))[:, None]
            parts += [_fade(take, rate), wound, np.zeros((n - len(wound), data.shape[1]), np.float32)]
            continue
        # the spin back: the end of the take, backwards and fast (a scratch), a bit quieter
        n = int(SCRATCH * rate)
        back = take[::-1][: int(n * 2.4)]
        scratch = _resample(back, np.concatenate([np.linspace(1.2, 3.2, n // 2), np.linspace(3.2, 0.6, n - n // 2)]))
        scratch = np.pad(scratch, ((0, n - len(scratch)), (0, 0)))[:n] * 0.6
        parts += [_fade(take, rate), _fade(scratch, rate, 3)]
    out = np.clip(np.concatenate(parts), -1, 1)
    return rate, (out * 32767).astype(np.int16)


def main():
    rate, samples = off_break()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(samples.shape[1])
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(samples.tobytes())
    print(f"wrote {OUT.relative_to(ROOT)} ({len(samples) / rate:.2f} s)")


if __name__ == "__main__":
    main()
