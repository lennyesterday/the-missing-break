"""Shared building blocks for every scene: graffiti, the el train, the street."""

import math

from art.fonts import text_width

FONT = "Impact, 'Arial Black', sans-serif"  # signs, flyers, labels
GRAFFITI_FONT = "'Sedgwick Ave Display', Impact, 'Arial Black', sans-serif"  # pieces
TAG_FONT = "'Sedgwick Ave', 'Marker Felt', cursive"  # tags

SUNSET = (("0", "#e9733a"), ("0.55", "#f4b44a"), ("1", "#f9dd98"))
DUSK = (("0", "#1f1238"), ("0.5", "#7a3170"), ("1", "#f08a4b"))


def defs(sky=SUNSET, extra=""):
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in sky)
    return f'''  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>
    <linearGradient id="gPinkYellow" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffe14d"/><stop offset="0.5" stop-color="#ff8a3d"/><stop offset="1" stop-color="#ff3d8b"/>
    </linearGradient>
    <linearGradient id="gBlueGreen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7ef0ff"/><stop offset="0.5" stop-color="#3fa9f5"/><stop offset="1" stop-color="#2ecc71"/>
    </linearGradient>
    <linearGradient id="gOrangeRed" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff07a"/><stop offset="0.5" stop-color="#ff6b2b"/><stop offset="1" stop-color="#c0392b"/>
    </linearGradient>
    <linearGradient id="gPurple" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f3a6ff"/><stop offset="1" stop-color="#7d3cff"/>
    </linearGradient>
    <linearGradient id="gWhite" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#e8e8e8"/><stop offset="1" stop-color="#9fd3ff"/>
    </linearGradient>
    <linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff4a8"/><stop offset="0.5" stop-color="#ffd23f"/><stop offset="1" stop-color="#e8962a"/>
    </linearGradient>
    <linearGradient id="gSteel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f4f4f4"/><stop offset="0.5" stop-color="#a7adb5"/><stop offset="1" stop-color="#4a4f57"/>
    </linearGradient>
    <pattern id="bricks" width="40" height="20" patternUnits="userSpaceOnUse">
      <rect width="40" height="20" fill="#8a4030"/>
      <path d="M0 0H40M0 10H40M20 0V10M0 10V20M40 10V20" stroke="#6a2e20" stroke-width="2"/>
    </pattern>
    <pattern id="awning" width="40" height="40" patternUnits="userSpaceOnUse">
      <rect width="20" height="40" fill="#c0392b"/>
      <rect x="20" width="20" height="40" fill="#f4f4f4"/>
    </pattern>
    <pattern id="lattice" width="24" height="18" patternUnits="userSpaceOnUse">
      <rect width="24" height="18" fill="#34463a"/>
      <path d="M0 0L24 18M24 0L0 18" stroke="#22302a" stroke-width="2.5"/>
    </pattern>
    <pattern id="chainlink" width="16" height="16" patternUnits="userSpaceOnUse">
      <path d="M0 0L16 16M16 0L0 16" stroke="#8a8f99" stroke-width="1.5"/>
    </pattern>
    <pattern id="shutter" width="10" height="6" patternUnits="userSpaceOnUse">
      <rect width="10" height="6" fill="#8d9097"/><path d="M0 5.5H10" stroke="#6d7078" stroke-width="1"/>
    </pattern>
{extra}  </defs>
'''


def _bounce(text, size):
    """Letters that bounce and lean a little, like a hand-painted piece (still easy to read).
    Small pieces bounce less, so they stay readable."""
    tilt = ("-4", "3", "-2", "4", "-3", "2") if size >= 30 else ("-2", "1", "-1", "2", "-1", "1")
    lift = max(1, round(size * 0.05))
    rotate = " ".join(tilt[i % len(tilt)] for i in range(len(text)))
    dy = " ".join("0" if i == 0 else (str(lift) if i % 2 else str(-lift)) for i in range(len(text)))
    return f'rotate="{rotate}" dy="{dy}"'


