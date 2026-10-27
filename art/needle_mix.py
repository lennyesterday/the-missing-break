"""Makes Needle's set at the Borough DJ Battle (static/audio/records/needle_mix.wav): he cuts from
break to break through the classics on the basement floor, two bars of each at its own tempo with
a quick scratch between them, then spins the record back and "Think (About It)" drops: its drum
break, three times round its 2-bar loop.

    uv run python -m art.needle_mix

The mp3s are decoded with afconvert (macOS). The picture (art/build.py) uses timeline() too: the
sign over the booth changes at every cut, the club goes off at the drop.
"""

import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

from art.off_break import _fade, _resample

ROOT = Path(__file__).resolve().parent.parent
RECORDS = ROOT / "static" / "audio" / "records"
OUT = RECORDS / "needle_mix.wav"
BREAK = RECORDS / "think_about_it_break.wav"
LOOP = 4.199  # one 2-bar loop of the break (logic.SONGS["think_about_it_break"]["loop_secs"])

# (the record, where in it the 2 bars start (on a beat), one beat in seconds, how many beats);
# found by looking for the drums, each starting just before a hit
MIX = [
    ("apache", 132.708, 0.5253, 8),                # the break
    ("funky_drummer", 131.971, 0.6078, 8),         # the break
    ("its_just_begun", 134.844, 0.5035, 8),        # the break
    ("the_mexican", 77.476, 0.5336, 8),
    ("vitamin_c", 109.274, 0.4992, 8),
    ("impeach_the_president", 1.221, 0.6251, 8),   # the drums at the start
]
SCRATCH = 0.22  # the spin back between two breaks
REWIND = 0.6  # the rewind before the drop ...
HUSH = 0.3  # ... and a moment of silence
DROP_LOOPS = 3  # "Think (About It)" goes round its loop this many times


def timeline():
    """(record, from, to) in seconds into the set, the last one "Think (About It)"."""
    t, cuts = 0.0, []
    for k, (song, _, beat, beats) in enumerate(MIX):
        cuts.append((song, round(t, 3), round(t + beat * beats, 3)))
        t += beat * beats + (SCRATCH if k < len(MIX) - 1 else 0)
    t += REWIND + HUSH
    cuts.append(("think_about_it", round(t, 3), round(t + LOOP * DROP_LOOPS, 3)))
    return cuts


def drop_at():
    return timeline()[-1][1]


def total_secs():
    return timeline()[-1][2]


def _read(path):
    with wave.open(str(path)) as w:
        rate, channels = w.getframerate(), w.getnchannels()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, channels)
    return rate, data.astype(np.float32) / 32768


def _decoded(song, folder):
    """The record as 44.1 kHz stereo samples (afconvert decodes the mp3)."""
    wav = Path(folder) / f"{song}.wav"
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@44100", "-c", "2", str(RECORDS / f"{song}.mp3"), str(wav)],
                   check=True)
    return _read(wav)


def _level(x, rms):
    """x at the loudness rms (so no break is louder than the others)."""
    return x * (rms / max(float(np.sqrt(np.mean(x ** 2))), 1e-6))


def _spin_back(x, rate, secs, top=3.2, end=0.6):
    """The end of x backwards and fast (a scratch), a bit quieter: secs long."""
    n = int(secs * rate)
    back = x[::-1][: int(n * 2.4)]
    out = _resample(back, np.concatenate([np.linspace(1.2, top, n // 2), np.linspace(top, end, n - n // 2)]))
    return _fade(np.pad(out, ((0, n - len(out)), (0, 0)))[:n] * 0.6, rate, 3)


def needle_mix():
    rate, drop = _read(BREAK)
    rms = float(np.sqrt(np.mean(drop ** 2)))
    parts = []
    with tempfile.TemporaryDirectory() as folder:
        for k, (song, start, beat, beats) in enumerate(MIX):
            r, data = _decoded(song, folder)
            assert r == rate
            a = int(start * rate)
            piece = _level(data[a:a + int(beat * beats * rate)], rms)
            parts.append(_fade(piece, rate))
            if k < len(MIX) - 1:
                parts.append(_spin_back(piece, rate, SCRATCH))
            else:  # the rewind before the drop, then a moment of silence
                parts += [_spin_back(piece, rate, REWIND, top=4.0, end=1.5),
                          np.zeros((int(HUSH * rate), data.shape[1]), np.float32)]
    loops = np.concatenate([drop[: int(LOOP * rate)]] * DROP_LOOPS)
    loops[-int(0.5 * rate):] *= np.linspace(1, 0, int(0.5 * rate))[:, None]  # it fades at the very end
    parts.append(loops)
    out = np.clip(np.concatenate(parts), -1, 1)
    # exactly as long as the timeline says (rounding of each piece)
    n = int(round(total_secs() * rate))
    out = np.pad(out, ((0, max(0, n - len(out))), (0, 0)))[:n]
    return rate, (out * 32767).astype(np.int16)


def main():
    rate, samples = needle_mix()
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(samples.shape[1])
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(samples.tobytes())
    print(f"wrote {OUT.relative_to(ROOT)} ({len(samples) / rate:.2f} s, the drop at {drop_at():.2f} s)")


if __name__ == "__main__":
    main()