def _piece_layers(x, y, plain, main_fill, size, rot, shadow, anchor, cloud):
    """The layers of a piece, back to front: outer outline, 3D block, the coloured letters with
    their black outline, and a thin shine. The outer outline is white on big pieces and dark on
    small ones, so small light letters don't run into it."""
    if cloud is None:
        cloud = "#f4f4f4" if size >= 30 else "#1a1030"
    t = (f'font-family="{GRAFFITI_FONT}" font-size="{size:.1f}" letter-spacing="1" '
         f'text-anchor="{anchor}" {_bounce(plain, size)}')
    outline = max(2.5, round(size * 0.11, 1))
    depth = max(1.5, round(size * 0.045, 1))
    steps = 4
    cloud_width = outline + 2 * max(3, round(size * 0.12, 1))
    far = steps * depth
    out = [f'<g transform="rotate({rot} {x} {y})">']
    for dx in (0, far):  # the white outline goes around the letters and their 3D block
        out.append(f'<text class="cloud" x="{x + dx}" y="{y + dx}" {t} fill="{cloud}" stroke="{cloud}" '
                   f'stroke-width="{cloud_width:.1f}" stroke-linejoin="round">{plain}</text>')
    for k in range(steps, 0, -1):
        out.append(f'<text class="block" x="{x + k * depth:.1f}" y="{y + k * depth:.1f}" {t} fill="{shadow}" '
                   f'stroke="{shadow}" stroke-width="{outline}" stroke-linejoin="round">{plain}</text>')
    out.append(f'<text x="{x}" y="{y}" {t} {main_fill[0]} stroke="#111" stroke-width="{outline}" '
               f'stroke-linejoin="round" paint-order="stroke">{main_fill[1]}</text>')
    out.append(f'<text x="{x - 0.8}" y="{y - 0.8}" {t} fill="none" stroke="#fff" stroke-width="0.9" opacity="0.6">{plain}</text>')
    out.append("</g>")
    return "".join(out)


def _fit(text, size, fit):
    """Shrink the size so the text is at most fit px wide."""
    if fit:
        size = min(size, size * fit / text_width(text, size))
    return size


def piece(x, y, word, grad, size=40, rot=0, shadow="#111", anchor="start", fit=None, cloud=None):
    """A graffiti piece: graffiti letters that bounce, a black outline, a 3D block, a white outer
    outline and a colour fade. fit: the most px it may be wide (it shrinks to fit)."""
    size = _fit(word, size, fit)
    return _piece_layers(x, y, word, (f'fill="url(#{grad})"', word), size, rot, shadow, anchor, cloud)


def piece_parts(x, y, parts, size=24, fit=None, cloud=None):
    """A piece over a whole line with a colour fade per part. parts: (text, gradient id) in order."""
    plain = "".join(text for text, _ in parts)
    size = _fit(plain, size, fit)
    spans = "".join(f'<tspan fill="url(#{grad})">{text}</tspan>' for text, grad in parts)
    return _piece_layers(x, y, plain, ("", spans), size, 0, "#111", "start", cloud)


def block_text(x, y, parts, size=24, anchor="start"):
    """Readable spray-painted block letters: drop shadow, black outline, a colour per part.

    parts is a list of (text, colour) that follow each other on one line.
    """
    t = f'font-family="{FONT}" font-size="{size}" letter-spacing="1" text-anchor="{anchor}"'
    plain = "".join(text for text, _ in parts)
    spans = "".join(f'<tspan fill="{color}">{text}</tspan>' for text, color in parts)
    return (f'<text class="label" x="{x + 3}" y="{y + 3}" {t} fill="#111" stroke="#111" stroke-width="5" stroke-linejoin="round">{plain}</text>'
            f'<text class="label" x="{x}" y="{y}" {t} stroke="#111" stroke-width="4" stroke-linejoin="round" paint-order="stroke">{spans}</text>')


def tag(x, y, word, color, size=16, rot=-6):
    """A quick handwritten tag."""
    return (f'<text class="tag" x="{x}" y="{y}" font-family="{TAG_FONT}" font-size="{size}" '
            f'fill="{color}" transform="rotate({rot} {x} {y})">{word}</text>')


def spinning_record(cx, cy, r, label="#ff4f79", tilt=0.25, secs=1.8):
    """A record turning on a platter, seen at an angle. The disc is drawn round, turns around its
    own centre, and is then squashed into the tilt, so its outline stays still and only the
    grooves and the label go round (33 rpm is about 1.8 s per turn). The shine stays still."""
    grooves = "".join(f'<circle r="{r * k:.1f}" fill="none" stroke="#2c2c2c" stroke-width="1.2"/>' for k in (0.85, 0.7, 0.55))
    return (f'<g class="spinning-record" transform="translate({cx} {cy}) scale(1 {tilt})">'
            f'<circle r="{r}" fill="#111" stroke="#3a3a3a" stroke-width="1.5"/>'
            f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{secs}s" repeatCount="indefinite"/>'
            f'{grooves}<circle r="{r * 0.32:.1f}" fill="{label}"/>'
            f'<rect x="-1.2" y="{-r * 0.32:.1f}" width="2.4" height="{r * 0.2:.1f}" fill="#f4f4f4"/>'
            f'<path d="M{r * 0.45:.1f} 0H{r * 0.82:.1f}" stroke="#4a4a4a" stroke-width="2"/></g>'
            f'<path d="M{-r * 0.75:.1f} {-r * 0.35:.1f}A{r * 0.8:.1f} {r * 0.8:.1f} 0 0 1 {-r * 0.2:.1f} {-r * 0.78:.1f}" '
            f'stroke="#f4f4f4" stroke-width="2" fill="none" opacity="0.35"/>'
            f'<circle r="1.6" fill="#c9ccd2"/></g><!-- end record -->')


def star(cx, cy, r, color):
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy - rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="#111" stroke-width="2"/>'


def _car(x, word, grad, extras="", front=False, offset=10, width=280, centred=False, size=38):
    """One stainless 70s subway car, covered top to bottom with a piece."""
    k = width / 280
    windows = "".join(f'<rect x="{x + wx * k:.0f}" y="76" width="26" height="17" rx="2" fill="#2b3440"/>'
                      for wx in (14, 48, 196, 230))
    doors = "".join(f'<rect x="{x + dx * k:.0f}" y="73" width="32" height="51" fill="#a6a9b0" stroke="#6d7078" stroke-width="1.5"/>'
                    f'<rect x="{x + dx * k + 4:.0f}" y="77" width="10" height="17" fill="#2b3440"/>'
                    f'<rect x="{x + dx * k + 18:.0f}" y="77" width="10" height="17" fill="#2b3440"/>'
                    for dx in (88, 152))
    wheels = "".join(f'<circle cx="{x + wx * k:.0f}" cy="134" r="6" fill="#222"/>' for wx in (28, 56, 224, 252))
    sign = "" if not front else (
        f'<rect x="{x - 4}" y="72" width="8" height="52" fill="#8d9097"/>'
        f'<circle cx="{x + 27}" cy="85" r="9" fill="#d02b2b" stroke="#111" stroke-width="1.5"/>'
        f'<text x="{x + 27}" y="90" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#fff" text-anchor="middle">2</text>')
    return (f'<g>'
            f'<rect x="{x}" y="68" width="{width}" height="60" rx="6" fill="#c3c6cc" stroke="#555" stroke-width="2"/>'
            f'<path d="M{x + 4} 71H{x + width - 4}" stroke="#e6e8ec" stroke-width="2"/>'
            f'{windows}{doors}{sign}{extras}'
            + (piece(x + width / 2, 118, word, grad, size=size, rot=-2, anchor="middle", fit=width - 24) if centred
               else piece(x + offset, 118, word, grad, size=size, rot=-2, fit=width - offset - 14))
            + f'<rect x="{x}" y="126" width="{width}" height="6" fill="#3a3a3a"/>{wheels}'
            f'</g>')


def train(dur="7s", every=None, at=0):
    """Three graffiti-covered cars on the el, passing right to left on a loop. every (seconds):
    it passes in dur, then the el is empty until the next one comes; at: it comes this many
    seconds into each round (until then the el is empty)."""
    cars = (
        _car(0, "PORTALS", "gPinkYellow", extras=star(250, 88, 12, "#ffd23f") + tag(196, 118, "Portals 77", "#111", 13),
             front=True, offset=44)
        + _car(288, "BRONX", "gBlueGreen",
               extras=star(510, 92, 14, "#ff4f79") + star(540, 106, 9, "#7ed957") + tag(440, 120, "Needle", "#c0392b", 15)
               + '<path d="M496 82L556 82L548 74M556 82L548 90" stroke="#111" stroke-width="4" fill="none"/>')
        + _car(576, "THINK ABOUT IT", "gOrangeRed", extras=tag(800, 120, "Sopranos", "#111", 12, rot=-4), size=29)
    )
    if every and at:
        secs = float(dur.rstrip("s"))
        move = (f'<animateTransform attributeName="transform" type="translate" values="820 0;820 0;-900 0;-900 0" '
                f'keyTimes="0;{at / every:.4f};{(at + secs) / every:.4f};1" dur="{every}s" repeatCount="indefinite"/>')
    elif every:
        move = (f'<animateTransform attributeName="transform" type="translate" values="820 0;-900 0;-900 0" '
                f'keyTimes="0;{float(dur.rstrip("s")) / every:.4f};1" dur="{every}s" repeatCount="indefinite"/>')
    else:
        move = f'<animateTransform attributeName="transform" type="translate" values="820 0;-900 0" dur="{dur}" repeatCount="indefinite"/>'
    return f'''  <!-- the passing train, looping. It runs on the el behind the street. -->
  <g>
    {move}
    {cars}
  </g>
'''


def button_train(arrive_secs=2.6):
    """The home screen's train: it pulls in and stops, and its three pieces are the buttons.

    Each car is a group with data-action; the app's home screen component makes them clickable.
    """
    width, gap = 256, 8
    cars = [
        ("start", "START", "gPinkYellow", "Start a new game",
         star(width - 30, 88, 11, "#ffd23f") + tag(14, 120, "Portals 77", "#111", 12)),
        ("resume", "RESUME", "gBlueGreen", "Resume your saved game",
         star(width + gap + 30, 90, 10, "#ff4f79") + tag(width + gap + 170, 121, "Needle", "#c0392b", 13)),
        ("menu", "MENU", "gOrangeRed", "Menu (coming soon)",
         f'<g transform="rotate(8 {2 * (width + gap) + 210} 92)">'
         f'<rect x="{2 * (width + gap) + 182}" y="80" width="58" height="22" rx="3" fill="#ffd23f" stroke="#111" stroke-width="2"/>'
         f'<text x="{2 * (width + gap) + 211}" y="97" font-family="{FONT}" font-size="15" fill="#111" text-anchor="middle">SOON</text></g>'),
    ]
    groups = "".join(
        f'<g data-action="{action}" role="button" tabindex="0" aria-label="{label}">'
        f'<title>{label}</title>'
        + _car(i * (width + gap), word, grad, extras=extras, front=(i == 0), width=width, centred=True, size=42)
        + '</g>'
        for i, (action, word, grad, label, extras) in enumerate(cars))
    stop_x = (800 - (3 * width + 2 * gap)) // 2
    return f'''  <!-- the train pulls in and stops: its pieces are the START / RESUME / MENU buttons -->
  <g>
    <animateTransform attributeName="transform" type="translate" values="820 0;{stop_x} 0" keyTimes="0;1"
      calcMode="spline" keySplines="0.15 0.6 0.3 1" dur="{arrive_secs}s" fill="freeze"/>
    {groups}
  </g>
'''


def el(columns=(290, 510)):
    """Elevated subway structure: lattice deck girder and its columns."""
    cols = "".join(f'<rect x="{x}" y="156" width="14" height="190"/>' for x in columns)
    return f'''  <!-- elevated subway structure -->
  <rect x="0" y="134" width="800" height="22" fill="url(#lattice)"/>
  <rect x="0" y="132" width="800" height="5" fill="#22302a"/>
  <rect x="0" y="154" width="800" height="4" fill="#22302a"/>
  <g fill="#34463a" stroke="#22302a" stroke-width="2">{cols}</g>
'''


def skyline(body="#9a5a45", tower="#7a4434", opacity=0.55, windows=False):
    """Far skyline with water towers."""
    lit = "" if not windows else "".join(
        f'<rect x="{x}" y="{y}" width="6" height="8" fill="#ffd98a" opacity="0.8"/>'
        for x, y in ((20, 60), (60, 90), (130, 50), (150, 80), (220, 75), (280, 100), (350, 55), (390, 85),
                     (460, 80), (500, 110), (570, 60), (620, 95), (700, 70), (760, 100)))
    return f'''  <!-- far skyline with water towers -->
  <g fill="{body}" opacity="{opacity}">
    <rect x="0" y="40" width="110" height="160"/><rect x="100" y="20" width="80" height="180"/>
    <rect x="190" y="50" width="120" height="150"/><rect x="330" y="30" width="90" height="170"/>
    <rect x="430" y="55" width="100" height="145"/><rect x="540" y="35" width="120" height="165"/>
    <rect x="670" y="45" width="130" height="155"/>
  </g>
  {lit}
  <g fill="{tower}" opacity="0.7">
    <path d="M128 20V8Q140 0 152 8V20Z"/><path d="M131 20L128 28M149 20L152 28" stroke="{tower}" stroke-width="2"/>
    <path d="M360 30V16Q373 8 386 16V30Z"/>
    <path d="M700 45V31Q712 23 724 31V45Z"/>
  </g>
'''


def street(extra=""):
    """Sidewalk (top at y=340, the crew stands on it) and the street."""
    return f'''  <!-- sidewalk and street -->
  <rect y="340" width="800" height="40" fill="#9a9aa2"/>
  <path d="M0 340H800" stroke="#6e6e76" stroke-width="3"/>
  <g stroke="#7d7d85" stroke-width="2"><path d="M80 340V380M200 340V380M320 340V380M440 340V380M560 340V380M680 340V380"/></g>
  <rect y="380" width="800" height="70" fill="#3a3a42"/>
  <path d="M0 415H800" stroke="#d9c24a" stroke-width="4" stroke-dasharray="30 20"/>
  {extra}
'''
