"""The five crew members, drawn side-on facing right. Origin of each figure is the hip.

Every member keeps the same look and props everywhere (specs/scene-art.md).
`motion=Walk(...)` makes them walk to the right; `motion=None` makes them stand,
and `idle` says how: "nod" to the beat (default), "still", or "angry" (shaking).
"""

import math
from dataclasses import dataclass

from art.scenery import FONT, spinning_record

HIP_Y = 327  # hips at this height put the feet on the sidewalk
FEET_Y = HIP_Y + 48  # where the soles are
HEAD_ABOVE_FEET = FEET_Y - (HIP_Y - 64)  # from the soles up to the middle of the head


@dataclass(frozen=True)
class Walk:
    dist: int  # how far to the right they walk
    secs: float  # how long it takes
    stride: float = 1.0  # seconds per stride: 1 is walking, about 0.4 is running


SWING_A, SWING_B = "0;25;0;-25;0", "0;-25;0;25;0"
ARM_A, ARM_B = "0;30;0;-30;0", "0;-30;0;30;0"
LEATHER = "#161616"


def _rot(values, motion):
    if motion is None:
        return ""
    return (f'<animateTransform attributeName="transform" type="rotate" values="{values}" '
            f'dur="{motion.stride}s" repeatCount="{motion.secs / motion.stride:g}" additive="sum"/>')


def _repeat(motion):
    """Props that loop (music notes, spray mist) play for the walk, or forever when idle."""
    return 'repeatCount="indefinite"' if motion is None else f'repeatDur="{motion.secs}s"'


def _leg(values, motion, trouser, shoe, shoe_extra=""):
    """A leg: the trouser with a crease, the shoe with its sole and a lace."""
    sole = "#9a9aa2" if shoe.lower() in ("#f4f4f4", "#ffffff") else "#e6e6e6"
    return (f'<g>{_rot(values, motion)}<rect x="-6" y="0" width="12" height="44" rx="5" fill="{trouser}"/>'
            '<path d="M2 6V38" stroke="#000" stroke-width="1.5" opacity="0.18"/>'
            f'<rect x="-6" y="40" width="20" height="8" rx="3" fill="{shoe}"/>'
            f'<rect class="sole" x="-6" y="46" width="20" height="2.5" rx="1" fill="{sole}"/>'
            f'<path d="M2 41L6 43" stroke="{sole}" stroke-width="1.2"/>{shoe_extra}</g>')


def _arm(values, motion, sleeve, skin, hand_extra="", shade=False):
    extra = '<rect x="-5" y="0" width="10" height="38" rx="5" fill="#000" opacity="0.25"/>' if shade else ""
    return (f'<g transform="translate(0 -44)">{_rot(values, motion)}'
            f'<rect x="-5" y="0" width="10" height="38" rx="5" fill="{sleeve}"/>{extra}'
            '<path d="M-5 33H5" stroke="#000" stroke-width="1.5" opacity="0.2"/>'
            f'{hand_extra}<circle cy="40" r="6" fill="{skin}"/><circle cx="4" cy="37" r="2.2" fill="{skin}" stroke="#000" stroke-opacity="0.2" stroke-width="0.8"/></g>')


def _figure(name, x0, phase, motion, top, trouser, shoe, skin, head, torso_extra="", behind="",
            front_arm=None, front="", shoe_extra="", y0=HIP_Y, idle="nod"):
    legs = (SWING_A, SWING_B) if phase else (SWING_B, SWING_A)
    arms = (ARM_A, ARM_B) if phase else (ARM_B, ARM_A)  # arms swing against the legs
    if front_arm is None:
        front_arm = _arm(arms[1], motion, top, skin)
    if motion is None:
        travel = ""
        bob = {
            "nod": '<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="0.5s" repeatCount="indefinite"/>',
            "angry": '<animateTransform attributeName="transform" type="translate" values="0 0;-2 0;2 0;-2 0;0 0" dur="0.35s" repeatCount="indefinite"/>',
            "still": "",
        }[idle]
    else:
        travel = (f'<animateTransform attributeName="transform" type="translate" from="0 0" '
                  f'to="{motion.dist} 0" dur="{motion.secs}s" fill="freeze"/>')
        bob = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" '
               f'dur="{motion.stride / 4:g}s" repeatCount="{4 * motion.secs / motion.stride:g}"/>')
    return f"""
  <!-- {name} -->
  <g transform="translate({x0} {y0})"><g>
    {travel}
    <g>
      {bob}
      {_arm(arms[0], motion, top, skin, shade=True)}
      {_leg(legs[1], motion, trouser, shoe, shoe_extra)}
      {_leg(legs[0], motion, trouser, shoe, shoe_extra)}
      {behind}
      <path d="M-17 -48H17L15 4H-15Z" fill="{top}"/>
      <path class="shade" d="M-17 -48H-9L-9 4H-15Z" fill="#000" opacity="0.16"/>
      <path d="M14 -44L12.5 0" stroke="#fff" stroke-width="2.5" opacity="0.13"/>
      <rect class="belt" x="-15" y="-3" width="30" height="5" fill="#000" opacity="0.3"/>
      <ellipse cx="0" cy="-47" rx="11" ry="3" fill="#000" opacity="0.18"/>
      {torso_extra}
      {front_arm}
      {head}
      {front}
    </g>
  </g></g>
"""


def _face(skin, eye_y=-64, cy=-64, r=16):
    """A head in profile, looking right: the back of it in shadow, an ear, a nose, an eye with a
    glint, a brow and a mouth."""
    return (f'<circle cx="0" cy="{cy}" r="{r}" fill="{skin}"/>'
            f'<path class="shade" d="M0 {cy - r}A{r} {r} 0 0 0 0 {cy + r}A{r * 0.55:.1f} {r} 0 0 1 0 {cy - r}Z" fill="#000" opacity="0.16"/>'
            f'<path d="M{r - 1} {eye_y + 1}Q{r + 3.5} {eye_y + 4} {r - 0.5} {eye_y + 6.5}" fill="{skin}"/>'
            f'<g class="ear"><circle cx="-3" cy="{cy + 2}" r="4.2" fill="{skin}"/><path d="M-4 {cy}Q-1 {cy + 2} -4 {cy + 4}" stroke="#000" stroke-width="1" opacity="0.3" fill="none"/></g>'
            f'<circle cx="9" cy="{eye_y}" r="2" fill="#111"/><circle cx="9.7" cy="{eye_y - 0.7}" r="0.6" fill="#fff"/>'
            f'<path class="brow" d="M5.5 {eye_y - 4.5}L12.5 {eye_y - 5.5}" stroke="#111" stroke-width="1.8" stroke-linecap="round"/>'
            f'<path class="mouth" d="M7 {eye_y + 10}Q10.5 {eye_y + 11.5} 13.5 {eye_y + 9.5}" stroke="#2a1208" stroke-width="1.5" fill="none" stroke-linecap="round"/>')


def _leather(shirt):
    """Black leather jacket: collar, open front showing the shirt, zip and shine."""
    return (f'<path d="M-7 -48L0 -34L7 -48Z" fill="{shirt}"/>'
            '<path d="M-11 -48L-1 -32M11 -48L1 -32" stroke="#3a3a3a" stroke-width="3"/>'
            '<path d="M3 -32V2" stroke="#8a8a8a" stroke-width="1.5"/>'
            '<path d="M-13 -42Q-15 -22 -12 -2" stroke="#4a4a4a" stroke-width="2" fill="none"/>')


_SHORT_HAIR = '<path d="M-16 -68Q0 -88 16 -68Z" fill="#1e1410"/>'


def bible(x0, motion=None, book=True, idle="nod", shooting_arm=None):
    """MC Bible: black leather jacket over a green shirt, jeans, his rhyme book.

    book=False: he doesn't have it (it is still on the couch), and points ahead instead.
    shooting_arm: his hands are free, he shoots hoops (the arm that goes up for the shot).
    """
    holding = (
        '<path d="M2 -42L10 -22L16 -12" stroke="#161616" stroke-width="10" stroke-linecap="round" fill="none"/>'
        '<g transform="rotate(-4 18 -26)">'
        '<rect x="-2" y="-50" width="40" height="48" rx="3" fill="#7a2e1f" stroke="#111" stroke-width="2"/>'
        '<rect x="-2" y="-50" width="6" height="48" fill="#4f1d13"/>'
        '<rect x="5" y="-45" width="31" height="34" fill="none" stroke="#ffd23f" stroke-width="1.2"/>'
        f'<text x="20.5" y="-31" font-family="{FONT}" font-size="11" fill="#ffd23f" text-anchor="middle">RHYME</text>'
        f'<text x="20.5" y="-18" font-family="{FONT}" font-size="11" fill="#ffd23f" text-anchor="middle">BOOK</text>'
        '</g>'
        '<circle cx="14" cy="-4" r="6" fill="#7a4a2e"/>'
    )
    pointing = ('<path d="M2 -42L20 -46L38 -52" stroke="#161616" stroke-width="10" stroke-linecap="round" fill="none"/>'
                '<circle cx="40" cy="-53" r="6" fill="#7a4a2e"/>')
    if shooting_arm:
        arm, what = shooting_arm, ", shooting)"
    elif book:
        arm, what = holding, ", rhyme book)"
    elif motion is None:
        arm, what = pointing, ", pointing)"
    else:
        arm, what = None, ")"  # walking without his book: his arm swings like the others'
    return _figure("MC Bible (black leather jacket" + what, x0, True, motion,
                   LEATHER, "#2d4f8a", "#f4f4f4", "#7a4a2e", _face("#7a4a2e") + _SHORT_HAIR,
                   torso_extra=_leather("#2e8b57"), front_arm=arm, idle=idle)


def bible_either(x0, motion=None, idle="still", hide_when=None):
    """MC Bible twice: with his rhyme book (shown while the crew has it, "has-rhyme_book")
    and without it ("lacks-rhyme_book"). The app shows the right one.
    hide_when: a part of the picture during which he is somewhere else (e.g. on the mic)."""
    away = f" !{hide_when}" if hide_when else ""
    return (f'<g data-overlay="lacks-rhyme_book{away}" style="display:none">{bible(x0, motion, book=False, idle=idle)}</g>'
            f'<g data-overlay="has-rhyme_book{away}" style="display:none">{bible(x0, motion, book=True, idle=idle)}</g>'
            "\n  <!-- end bible-book -->")


def bible_choking(x0):
    """MC Bible at the mic without his rhyme book: he has forgotten his bars. The mic at his mouth,
    the other hand scratching his head, sweat running down, "UHH..." in a little bubble."""
    mic = ('<path d="M2 -44L16 -58L14 -66" stroke="#161616" stroke-width="10" stroke-linecap="round" fill="none"/>'
           '<circle cx="14" cy="-67" r="6" fill="#7a4a2e"/>'
           '<rect x="16" y="-74" width="6" height="14" rx="2" fill="#2a2a2a" transform="rotate(-60 19 -67)"/>'
           '<circle cx="26" cy="-72" r="5.5" fill="#c9ccd2" stroke="#555" stroke-width="1.2"/>')
    scratch = ('<g><animateTransform attributeName="transform" type="rotate" values="0 -6 -42;8 -6 -42;0 -6 -42" '
               'dur="0.4s" repeatCount="indefinite"/>'
               '<path d="M-6 -42L-22 -58L-14 -80" stroke="#161616" stroke-width="10" stroke-linecap="round" fill="none"/>'
               '<circle cx="-13" cy="-82" r="6" fill="#7a4a2e"/></g>')
    sweat = "".join(
        f'<path d="M{x} -78q-3 5 0 7q3 -2 0 -7Z" fill="#9fd3ff" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;0" dur="1.2s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;0 18" dur="1.2s" begin="{b}s" repeatCount="indefinite"/></path>'
        for x, b in ((-14, 0), (16, 0.6)))
    uhh = ('<g><rect x="20" y="-122" width="64" height="26" rx="9" fill="#f4f4f4" stroke="#111" stroke-width="2"/>'
           '<path d="M26 -96L22 -86L34 -96Z" fill="#f4f4f4" stroke="#111" stroke-width="1.5"/>'
           '<text x="52" y="-103" font-family="Arial Black, Arial, sans-serif" font-weight="bold" font-size="13" fill="#111" text-anchor="middle">UHH...'
           '<animate attributeName="opacity" values="1;0.3;1" dur="1.4s" repeatCount="indefinite"/></text></g>')
    return _figure("MC Bible (choking at the mic, empty-handed)", x0, True, None, LEATHER, "#2d4f8a", "#f4f4f4",
                   "#7a4a2e", _face("#7a4a2e") + _SHORT_HAIR, torso_extra=_leather("#2e8b57"),
                   front_arm=mic, front=scratch + sweat + uhh, idle="still")


def bible_on_mic(x0):
    """MC Bible rapping: the mic up at his mouth, his rhyme book open in the other hand,
    nodding to the beat."""
    mic = ('<path d="M2 -44L16 -58L14 -66" stroke="#161616" stroke-width="10" stroke-linecap="round" fill="none"/>'
           '<circle cx="14" cy="-67" r="6" fill="#7a4a2e"/>'
           '<rect x="16" y="-74" width="6" height="14" rx="2" fill="#2a2a2a" transform="rotate(-60 19 -67)"/>'
           '<circle cx="26" cy="-72" r="5.5" fill="#c9ccd2" stroke="#555" stroke-width="1.2"/>')
    book = ('<path d="M-6 -42L-22 -22L-26 -10" stroke="#111" stroke-width="10" stroke-linecap="round" fill="none"/>'
            '<g transform="rotate(-18 -30 -12)">'
            '<path d="M-48 -22L-30 -18L-12 -22V-4L-30 0L-48 -4Z" fill="#f4e7c3" stroke="#111" stroke-width="1.5"/>'
            '<path d="M-30 -18V0" stroke="#7a2e1f" stroke-width="2"/>'
            '<path d="M-44 -16H-34M-44 -12H-34M-26 -16H-16M-26 -12H-16" stroke="#7a2e1f" stroke-width="1"/></g>'
            '<circle cx="-26" cy="-8" r="6" fill="#7a4a2e"/>')
    return _figure("MC Bible (on the mic, rhyme book open)", x0, True, None, LEATHER, "#2d4f8a", "#f4f4f4",
                   "#7a4a2e", _face("#7a4a2e") + _SHORT_HAIR, torso_extra=_leather("#2e8b57"),
                   front_arm=mic, front=book, idle="nod")


def portals(x0, motion=None, spraying=False, y0=HIP_Y, spray_secs=None, idle="nod"):
    """Portals: paint-splattered denim jacket, afro with headband, spray can, bag full of cans.

    spray_secs limits how long mist comes out of the can (default: while he walks, or forever).
    """
    if spraying:
        rep = f'repeatDur="{spray_secs}s"' if spray_secs else _repeat(motion)
        mist = "".join(
            f'<circle cx="{48 + dx}" cy="{-118 + dy}" r="3" fill="#ff6fa8" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.8;0" dur="0.4s" begin="{b}s" {rep}/>'
            f'<animate attributeName="r" values="2;9" dur="0.4s" begin="{b}s" {rep}/></circle>'
            for dx, dy, b in ((0, 0, 0), (6, -6, 0.13), (4, 6, 0.26)))
        front_arm = (
            '<path d="M4 -44L22 -66L30 -84" stroke="#3d6fb6" stroke-width="10" stroke-linecap="round" fill="none"/>'
            '<g transform="rotate(30 30 -92)">'
            '<rect x="25" y="-114" width="10" height="22" rx="2" fill="#ff4f79"/>'
            '<rect x="27" y="-119" width="6" height="5" fill="#222"/></g>'
            '<circle cx="30" cy="-86" r="6" fill="#5a3a24"/>' + mist)
    else:
        can = ('<rect x="-5" y="38" width="10" height="20" rx="2" fill="#ff4f79"/>'
               '<rect x="-3" y="56" width="6" height="5" fill="#222"/>')
        front_arm = _arm(ARM_A, motion, "#3d6fb6", "#5a3a24", hand_extra=can)
    return _figure(
        "Portals (denim, spray can, bag full of cans)", x0, False, motion, "#3d6fb6", "#2a2a2a", "#f4f4f4", "#5a3a24",
        '<circle cx="0" cy="-68" r="22" fill="#1e1410"/>' + _face("#5a3a24", -62, cy=-62, r=15)
        + '<path d="M-21 -72Q0 -80 21 -72" stroke="#ffd23f" stroke-width="5" fill="none"/>',
        torso_extra=('<g><circle cx="-6" cy="-30" r="3" fill="#ffd23f"/><circle cx="7" cy="-18" r="2.5" fill="#ff4f79"/>'
                     '<circle cx="-2" cy="-8" r="2" fill="#7ed957"/><circle cx="9" cy="-38" r="2" fill="#f4f4f4"/></g>'
                     '<path d="M12 -46L-14 -8" stroke="#6b4e2a" stroke-width="4"/>'),
        behind=('<rect x="-12" y="-30" width="6" height="12" rx="2" fill="#ffd23f"/>'
                '<rect x="-20" y="-32" width="6" height="14" rx="2" fill="#7ed957"/>'
                '<rect x="-28" y="-29" width="6" height="11" rx="2" fill="#3fa9f5"/>'
                '<rect x="-30" y="-20" width="26" height="24" rx="4" fill="#8b6b3a"/>'),
        front_arm=front_arm,
        y0=y0,
        idle=idle,
    )


def needle(x0, motion=None, idle="nod", front_arm=None):
    """Fantastic Needle: yellow shirt, red Kangol flat cap, red Pumas, headphones around his neck.

    idle="angry" also puts steam over his head.
    """
    steam = "" if idle != "angry" else "".join(
        f'<g opacity="0"><animate attributeName="opacity" values="0;0.9;0" dur="1.2s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} -26" dur="1.2s" begin="{b}s" repeatCount="indefinite"/>'
        f'<circle cx="{cx}" cy="-96" r="7" fill="#e8e8e8"/><circle cx="{cx + 6}" cy="-102" r="5" fill="#e8e8e8"/></g>'
        for cx, dx, b in ((-12, -8, 0), (12, 8, 0.6)))
    return _figure(
        "Fantastic Needle (red Kangol, red Pumas, headphones)", x0, True, motion, "#f2c230", "#2d4f8a", "#d02b2b",
        "#4a2e1c",
        _face("#4a2e1c", -63)
        + '<path d="M-18 -67Q-20 -84 0 -85Q20 -85 23 -73L27 -70Q14 -66 -18 -66Z" fill="#d02b2b"/>'
        + '<path d="M-16 -70Q2 -74 22 -72" stroke="#a51f1f" stroke-width="1.5" fill="none"/>',
        front=('<path d="M-12 -50Q0 -38 12 -50" stroke="#222" stroke-width="4" fill="none"/>'
               '<rect x="-17" y="-55" width="8" height="11" rx="3" fill="#222"/>'
               '<rect x="9" y="-55" width="8" height="11" rx="3" fill="#222"/>'
               + ('<path d="M4 -70L14 -67" stroke="#111" stroke-width="2.5"/>' if idle == "angry" else "")
               + steam),
        shoe_extra='<path d="M-3 47Q4 41 13 44" stroke="#f4f4f4" stroke-width="2" fill="none"/>',
        front_arm=front_arm,  # e.g. reaching up for a dunk
        idle=idle,
    )


def reekz(x0, motion=None, idle="nod", music=True):
    """Reekz: red tracksuit, white bucket hat, ghettoblaster on his shoulder playing music.

    music=False: the ghettoblaster is quiet (no notes).
    """
    rep = _repeat(motion)
    boombox = f"""<g transform="translate(-2 16)">
        <path d="M14 -100V-108H58V-100" stroke="#222" stroke-width="4" fill="none"/>
        <path d="M54 -108L66 -126" stroke="#222" stroke-width="2"/>
        <rect x="10" y="-100" width="52" height="28" rx="4" fill="#c9ccd2" stroke="#111" stroke-width="2.5"/>
        <circle cx="22" cy="-86" r="9" fill="#222"/><circle cx="22" cy="-86" r="4" fill="#777"/>
        <circle cx="50" cy="-86" r="9" fill="#222"/><circle cx="50" cy="-86" r="4" fill="#777"/>
        <rect x="32" y="-96" width="8" height="9" fill="#3a3a3a"/>
        <circle cx="24" cy="-73" r="5" fill="#4a2e1c"/>
        <g font-family="Arial, sans-serif" font-size="18" fill="#111" {'' if music else 'display="none"'}>
          <text x="64" y="-104" opacity="0">♪
            <animate attributeName="opacity" values="0;1;0" dur="1s" {rep}/>
            <animateTransform attributeName="transform" type="translate" values="0 0;8 -22" dur="1s" {rep}/></text>
          <text x="72" y="-92" opacity="0">♫
            <animate attributeName="opacity" values="0;1;0" dur="1s" begin="0.5s" {rep}/>
            <animateTransform attributeName="transform" type="translate" values="0 0;10 -24" dur="1s" begin="0.5s" {rep}/></text>
        </g>
      </g>"""
    return _figure(
        "Reekz (tracksuit, white bucket hat, ghettoblaster)", x0, True, motion, "#c0392b", "#c0392b", "#f4f4f4", "#4a2e1c",
        _face("#4a2e1c", -62)
        + '<path d="M-13 -70Q-12 -86 0 -86Q12 -86 13 -70Z" fill="#f4f4f4" stroke="#b5b5b5" stroke-width="1.5"/>'
        + '<path d="M-23 -63L-15 -71H15L23 -63Q0 -59 -23 -63Z" fill="#f4f4f4" stroke="#b5b5b5" stroke-width="1.5"/>',
        torso_extra='<path d="M-12 -48V4M12 -48V4" stroke="#f4f4f4" stroke-width="3"/>',
        front_arm='<path d="M6 -42L18 -52L20 -58" stroke="#c0392b" stroke-width="10" stroke-linecap="round" fill="none"/>',
        front=boombox,
        idle=idle,
    )


# A breaking crew from the neighbourhood, cyphering on the block: (skin, top, trousers, shoes,
# hat, what's on top of the shoes)
BBOYS = {
    "kangol": ("#4a2e1c", "#c0392b", "#111", "#f4f4f4", "kangol"),
    "bucket hat": ("#7a4a2e", "#2e8b57", "#2e8b57", "#f4f4f4", "bucket"),
    "headband": ("#5a3a24", "#ffd23f", "#2d4f8a", "#f4f4f4", "headband"),
    "cap": ("#c68e5f", "#3d6fb6", "#3d6fb6", "#111", "cap"),
    "toprock": ("#6b4226", "#7d3cff", "#7d3cff", "#f4f4f4", "headband"),
}


def bboy(x0, who, dancing=False):
    """A b-boy from the cypher: tracksuit, shell-toes with stripes, a Kangol, a bucket hat, a
    headband or a cap. dancing: toprock in the middle of the cypher (stepping on the spot,
    swaying, arms out)."""
    skin, top, trousers, shoes, hat = BBOYS[who]
    hats = {
        "kangol": '<path d="M-18 -67Q-20 -84 0 -85Q20 -85 23 -73L27 -70Q14 -66 -18 -66Z" fill="#111"/>',
        "bucket": '<path d="M-14 -72Q0 -90 14 -72Z" fill="#f4f4f4"/><path d="M-22 -70H22" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>',
        "headband": '<circle cx="0" cy="-70" r="19" fill="#1e1410"/>',
        "cap": '<path d="M-16 -68Q0 -86 16 -68Z" fill="#d02b2b"/><path d="M8 -68H28" stroke="#d02b2b" stroke-width="4" stroke-linecap="round"/>',
    }
    head = (hats[hat] + _face(skin) + '<path d="M-17 -70Q0 -78 17 -70" stroke="#d02b2b" stroke-width="4" fill="none"/>'
            if hat == "headband" else _face(skin) + hats[hat])
    stripes = '<path d="M0 44L4 40M4 44L8 40M8 44L12 40" stroke="#111" stroke-width="1.5"/>'
    # stepping on the spot: a "walk" that never goes anywhere and never stops (the toprock)
    steps = Walk(dist=0, secs=3600, stride=0.6) if dancing else None
    figure = _figure(f"B-boy ({'toprock, ' if dancing else ''}{who})", x0, dancing, steps, top, trousers, shoes, skin, head,
                     torso_extra='<path d="M-14 -46V2M14 -46V2" stroke="#f4f4f4" stroke-width="2.5"/>',
                     shoe_extra=stripes, idle="nod")
    if not dancing:
        return figure
    return (f'<g><animateTransform attributeName="transform" type="rotate" values="-6 {x0} 375;6 {x0} 375;-6 {x0} 375" '
            f'dur="1.2s" repeatCount="indefinite"/>{figure}</g>')


def grandmaster_flash(x0, idle="nod"):
    """Grandmaster Flash, the guru of the wheels of steel: a big afro, dark shades, a black
    leather jacket over a red shirt, headphones round his neck, a gold chain; one hand raised
    as he speaks."""
    skin = "#5a3a24"
    head = ('<circle cx="0" cy="-72" r="23" fill="#1e1410"/>' + _face(skin)
            + '<rect x="-2" y="-69" width="18" height="7" rx="3" fill="#111"/>'
            + '<path d="M-1 -66H-8" stroke="#111" stroke-width="2"/>')
    raised = ('<path d="M2 -42L18 -60L22 -82" stroke="#161616" stroke-width="10" stroke-linecap="round" fill="none"/>'
              f'<circle cx="23" cy="-86" r="6" fill="{skin}"/>')
    front = ('<path d="M-12 -50Q0 -38 12 -50" stroke="#222" stroke-width="4" fill="none"/>'
             '<rect x="-17" y="-55" width="8" height="11" rx="3" fill="#222"/><rect x="9" y="-55" width="8" height="11" rx="3" fill="#222"/>'
             '<path d="M-8 -46Q0 -30 8 -46" stroke="#e0b84a" stroke-width="2.5" fill="none"/>'
             '<circle cx="0" cy="-34" r="3.5" fill="#e0b84a"/>')
    return _figure("Grandmaster Flash (the guru: afro, shades, black leather, headphones, gold chain)", x0, True, None,
                   LEATHER, "#2a2a2a", "#f4f4f4", skin, head, torso_extra=_leather("#c0392b"),
                   front_arm=raised, front=front, idle=idle)


def store_clerk(x0):
    """The man behind the corner store's counter: a white apron, a paper cap, a moustache."""
    skin = "#c68e5f"
    head = (_face(skin) + '<path d="M-14 -76H16L12 -84H-10Z" fill="#f4f4f4" stroke="#999" stroke-width="1"/>'
            + '<path d="M4 -58Q10 -55 15 -58" stroke="#3a2414" stroke-width="3" fill="none"/>')
    return _figure("Store clerk (white apron, paper cap)", x0, False, None, "#f4f4f4", "#3a3a42", "#111", skin, head,
                   torso_extra='<path d="M-12 -40H12V4H-12Z" fill="#e8e8e8" stroke="#bbb" stroke-width="1"/>', idle="nod")


def walking_crew(front_x, motion, spacing=70):
    """All four in a row, Reekz in front. Drawn back to front so nobody covers the one ahead."""
    xs = [front_x - i * spacing for i in range(4)]  # reekz, needle, portals, bible
    return "".join([bible_either(xs[3], motion), portals(xs[2], motion), needle(xs[1], motion),
                    reekz(xs[0], motion)])


def _project(p, yaw, roll=0.0, pitch=math.radians(16), dist=420, floor=None):
    """3D point -> 2D screen point (x right, y down) plus depth (bigger z = nearer to us).

    roll turns around the body's x axis, yaw around the vertical axis, and the camera looks
    down a little (pitch) with perspective, so circles on the floor show as ellipses.
    """
    x, y, z = p
    y, z = y * math.cos(roll) - z * math.sin(roll), y * math.sin(roll) + z * math.cos(roll)
    x, z = x * math.cos(yaw) + z * math.sin(yaw), -x * math.sin(yaw) + z * math.cos(yaw)
    if floor is not None:
        y = max(y, floor)
    y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)
    s = dist / (dist - z)
    return x * s, -y * s, z


RING = 16  # points round a brim or a headband


def _head_axes(j, head="head", face="face", hat="hat"):
    """The head's centre and its front, up and right directions (unit vectors)."""
    def sub(a, b):
        return tuple(x - y for x, y in zip(a, b))

    def unit(v):
        n = math.sqrt(sum(x * x for x in v)) or 1
        return tuple(x / n for x in v)
    centre = j[head]
    front = unit(sub(j[face], centre))
    up = sub(j[hat], centre)
    up = unit(tuple(u - sum(a * b for a, b in zip(up, front)) * f for u, f in zip(up, front)))
    right = (up[1] * front[2] - up[2] * front[1], up[2] * front[0] - up[0] * front[2], up[0] * front[1] - up[1] * front[0])
    return centre, front, up, right


def _headwear_points(j, kind, head="head", face="face", hat="hat", r=14):
    """3D points of what he wears on his head, turned with it. "bucket": a brim (a ring round
    the head, a little above the eyes) and the crown's middle; "headband": hair (its middle)
    and a band round the forehead."""
    c, front, up, right = _head_axes(j, head, face, hat)

    def at(height, radius, angle):
        ca, sa = math.cos(angle), math.sin(angle)
        return tuple(c[k] + r * (height * up[k] + radius * (ca * right[k] + sa * front[k])) for k in range(3))
    if kind == "bucket":
        ring = {f"brim{i}": at(0.8, 1.15, 2 * math.pi * i / RING) for i in range(RING)}
        return {**ring, "crown": at(1.15, 0, 0)}  # above the eyes
    ring = {f"band{i}": at(0.38, 1.02, 2 * math.pi * i / RING) for i in range(RING)}
    return {**ring, "hair": at(0.3, 0, 0)}


def _headwear_svg(proj, kind, colour, timing, loop, head="head"):
    """What he wears on his head through all frames: (drawn behind the head, drawn on top).
    The bucket hat: the brim, then the round crown. The headband: hair behind the head, and the
    band, each piece of it only while it is on the side facing us."""
    seq = proj + proj[:1] if loop else proj

    def values(fn):
        return ";".join(fn(f) for f in seq)

    def circle(cls, n, radius, fill):
        return (f'<circle class="{cls}" r="{radius}" fill="{fill}" stroke="#111" stroke-width="1.5">'
                f'<animate attributeName="cx" values="{values(lambda f: f"{f[n][0]:.1f}")}" {timing}/>'
                f'<animate attributeName="cy" values="{values(lambda f: f"{f[n][1]:.1f}")}" {timing}/></circle>')
    if kind == "bucket":
        brim = values(lambda f: " ".join(f"{f[f'brim{i}'][0]:.1f},{f[f'brim{i}'][1]:.1f}" for i in range(RING)))
        top = (f'<polygon class="brim" fill="{colour}" stroke="#111" stroke-width="1.5" stroke-linejoin="round">'
               f'<animate attributeName="points" values="{brim}" {timing}/></polygon>'
               + circle("crown", "crown", 8, colour))
        return "", top
    behind = circle("hair", "hair", 16.5, "#1e1410")
    pieces = []
    for i in range(RING):
        a, b = f"band{i}", f"band{(i + 1) % RING}"
        seen = ";".join("1" if (f[a][2] + f[b][2]) / 2 > f[head][2] else "0" for f in proj)
        d = values(lambda f: f"M{f[a][0]:.1f} {f[a][1]:.1f}L{f[b][0]:.1f} {f[b][1]:.1f}")
        pieces.append(f'<path class="headband" stroke="{colour}" stroke-width="4.5" stroke-linecap="round" fill="none">'
                      f'<animate attributeName="opacity" values="{seen}" calcMode="discrete" {timing}/>'
                      f'<animate attributeName="d" values="{d}" {timing}/></path>')
    return behind, "".join(pieces)


def _face_points(j, head="head", face="face", hat="hat", r=13):
    """The face on a 3D head: two eyes and a mouth (corners and middle, a smile) on the front of
    the head, turned with it. The head's front points at face, its top at hat."""
    centre, front, up, right = _head_axes(j, head, face, hat)

    def at(a, b, c):
        return tuple(centre[k] + r * (a * front[k] + b * up[k] + c * right[k]) for k in range(3))
    return {"eye_l": at(0.8, 0.3, -0.42), "eye_r": at(0.8, 0.3, 0.42),
            "mouth_l": at(0.82, -0.4, -0.3), "mouth_c": at(0.9, -0.48, 0), "mouth_r": at(0.82, -0.4, 0.3)}


def _face_svg(proj, head, timing, loop):
    """The eyes and the mouth through all frames (proj: projected points per frame, with
    _face_points); each shows only while it is on the side of the head facing us."""
    seq = proj + proj[:1] if loop else proj

    def values(fn):
        return ";".join(fn(f) for f in seq)

    def seen(n):
        return f'values="{";".join("1" if f[n][2] > f[head][2] + 1 else "0" for f in proj)}" calcMode="discrete"'

    def xy(f, n):
        return f"{f[n][0]:.1f} {f[n][1]:.1f}"
    eyes = "".join(f'<circle class="eye" r="2.4" fill="#111"><animate attributeName="opacity" {seen(n)} {timing}/>'
                   f'<animate attributeName="cx" values="{values(lambda f: f"{f[n][0]:.1f}")}" {timing}/>'
                   f'<animate attributeName="cy" values="{values(lambda f: f"{f[n][1]:.1f}")}" {timing}/></circle>'
                   for n in ("eye_l", "eye_r"))
    def smile(f):
        return f"M{xy(f, 'mouth_l')}L{xy(f, 'mouth_c')}L{xy(f, 'mouth_r')}"
    mouth = (f'<path class="mouth" stroke="#111" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none">'
             f'<animate attributeName="opacity" {seen("mouth_c")} {timing}/>'
             f'<animate attributeName="d" values="{values(smile)}" {timing}/></path>')
    return eyes + mouth


def _spin3d(move, points, limbs, torso, head, face, hat, pose, frames, secs, red, back_red, skin, white, floor=None,
            world=None, trail=()):
    """Animate a 3D skeleton through one full turn, as SVG paths with per-frame values.

    points: name -> (x, y, z) in body coordinates. limbs: (from, to, width, colour, shoe).
    pose(i) gives (yaw, roll) for frame i. Each limb is drawn twice, behind and in front of
    the torso; per frame only the copy on the correct side is visible.
    """
    def with_face(j):
        return {**j, **_face_points(j, head, face, hat), **_headwear_points(j, "bucket", head, face, hat)}
    if world:  # the move computes every joint in the room itself (e.g. the 1990)
        proj = [{n: _project(p, 0, 0) for n, p in with_face(world(2 * math.pi * i / frames)).items()} for i in range(frames)]
    else:
        proj = [{n: _project(p, *pose(i), floor=floor) for n, p in with_face(points).items()} for i in range(frames)]
    timing = f'dur="{secs}s" repeatCount="indefinite"'

    def values(fn):
        return ";".join(fn(f) for f in proj + proj[:1])

    def discrete(fn):
        return f'values="{";".join(fn(i) for i in range(frames))}" calcMode="discrete"'

    def torso_z(i):
        return sum(proj[i][n][2] for n in torso) / len(torso)

    def limb(a, b, width, colour, shoe, layer):
        in_front = (lambda i: (proj[i][a][2] + proj[i][b][2]) / 2 >= torso_z(i))
        show = discrete(lambda i: "1" if in_front(i) == (layer == "front") else "0")
        d = values(lambda f: f"M{f[a][0]:.1f} {f[a][1]:.1f}L{f[b][0]:.1f} {f[b][1]:.1f}")
        out = (f'<g class="{layer}"><animate attributeName="opacity" {show} {timing}/>'
               f'<path stroke="#111" stroke-width="{width + 3}" stroke-linecap="round" fill="none">'
               f'<animate attributeName="d" values="{d}" {timing}/></path>'
               f'<path stroke="{colour}" stroke-width="{width}" stroke-linecap="round" fill="none">'
               f'<animate attributeName="d" values="{d}" {timing}/></path>')
        if colour == red:  # tracksuit stripe
            out += f'<path stroke="{white}" stroke-width="2" fill="none"><animate attributeName="d" values="{d}" {timing}/></path>'
        if shoe:
            out += (f'<circle r="7" fill="{white}" stroke="#111" stroke-width="1.5">'
                    f'<animate attributeName="cx" values="{values(lambda f: f"{f[b][0]:.1f}")}" {timing}/>'
                    f'<animate attributeName="cy" values="{values(lambda f: f"{f[b][1]:.1f}")}" {timing}/></circle>')
        return out + "</g>"

    back = "".join(limb(*l, "back") for l in limbs)
    front = "".join(limb(*l, "front") for l in limbs)
    # torso: a plane through shoulders and hips; a thick outline keeps it solid when seen edge-on
    corners = values(lambda f: " ".join(f"{f[n][0]:.1f},{f[n][1]:.1f}" for n in torso))
    facing = [(proj[i][face][2] > proj[i][head][2]) for i in range(frames)]
    torso_svg = (f'<polygon fill="#111" stroke="#111" stroke-width="17" stroke-linejoin="round">'
                 f'<animate attributeName="points" values="{corners}" {timing}/></polygon>'
                 f'<polygon stroke-width="14" stroke-linejoin="round">'
                 f'<animate attributeName="points" values="{corners}" {timing}/>'
                 f'<animate attributeName="fill" {discrete(lambda i: red if facing[i] else back_red)} {timing}/>'
                 f'<animate attributeName="stroke" {discrete(lambda i: red if facing[i] else back_red)} {timing}/></polygon>')
    _, bucket_hat = _headwear_svg(proj, "bucket", white, timing, loop=True, head=head)  # his white bucket hat
    head_svg = (f'<circle r="14" fill="{skin}" stroke="#111" stroke-width="1.5">'
                f'<animate attributeName="cx" values="{values(lambda f: f"{f[head][0]:.1f}")}" {timing}/>'
                f'<animate attributeName="cy" values="{values(lambda f: f"{f[head][1]:.1f}")}" {timing}/></circle>'
                f'<g id="{move}-face">{_face_svg(proj, head, timing, loop=True)}</g>{bucket_hat}')
    # a faint trail along the path of the feet (the circle they sweep)
    trails = "".join(
        f'<path d="M{" L".join(f"{f[n][0]:.1f} {f[n][1]:.1f}" for f in proj)}Z" fill="none" stroke="{white}" '
        f'stroke-width="2" stroke-dasharray="4 7" opacity="0.3"/>' for n in trail)
    return trails + back + torso_svg + head_svg + front


# The 1990, joint by joint: a handstand on his right hand (at the origin), his body upside down
# above it, leaning a little so his weight sits over the hand, legs in a small V, the other arm
# tucked to his body. y is up.
NINETEEN_NINETY_BODY = {
    "hand_r": (0, 0, 0), "el_r": (1, 22, 0), "sh_r": (2, 44, 0), "sh_l": (2, 44, -26),
    "head": (6, 30, -13), "face": (17, 30, -13), "hat": (6, 18, -13),
    "hip_r": (-2, 92, -4), "hip_l": (-2, 92, -22),
    "kn_r": (-6, 124, 8), "kn_l": (-6, 124, -34), "foot_r": (-8, 152, 16), "foot_l": (-8, 152, -42),
    "el_l": (12, 58, -38), "hand_l": (14, 76, -30),
}


def _nineteen_ninety_world(t):
    """Where every joint is at phase t of the 1990: the whole body turns around the vertical
    line through the hand he stands on, so that hand stays put on the floor."""
    c, s = math.cos(t), math.sin(t)
    return {n: (x * c + z * s, y, -x * s + z * c) for n, (x, y, z) in NINETEEN_NINETY_BODY.items()}


def reekz_breaking(x0, floor_y, loop_secs=6):
    """Reekz breaking on the floor, in 3D, in a loop: a headspin, then a 1990, then again,
    with a short crossfade between them.

    Both moves come from a 3D skeleton turned in space and drawn in perspective (36 positions
    per turn), so his legs pass in front of and behind his body and his feet trace ellipses.
    Same look as always: red tracksuit with white stripes, white bucket hat, white sneakers.
    (x0, floor_y) is the spot on the floor he spins on.
    """
    red, back_red, skin, white = "#c0392b", "#93291e", "#4a2e1c", "#f4f4f4"
    frames = 36
    # crossfades of 0.3 s: headspin for the first half of the loop, 1990 for the second
    fade = 0.3 / loop_secs
    times = f'keyTimes="0;{0.5 - fade:.3f};0.5;{1 - fade:.3f};1"'
    show_first = f'values="1;1;0;0;1" {times}'
    show_second = f'values="0;0;1;1;0" {times}'

    # headspin: upside down on his head, turning around the vertical axis through the head
    hs_points = {
        "hat": (0, 4, 0), "head": (0, 16, 0), "face": (0, 18, 12),
        "sh_l": (-15, 32, 0), "sh_r": (15, 32, 0), "hip_l": (-9, 80, 0), "hip_r": (9, 80, 0),
        "hand_l": (-42, 24, 6), "hand_r": (42, 24, -6), "foot_l": (-40, 128, 10), "foot_r": (40, 128, -10),
    }
    hs_limbs = [("sh_l", "hand_l", 9, red, False), ("sh_r", "hand_r", 9, red, False),
                ("hip_l", "foot_l", 11, red, True), ("hip_r", "foot_r", 11, red, True)]
    headspin = _spin3d("headspin", hs_points, hs_limbs, ("sh_l", "sh_r", "hip_r", "hip_l"), "head", "face", "hat",
                       lambda i: (2 * math.pi * i / frames, 0.0), frames, 0.9, red, back_red, skin, white)

    # 1990: spinning in a one-handed handstand (see _nineteen_ninety_world)
    ninety_limbs = [("sh_l", "el_l", 9, red, False), ("el_l", "hand_l", 8, red, False),
                    ("sh_r", "el_r", 9, red, False), ("el_r", "hand_r", 8, red, False),
                    ("hip_l", "kn_l", 12, red, False), ("kn_l", "foot_l", 11, red, True),
                    ("hip_r", "kn_r", 12, red, False), ("kn_r", "foot_r", 11, red, True)]
    nineteen_ninety = _spin3d("nineteen-ninety", NINETEEN_NINETY_BODY, ninety_limbs, ("sh_l", "sh_r", "hip_r", "hip_l"),
                              "head", "face", "hat", None, 48, 0.8, red, back_red, skin, white,
                              world=_nineteen_ninety_world, trail=("foot_l", "foot_r"))
    return f"""
  <!-- Reekz (breaking in 3D: headspin, then 1990, in a loop) -->
  <g id="reekz-breaking" transform="translate({x0} {floor_y})">
    <ellipse cx="0" cy="2" rx="70" ry="13" fill="#000" opacity="0.3"/>
    <g id="headspin" opacity="1">
      <animate attributeName="opacity" {show_first} dur="{loop_secs}s" repeatCount="indefinite"/>
      {headspin}
    </g>
    <!-- end headspin -->
    <g id="nineteen-ninety" opacity="0">
      <animate attributeName="opacity" {show_second} dur="{loop_secs}s" repeatCount="indefinite"/>
      {nineteen_ninety}
    </g>
    <!-- end nineteen-ninety -->
  </g>
  <!-- end reekz-breaking -->
"""

def portals_back(arm_angle_anim="", mist_anim=""):
    """Portals seen from behind, facing the wall he paints on. Origin is the hip.

    His right arm reaches out from the shoulder at (16, -46) towards the wall; arm_angle_anim is
    an animateTransform (rotate around the shoulder) that aims it, mist_anim switches the paint
    mist at the can on and off. Same look: denim jacket with paint splatters, afro with yellow
    headband, bag full of cans, dark trousers, white sneakers.
    """
    denim, skin = "#3d6fb6", "#5a3a24"
    mist = "".join(
        f'<circle cx="{58 + dx}" cy="{dy}" r="3" fill="#ff6fa8" opacity="0.8">'
        f'<animate attributeName="r" values="2;9" dur="0.4s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.9;0" dur="0.4s" begin="{b}s" repeatCount="indefinite"/></circle>'
        for dx, dy, b in ((0, 0, 0), (5, -5, 0.13), (4, 5, 0.26)))
    return f"""
  <!-- Portals (from behind, painting) -->
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="0.5s" repeatCount="indefinite"/>
    <rect x="-15" y="0" width="12" height="44" rx="5" fill="#2a2a2a"/><rect x="3" y="0" width="12" height="44" rx="5" fill="#2a2a2a"/>
    <rect x="-17" y="40" width="16" height="9" rx="3" fill="#f4f4f4"/><rect x="1" y="40" width="16" height="9" rx="3" fill="#f4f4f4"/>
    <rect x="-34" y="-30" width="6" height="12" rx="2" fill="#ffd23f"/><rect x="-27" y="-32" width="6" height="14" rx="2" fill="#7ed957"/>
    <rect x="-38" y="-20" width="24" height="24" rx="4" fill="#8b6b3a"/>
    <path d="M-20 -50H20L18 4H-18Z" fill="{denim}"/>
    <path d="M-16 -48L14 -8" stroke="#6b4e2a" stroke-width="4"/>
    <circle cx="-6" cy="-30" r="3" fill="#ffd23f"/><circle cx="8" cy="-18" r="2.5" fill="#ff4f79"/>
    <circle cx="-2" cy="-6" r="2" fill="#7ed957"/><circle cx="10" cy="-38" r="2" fill="#f4f4f4"/>
    <rect x="-24" y="-46" width="10" height="40" rx="5" fill="{denim}"/><circle cx="-19" cy="-4" r="6" fill="{skin}"/>
    <rect x="-7" y="-56" width="14" height="10" fill="{skin}"/>
    <circle cx="0" cy="-72" r="22" fill="#1e1410"/>
    <path d="M-21 -74Q0 -66 21 -74" stroke="#ffd23f" stroke-width="5" fill="none"/>
    <g>
      {arm_angle_anim}
      <path d="M16 -46H54" stroke="{denim}" stroke-width="10" stroke-linecap="round"/>
      <circle cx="56" cy="-46" r="6" fill="{skin}"/>
      <rect x="54" y="-58" width="10" height="20" rx="2" fill="#ff4f79" transform="rotate(90 59 -48)"/>
      <rect x="66" y="-50" width="5" height="6" fill="#222"/>
      <g transform="translate(16 -46)">{mist_anim}{mist}</g>
    </g>
  </g>
"""


def rico(x0, y0=HIP_Y, idle="nod"):
    """Rico, who runs the record shop: grey afro, moustache, big 70s glasses, an orange shirt
    with a wide collar and a brown pattern, brown flares."""
    shirt, skin = "#e8742a", "#8a5a3a"
    head = (
        '<circle cx="0" cy="-70" r="21" fill="#9a9a9a"/>'
        + f'<circle cx="0" cy="-64" r="16" fill="{skin}"/>'
        + '<circle cx="9" cy="-65" r="5" fill="none" stroke="#111" stroke-width="1.8"/>'
        + '<path d="M-2 -65H4" stroke="#111" stroke-width="1.5"/>'
        + '<circle cx="9" cy="-65" r="1.6" fill="#111"/>'
        + '<path d="M4 -56Q10 -53 16 -56" stroke="#3a3a3a" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    )
    pattern = ('<path d="M-12 -40L-6 -34L0 -40L6 -34L12 -40M-12 -24L-6 -18L0 -24L6 -18L12 -24M-12 -8L-6 -2L0 -8L6 -2L12 -8" '
               'stroke="#7a3d16" stroke-width="2" fill="none"/>'
               '<path d="M-10 -48L0 -38L10 -48L14 -44L0 -32L-14 -44Z" fill="#f4e7c3"/>')
    return _figure("Rico (record shop owner, orange 70s shirt, glasses)", x0, True, None, shirt, "#6b3f1f", "#3a2414",
                   skin, head, torso_extra=pattern, y0=y0, idle=idle)


def king_krete(x0, seat_y):
    """King Krete, the Sopranos' MC, sitting on a crate (side view, facing right; the scene
    mirrors him). Gold crown, sunglasses, gold chain, black leather vest over a red shirt,
    grey trousers. (x0, seat_y) is where he sits. His hands are free: the scene puts the
    record under his arm."""
    skin, red, grey = "#6b4226", "#c0392b", "#4a4f57"
    return f"""
  <!-- King Krete (Sopranos MC: gold crown, sunglasses, gold chain, leather vest) -->
  <g transform="translate({x0} {seat_y})">
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -1.5;0 0" dur="1.2s" repeatCount="indefinite"/>
      <path d="M-6 -2H34" stroke="#111" stroke-width="17" stroke-linecap="round"/>
      <path d="M-6 -2H34" stroke="{grey}" stroke-width="14" stroke-linecap="round"/>
      <path d="M34 -2V44" stroke="#111" stroke-width="15" stroke-linecap="round"/>
      <path d="M34 -2V44" stroke="{grey}" stroke-width="12" stroke-linecap="round"/>
      <rect x="28" y="40" width="22" height="9" rx="3" fill="#111"/>
      <path d="M-20 -60H18L16 0H-18Z" fill="{red}"/>
      <path d="M-20 -60H-6L-4 0H-18Z M18 -60H6L4 0H16Z" fill="#161616"/>
      <path d="M-8 -58Q0 -38 8 -58" stroke="#e0b84a" stroke-width="3" fill="none"/>
      <circle cx="0" cy="-42" r="4" fill="#e0b84a"/>
      <path d="M14 -54L32 -30L40 -10" stroke="#161616" stroke-width="11" stroke-linecap="round" fill="none"/>
      <circle cx="41" cy="-8" r="6.5" fill="{skin}"/>
      <rect x="-7" y="-70" width="14" height="12" fill="{skin}"/>
      <circle cx="0" cy="-84" r="17" fill="{skin}" stroke="#111" stroke-width="1"/>
      <path d="M-17 -88Q0 -104 17 -88Z" fill="#1e1410"/>
      <rect x="0" y="-90" width="19" height="7" rx="2" fill="#111"/>
      <path d="M-16 -96L-14 -116L-6 -104L0 -120L6 -104L14 -116L16 -96Z" fill="#e0b84a" stroke="#8a6a14" stroke-width="1.5"/>
      <circle cx="0" cy="-108" r="2.5" fill="#c0392b"/>
      <path d="M8 -74Q13 -71 17 -74" stroke="#111" stroke-width="2" fill="none"/>
    </g>
  </g>
"""


def sopranos_member(x0, bandana="#c0392b"):
    """One of the Sopranos Family: grey tracksuit with red stripes, a bandana, arms crossed."""
    skin = "#5a3a24"
    crossed = ('<path d="M-14 -36L14 -30M14 -40L-14 -26" stroke="#5a5f68" stroke-width="10" stroke-linecap="round"/>'
               f'<circle cx="16" cy="-30" r="5.5" fill="{skin}"/><circle cx="-16" cy="-26" r="5.5" fill="{skin}"/>')
    return _figure("Sopranos member (grey tracksuit, bandana, arms crossed)", x0, True, None, "#5a5f68", "#4a4f57",
                   "#111", skin,
                   _face(skin) + f'<path d="M-17 -70Q0 -86 17 -70L17 -66H-17Z" fill="{bandana}"/>'
                   + f'<path d="M-17 -68L-26 -60" stroke="{bandana}" stroke-width="4"/>',
                   torso_extra='<path d="M-12 -48V4M12 -48V4" stroke="#c0392b" stroke-width="3"/>',
                   front_arm=crossed, idle="still")


def bouncer(x0, lifts_at=None):
    """The bouncer at the Borough DJ Battle's door: big, a black T-shirt, a shaved head, shades, a gold
    chain, arms crossed. lifts_at: when he uncrosses his arms and lifts the velvet rope (seconds)."""
    skin = "#3a2414"
    crossed = ('<path d="M-16 -36L16 -30M16 -40L-16 -26" stroke="#111" stroke-width="12" stroke-linecap="round"/>'
               f'<circle cx="18" cy="-30" r="6.5" fill="{skin}"/><circle cx="-18" cy="-26" r="6.5" fill="{skin}"/>')
    if lifts_at is not None:  # his arms cross until he lifts the rope, then one reaches out to it
        reach = (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{lifts_at:.2f}s"/>'
                 '<path d="M4 -44L28 -30" stroke="#111" stroke-width="12" stroke-linecap="round"/>'
                 f'<circle cx="31" cy="-28" r="6.5" fill="{skin}"/></g>')
        crossed = f'<g><set attributeName="opacity" to="0" begin="{lifts_at:.2f}s"/>{crossed}</g>{reach}'
    head = (_face(skin) + '<path d="M-2 -70H17V-62H-2Z" fill="#111"/>'
            '<path d="M-14 -50Q0 -40 14 -50" stroke="#e0b84a" stroke-width="3" fill="none"/>')
    return _figure("Bouncer (Borough DJ Battle, black T-shirt, shades)", x0, True, None, "#111", "#1b1b1b", "#111", skin, head,
                   torso_extra='<path d="M-19 -48H19L17 4H-17Z" fill="#111"/>', front_arm=crossed, idle="still")


def host(x0):
    """The host at the Borough DJ Battle: white suit with wide lapels, afro, big bow tie, a mic."""
    skin = "#6b4226"
    mic = ('<path d="M4 -44L20 -62L24 -70" stroke="#f4f4f4" stroke-width="10" stroke-linecap="round" fill="none"/>'
           '<circle cx="25" cy="-72" r="6" fill="#6b4226"/><rect x="27" y="-88" width="6" height="16" rx="2" fill="#2a2a2a"/>'
           '<circle cx="30" cy="-92" r="6" fill="#c9ccd2" stroke="#555" stroke-width="1.5"/>')
    return _figure("Host (Borough DJ Battle, white suit)", x0, True, None, "#f4f4f4", "#e8e8e8", "#111", skin,
                   '<circle cx="0" cy="-70" r="22" fill="#1e1410"/>' + _face(skin)
                   + '<path d="M-6 -50L0 -46L6 -50L6 -42L0 -46L-6 -42Z" fill="#d02b2b"/>',
                   torso_extra='<path d="M-10 -48L0 -26L10 -48" stroke="#c9c9c9" stroke-width="3" fill="none"/>',
                   front_arm=mic, idle="nod")


# The audience at the rap battle: people from the block, facing us. (skin, top, hair, hair colour)
LOOKS = [
    ("#4a2e1c", "#e8742a", "afro", "#1e1410"),
    ("#c68e5f", "#3fa9f5", "cap", "#d02b2b"),
    ("#7a4a2e", "#7ed957", "kangol", "#f4f4f4"),
    ("#5a3a24", "#ff4f79", "bandana", "#ffd23f"),
    ("#8a5a3a", "#f4f4f4", "short", "#1e1410"),
    ("#e0b08a", "#7d3cff", "cap", "#111"),
    ("#6b4226", "#ffd23f", "afro", "#3a2414"),
    ("#4a2e1c", "#2e8b57", "kangol", "#c0392b"),
    ("#c68e5f", "#c0392b", "short", "#5a3a24"),
    ("#7a4a2e", "#3d6fb6", "bandana", "#7ed957"),
]
CHEER = "cheering"  # while someone raps a verse, the audience throws its arms up


def _front_head(x, y, look, r=11):
    """A face looking at us: eyes, a grin, and the hair or hat of this look."""
    skin, _, hair, colour = look
    back = {"afro": f'<circle cx="{x}" cy="{y - 3}" r="{r + 5}" fill="{colour}"/>'}.get(hair, "")
    top = {
        "cap": f'<path d="M{x - r} {y - 3}Q{x} {y - r - 9} {x + r} {y - 3}Z" fill="{colour}"/>'
               f'<ellipse cx="{x}" cy="{y - 3}" rx="{r + 3}" ry="2.5" fill="{colour}"/>',
        "kangol": f'<path d="M{x - r - 2} {y - 4}Q{x} {y - r - 10} {x + r + 2} {y - 4}Z" fill="{colour}"/>',
        "bandana": f'<path d="M{x - r} {y - 4}Q{x} {y - r - 6} {x + r} {y - 4}Z" fill="{colour}"/>'
                   f'<path d="M{x + r - 2} {y - 4}L{x + r + 6} {y + 2}" stroke="{colour}" stroke-width="3"/>',
        "short": f'<path d="M{x - r} {y - 3}Q{x} {y - r - 5} {x + r} {y - 3}Z" fill="{colour}"/>',
    }.get(hair, "")
    return (f'{back}<circle cx="{x}" cy="{y}" r="{r}" fill="{skin}" stroke="#111" stroke-width="1"/>{top}'
            f'<circle class="eye" cx="{x - 4}" cy="{y}" r="1.6" fill="#111"/>'
            f'<circle class="eye" cx="{x + 4}" cy="{y}" r="1.6" fill="#111"/>'
            f'<path d="M{x - 4} {y + 5}Q{x} {y + 8} {x + 4} {y + 5}" stroke="#111" stroke-width="1.3" fill="none"/>')


def _arms(x, shoulder_y, skin, top, down, up):
    """Arms in two poses: down (most of the time) and up (cheering while Bible raps)."""
    def pair(points):
        return "".join(f'<path d="M{x + sx} {shoulder_y}L{x + hx} {hy}" stroke="{top}" stroke-width="7" stroke-linecap="round"/>'
                       f'<circle cx="{x + hx}" cy="{hy}" r="4" fill="{skin}"/>' for sx, hx, hy in points)
    return (f'<g data-overlay="!{CHEER}">{pair(down)}</g>'
            f'<g data-overlay="{CHEER}" style="display:none">'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="0.45s" repeatCount="indefinite"/>'
            f'{pair(up)}</g>')


def spectator_in_window(x, window_top, look, k=0):
    """Someone inside the train, looking out of a window."""
    skin, top, _, _ = look
    y = window_top + 15
    return (f'<g class="spectator"><animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" '
            f'dur="0.6s" begin="{(k % 4) * 0.15:.2f}s" repeatCount="indefinite"/>'
            f'<rect x="{x - 15}" y="{y + 10}" width="30" height="16" rx="6" fill="{top}"/>'
            f'{_front_head(x, y, look, r=9)}'
            f'{_arms(x, y + 14, skin, top, down=[], up=[(-12, -18, y - 20), (12, 18, y - 20)])}</g>')


def spectator_in_door(x, floor_y, look, k=0):
    """Someone standing in an open door of the train."""
    skin, top, _, _ = look
    head_y = floor_y - 84
    return (f'<g class="spectator"><animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" '
            f'dur="0.55s" begin="{(k % 4) * 0.15:.2f}s" repeatCount="indefinite"/>'
            f'<rect x="{x - 10}" y="{floor_y - 36}" width="8" height="36" rx="3" fill="#2d3a5a"/>'
            f'<rect x="{x + 2}" y="{floor_y - 36}" width="8" height="36" rx="3" fill="#2d3a5a"/>'
            f'<rect x="{x - 12}" y="{floor_y - 4}" width="11" height="5" rx="2" fill="#f4f4f4"/>'
            f'<rect x="{x + 1}" y="{floor_y - 4}" width="11" height="5" rx="2" fill="#f4f4f4"/>'
            f'<rect x="{x - 14}" y="{floor_y - 72}" width="28" height="40" rx="7" fill="{top}"/>'
            f'{_front_head(x, head_y, look)}'
            f'{_arms(x, floor_y - 68, skin, top, down=[(-12, -16, floor_y - 40), (12, 16, floor_y - 40)], up=[(-12, -22, head_y - 24), (12, 22, head_y - 24)])}</g>')


def spectator_on_roof(x, roof_y, look, k=0):
    """Someone sitting on the roof of the train, legs dangling over the side."""
    skin, top, _, _ = look
    head_y = roof_y - 42
    return (f'<g class="spectator"><animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" '
            f'dur="0.6s" begin="{(k % 4) * 0.15:.2f}s" repeatCount="indefinite"/>'
            f'<path d="M{x - 6} {roof_y}V{roof_y + 22}M{x + 6} {roof_y}V{roof_y + 20}" stroke="#2d3a5a" stroke-width="8" stroke-linecap="round"/>'
            f'<rect x="{x - 12}" y="{roof_y + 20}" width="11" height="5" rx="2" fill="#f4f4f4"/>'
            f'<rect x="{x + 1}" y="{roof_y + 18}" width="11" height="5" rx="2" fill="#f4f4f4"/>'
            f'<rect x="{x - 13}" y="{roof_y - 30}" width="26" height="32" rx="7" fill="{top}"/>'
            f'{_front_head(x, head_y, look)}'
            f'{_arms(x, roof_y - 26, skin, top, down=[(-11, -16, roof_y - 4), (11, 16, roof_y - 4)], up=[(-11, -20, head_y - 22), (11, 20, head_y - 22)])}</g>')


def battle_dj(x, table_y):
    """The DJ who provides the beats at the battle: two turntables on milk crates, headphones on,
    cap backwards, one hand scratching while the records spin."""
    skin, jacket = "#5a3a24", "#2e8b57"
    decks = "".join(
        f'<g class="turntable"><rect x="{x + dx - 26}" y="{table_y - 12}" width="52" height="12" rx="2" fill="#2a2a2a" stroke="#111" stroke-width="1.5"/>'
        + spinning_record(x + dx, table_y - 12, 20, c) + '</g>'
        for dx, c in ((-30, "#ff4f79"), (30, "#ffd23f")))
    crates = "".join(
        f'<rect x="{x + dx - 22}" y="{table_y + 6}" width="44" height="40" fill="{c}" stroke="#1d4a78" stroke-width="2"/>'
        f'<path d="M{x + dx - 22} {table_y + 20}H{x + dx + 22}M{x + dx - 22} {table_y + 33}H{x + dx + 22}" stroke="#1d4a78" stroke-width="1.5"/>'
        for dx, c in ((-30, "#2e6fb0"), (30, "#c0392b")))
    head_y = table_y - 54
    return f"""
  <g id="battle-dj">
    <!-- Battle DJ (provides the beats: headphones, cap backwards, scratching) -->
    <rect x="{x - 72}" y="{table_y - 52}" width="22" height="98" fill="#1b1b1b" stroke="#000" stroke-width="2"/>
    <circle cx="{x - 61}" cy="{table_y + 18}" r="8" fill="#2a2a2a" stroke="#000" stroke-width="1.5">
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -1;0 0" dur="0.5s" repeatCount="indefinite"/></circle>
    <circle cx="{x - 61}" cy="{table_y - 30}" r="6" fill="#2a2a2a" stroke="#000" stroke-width="1.5"/>
    <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="0.5s" repeatCount="indefinite"/>
      <rect x="{x - 16}" y="{table_y - 40}" width="32" height="40" rx="8" fill="{jacket}"/>
      <path d="M{x - 10} {table_y - 40}V{table_y}M{x + 10} {table_y - 40}V{table_y}" stroke="#f4f4f4" stroke-width="2.5"/>
      <path d="M{x - 7} {table_y - 38}Q{x} {table_y - 26} {x + 7} {table_y - 38}" stroke="#e0b84a" stroke-width="2.5" fill="none"/>
      {_front_head(x, head_y, (skin, jacket, "cap", "#111"))}
      <path d="M{x + 11} {head_y - 4}L{x + 20} {head_y - 1}" stroke="#111" stroke-width="3"/>
      <g id="headphones"><path d="M{x - 12} {head_y - 2}Q{x} {head_y - 22} {x + 12} {head_y - 2}" stroke="#d02b2b" stroke-width="3" fill="none"/>
        <rect x="{x - 16}" y="{head_y - 6}" width="7" height="12" rx="3" fill="#d02b2b"/><rect x="{x + 9}" y="{head_y - 6}" width="7" height="12" rx="3" fill="#d02b2b"/></g>
      <path d="M{x - 12} {table_y - 34}L{x - 26} {table_y - 14}" stroke="{jacket}" stroke-width="7" stroke-linecap="round"/>
      <circle cx="{x - 27}" cy="{table_y - 13}" r="4" fill="{skin}"/>
      <g id="scratch-hand">
        <animateTransform attributeName="transform" type="translate" values="0 0;8 0;0 0;-4 0;0 0" dur="0.5s" repeatCount="indefinite"/>
        <path d="M{x + 12} {table_y - 34}L{x + 28} {table_y - 14}" stroke="{jacket}" stroke-width="7" stroke-linecap="round"/>
        <circle cx="{x + 29}" cy="{table_y - 13}" r="4" fill="{skin}"/>
      </g>
    </g>
    <rect x="{x - 60}" y="{table_y}" width="120" height="7" fill="#8b5a2b" stroke="#3a2414" stroke-width="1.5"/>
    {decks}
    {crates}
  </g>
  <!-- end battle-dj -->
"""


def police_officer(x0, motion=None, shout=None, leash_to=None):
    """A 1970s NYPD patrolman: dark blue uniform, peaked cap with a badge, a badge on his chest,
    black belt with a nightstick. shout: words in a bubble over his head. leash_to: the x (relative
    to him) where his dog's collar is, for a leash in his hand."""
    navy, skin = "#1f2e4a", "#c68e5f"
    cap = ('<path d="M-17 -72Q0 -90 17 -72Z" fill="#1a2438"/>'
           '<rect x="-17" y="-74" width="34" height="6" rx="2" fill="#1a2438"/>'
           '<path d="M2 -70H24L20 -66H2Z" fill="#111"/>'
           '<circle cx="0" cy="-80" r="3.5" fill="#e0b84a" stroke="#8a6a14" stroke-width="1"/>')
    torso = ('<path d="M-10 -40L-6 -32" stroke="#e0b84a" stroke-width="0"/>'
             '<path d="M6 -40l4 -3l4 3l-1 5h-6Z" fill="#e0b84a" stroke="#8a6a14" stroke-width="1"/>'
             '<rect x="-17" y="-8" width="34" height="5" fill="#111"/><rect x="-3" y="-8" width="6" height="5" fill="#c9ccd2"/>'
             '<path d="M-14 -4L-20 22" stroke="#3a2414" stroke-width="4" stroke-linecap="round"/>')
    extra = ""
    if shout:
        w = len(shout) * 11 + 24
        extra += (f'<g><rect x="{-w / 2 + 10}" y="-138" width="{w}" height="32" rx="10" fill="#f4f4f4" stroke="#111" stroke-width="2.5"/>'
                  f'<path d="M4 -106L8 -94L14 -106Z" fill="#f4f4f4" stroke="#111" stroke-width="2"/>'
                  f'<text x="10" y="-115" font-family="{FONT}" font-size="19" fill="#d02b2b" text-anchor="middle">{shout}</text></g>')
    if leash_to is not None:
        extra += f'<path d="M6 -6Q{leash_to / 2} 14 {leash_to} -2" stroke="#3a2414" stroke-width="2" fill="none"/>'
    return _figure("Police officer (1970s NYPD: navy uniform, peaked cap, badge)", x0, True, motion, navy, navy, "#111",
                   skin, _face(skin) + cap, torso_extra=torso, front=extra)


def police_dog(x0, motion, bark=True):
    """A German shepherd on a leash, running (side view, facing right). Origin: under its chest."""
    tan, black = "#b07a3c", "#2a1d12"
    legs = "".join(
        f'<g><animateTransform attributeName="transform" type="rotate" values="{v}" dur="{motion.stride}s" '
        f'repeatCount="{motion.secs / motion.stride:g}" additive="sum"/>'
        f'<rect x="{lx - 3}" y="-6" width="6" height="24" rx="3" fill="{tan}" transform="translate(0 0)"/></g>'
        for lx, v in ((-26, "0 -26 -6;30 -26 -6;0 -26 -6;-30 -26 -6;0 -26 -6"), (-18, "0 -18 -6;-30 -18 -6;0 -18 -6;30 -18 -6;0 -18 -6"),
                      (14, "0 14 -6;-30 14 -6;0 14 -6;30 14 -6;0 14 -6"), (22, "0 22 -6;30 22 -6;0 22 -6;-30 22 -6;0 22 -6")))
    woof = (f'<text x="34" y="-42" font-family="{FONT}" font-size="20" fill="#ffd23f" stroke="#111" stroke-width="1">WOOF!'
            f'<animate attributeName="opacity" values="1;0;1" dur="0.5s" repeatCount="{motion.secs / 0.5:g}"/></text>') if bark else ""
    travel = (f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{motion.dist} 0" '
              f'dur="{motion.secs}s" fill="freeze"/>')
    return f"""
  <!-- Police dog (German shepherd on a leash) -->
  <g transform="translate({x0} {HIP_Y + 30})"><g>
    {travel}
    <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="{motion.stride / 2:g}s" repeatCount="{2 * motion.secs / motion.stride:g}"/>
      {legs}
      <path d="M-32 -14Q-46 -22 -50 -34" stroke="{tan}" stroke-width="5" fill="none" stroke-linecap="round"/>
      <ellipse cx="-4" cy="-12" rx="32" ry="12" fill="{tan}"/>
      <ellipse cx="-6" cy="-18" rx="22" ry="7" fill="{black}"/>
      <path d="M22 -20L34 -32L48 -28L50 -22L36 -16Z" fill="{tan}"/>
      <path d="M30 -30L32 -42L38 -32Z" fill="{black}"/>
      <path d="M46 -26L52 -24" stroke="#111" stroke-width="3" stroke-linecap="round"/>
      <circle cx="40" cy="-27" r="1.8" fill="#111"/>
      <path d="M22 -20L26 -12" stroke="#d02b2b" stroke-width="3"/>
      {woof}
    </g>
  </g></g>
"""


def placed(svg, who, x, feet, scale):
    """Someone (drawn standing at x) put into a circle at a depth: further back means higher up
    (feet) and smaller (scale), nearer means lower and bigger."""
    return (f'<g class="in-circle" data-x="{x:g}" data-feet="{feet:g}" data-scale="{scale:g}" data-who="{who}" '
            f'transform="translate({x:g} {feet:g}) scale({scale:g}) translate(-{x:g} -{FEET_Y})">{svg}</g>')


TROUSERS = ("#2d4f8a", "#2a2a2a", "#5a3e2a", "#3d6fb6", "#6e6a62", "#1f3a2a", "#7a2e1f")


def onlooker(x, feet, look, k=0, cheer=False, scale=1.0):
    """Someone from the block watching, facing us: jeans or slacks, a T-shirt or a jacket, the
    face and hair of their look. Bobbing to the music; cheer: arms up, jumping."""
    skin, top, _, _ = look
    trousers = TROUSERS[k % len(TROUSERS)]
    shoe = ("#f4f4f4", "#111", "#d02b2b", "#c9a23a")[k % 4]
    h = 1.0 + 0.06 * ((k * 7) % 5 - 2) / 2  # some taller, some shorter
    hip, shoulder, head = -36 * h, -72 * h, -86 * h
    if cheer:
        arms = (f'<path d="M-12 {shoulder + 4:.1f}L-22 {head - 12:.1f}M12 {shoulder + 4:.1f}L22 {head - 12:.1f}" stroke="{top}" stroke-width="7" stroke-linecap="round"/>'
                f'<circle cx="-22" cy="{head - 14:.1f}" r="4" fill="{skin}"/><circle cx="22" cy="{head - 14:.1f}" r="4" fill="{skin}"/>')
        move = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" dur="0.5s" '
                f'begin="{(k % 5) * 0.1:.1f}s" repeatCount="indefinite"/>')
    else:
        hand = -16 * h if k % 3 else -24 * h  # hands down, or one hand up to the chin
        arms = (f'<path d="M-12 {shoulder + 4:.1f}L-15 {hip + 4:.1f}M12 {shoulder + 4:.1f}L{15 if k % 3 else 8} {hip + 4 if k % 3 else head + 12:.1f}" stroke="{top}" stroke-width="7" stroke-linecap="round"/>'
                f'<circle cx="-15" cy="{hip + 6:.1f}" r="4" fill="{skin}"/><circle cx="{15 if k % 3 else 8}" cy="{hip + 6 if k % 3 else head + 12:.1f}" r="4" fill="{skin}"/>')
        move = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="0.5s" '
                f'begin="{(k % 4) * 0.12:.2f}s" repeatCount="indefinite"/>')
    jacket = (f'<path d="M-2 {shoulder:.1f}V{hip:.1f}" stroke="#000" stroke-width="1.5" opacity="0.3"/>' if k % 2 else
              f'<path d="M-6 {shoulder + 6:.1f}H6" stroke="#fff" stroke-width="2" opacity="0.35"/>')
    body = (f'<rect x="-10" y="{hip:.1f}" width="9" height="{-hip:.1f}" rx="3" fill="{trousers}"/>'
            f'<rect x="1" y="{hip:.1f}" width="9" height="{-hip:.1f}" rx="3" fill="{trousers}"/>'
            f'<rect x="-12" y="-4" width="11" height="5" rx="2" fill="{shoe}"/><rect x="1" y="-4" width="11" height="5" rx="2" fill="{shoe}"/>'
            f'<rect x="-14" y="{shoulder:.1f}" width="28" height="{hip - shoulder + 4:.1f}" rx="7" fill="{top}"/>'
            f'<rect x="-14" y="{shoulder:.1f}" width="8" height="{hip - shoulder + 4:.1f}" rx="4" fill="#000" opacity="0.15"/>{jacket}'
            f'{arms}{_front_head(0, head, look)}')
    kind = "onlooker cheering" if cheer else "onlooker"
    return (f'<g class="{kind}" transform="translate({x:g} {feet:g}) scale({scale:g})"><g>{move}{body}</g></g>')


# --- the crew facing us -------------------------------------------------------------------------
# The same five, turned to face the screen: the same clothes, hats and props as from the side.

def _front_face(skin, back="", top=""):
    """A head facing us: hair behind it, both ears, the head, the hair or hat on top, two eyes
    with a glint, brows, a nose and a smile."""
    eyes = "".join(f'<circle class="eye" cx="{x}" cy="-64" r="2.1" fill="#111"/><circle cx="{x + 0.7}" cy="-64.7" r="0.6" fill="#fff"/>'
                   for x in (-6, 6))
    brows = "".join(f'<path class="brow" d="M{x - 3.5} -69.5L{x + 3.5} -70" stroke="#111" stroke-width="1.8" stroke-linecap="round"/>'
                    for x in (-6, 6))
    ears = "".join(f'<g class="ear"><circle cx="{x}" cy="-62" r="4.2" fill="{skin}"/>'
                   f'<path d="M{x - 1 if x > 0 else x + 1} -64Q{x + (2 if x > 0 else -2)} -62 {x - 1 if x > 0 else x + 1} -60" stroke="#000" stroke-width="1" opacity="0.3" fill="none"/></g>'
                   for x in (-15.5, 15.5))
    return (f'{back}{ears}<circle cx="0" cy="-64" r="16" fill="{skin}"/>'
            '<path d="M-16 -64A16 16 0 0 0 0 -48A16 16 0 0 1 -11 -64Z" fill="#000" opacity="0.12"/>'
            f'{top}{eyes}{brows}'
            '<path d="M-1.5 -62Q0 -58 2 -59" stroke="#000" stroke-width="1.3" opacity="0.35" fill="none"/>'
            '<path class="mouth" d="M-5 -55Q0 -52 5 -55" stroke="#2a1208" stroke-width="1.6" fill="none" stroke-linecap="round"/>')


def _front_figure(name, x0, skin, top, trouser, shoe, head, torso_extra="", arms=None, front="", idle="nod", y0=HIP_Y):
    """Someone standing facing us (the hip is the origin): legs, shoes with soles, the torso with
    its shading and belt, arms down at the sides (or arms), the head, and what's in front."""
    sole = "#9a9aa2" if shoe.lower() in ("#f4f4f4", "#ffffff") else "#e6e6e6"
    legs = "".join(f'<rect x="{x}" y="0" width="10" height="44" rx="4" fill="{trouser}"/>'
                   f'<path d="M{x + 5} 6V38" stroke="#000" stroke-width="1.3" opacity="0.18"/>'
                   f'<path d="M{x - 2} 48V43Q{x - 2} 39 {x + 5} 39Q{x + 12} 39 {x + 12} 43V48Z" fill="{shoe}"/>'
                   f'<rect class="sole" x="{x - 2}" y="46" width="14" height="2.5" rx="1" fill="{sole}"/>'
                   for x in (-12, 2))
    if arms is None:
        arms = "".join(f'<rect x="{x}" y="-46" width="9" height="40" rx="4.5" fill="{top}"/>'
                       f'<rect x="{x}" y="-46" width="9" height="40" rx="4.5" fill="#000" opacity="{0.2 if x < 0 else 0.08}"/>'
                       f'<circle cx="{x + 4.5}" cy="-5" r="5.5" fill="{skin}"/>' for x in (-27, 18))
    bob = {"nod": '<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="0.5s" repeatCount="indefinite"/>',
           "still": ""}[idle]
    return f"""
  <!-- {name} (facing us) -->
  <g transform="translate({x0} {y0})"><g>
    {bob}
    {legs}
    <path d="M-19 -48H19L16 4H-16Z" fill="{top}"/>
    <path class="shade" d="M-19 -48H-12L-10 4H-16Z" fill="#000" opacity="0.16"/>
    <path d="M12 -48H19L16 4H10Z" fill="#000" opacity="0.07"/>
    <rect class="belt" x="-16" y="-3" width="32" height="5" fill="#000" opacity="0.3"/>
    <rect x="-5" y="-52" width="10" height="6" fill="{skin}"/><rect x="-5" y="-52" width="10" height="6" fill="#000" opacity="0.2"/>
    {torso_extra}
    {arms}
    {head}
    {front}
  </g></g>
"""


_FRONT_SHORT_HAIR = '<path class="short-hair" d="M-16 -66Q-16 -82 0 -82Q16 -82 16 -66Q8 -72 0 -72Q-8 -72 -16 -66Z" fill="#1e1410"/>'


def _front_leather(shirt):
    """The black leather jacket from the front: open over the shirt, lapels, zips, a shine."""
    return (f'<path d="M-8 -48L0 -26L8 -48Z" fill="{shirt}"/>'
            '<path d="M-12 -48L-2 -26M12 -48L2 -26" stroke="#3a3a3a" stroke-width="3"/>'
            '<path d="M-3 -26V2M3 -26V2" stroke="#8a8a8a" stroke-width="1.2"/>'
            '<path d="M-15 -42Q-17 -22 -14 -2" stroke="#4a4a4a" stroke-width="2" fill="none"/>')


def needle_front(x0, idle="nod"):
    """Fantastic Needle facing us: yellow shirt, red Kangol, red Pumas, headphones round his neck."""
    kangol = ('<g class="kangol"><path d="M-19 -67Q-19 -86 0 -87Q19 -86 19 -67Z" fill="#d02b2b"/>'
              '<path d="M-20 -68Q0 -63 20 -68" stroke="#a51f1f" stroke-width="3" fill="none"/>'
              '<path d="M-12 -80Q0 -84 12 -80" stroke="#e8564a" stroke-width="1.5" fill="none"/></g>')
    phones = ('<g class="headphones"><path d="M-13 -48Q0 -36 13 -48" stroke="#222" stroke-width="4" fill="none"/>'
              '<rect x="-20" y="-54" width="8" height="11" rx="3" fill="#222"/><rect x="12" y="-54" width="8" height="11" rx="3" fill="#222"/></g>')
    return _front_figure("Fantastic Needle (red Kangol, red Pumas, headphones)", x0, "#4a2e1c", "#f2c230", "#2d4f8a", "#d02b2b",
                         _front_face("#4a2e1c", top=kangol), front=phones, idle=idle)


def bible_front(x0, book=True, idle="nod"):
    """MC Bible facing us: black leather jacket over the green shirt, his rhyme book in both hands
    (book=False: his hands are empty)."""
    skin = "#7a4a2e"
    arms = None
    front = ""
    if book:
        arms = (f'<path d="M-22 -44L-24 -24L-12 -18" stroke="{LEATHER}" stroke-width="9" stroke-linecap="round" fill="none"/>'
                f'<path d="M22 -44L24 -24L12 -18" stroke="{LEATHER}" stroke-width="9" stroke-linecap="round" fill="none"/>')
        front = (f'<g transform="rotate(-3 0 -24)"><rect x="-17" y="-42" width="34" height="40" rx="3" fill="#7a2e1f" stroke="#111" stroke-width="2"/>'
                 '<rect x="-12" y="-38" width="24" height="28" fill="none" stroke="#ffd23f" stroke-width="1.2"/>'
                 f'<text x="0" y="-26" font-family="{FONT}" font-size="9" fill="#ffd23f" text-anchor="middle">RHYME</text>'
                 f'<text x="0" y="-15" font-family="{FONT}" font-size="9" fill="#ffd23f" text-anchor="middle">BOOK</text></g>'
                 f'<circle cx="-15" cy="-18" r="5.5" fill="{skin}"/><circle cx="15" cy="-18" r="5.5" fill="{skin}"/>')
    return _front_figure("MC Bible (black leather jacket" + (", rhyme book)" if book else ")"), x0, skin, LEATHER, "#2d4f8a", "#f4f4f4",
                         _front_face(skin, top=_FRONT_SHORT_HAIR), torso_extra=_front_leather("#2e8b57"), arms=arms, front=front, idle=idle)


def bible_front_either(x0, idle="nod"):
    """Bible facing us, with his book while the crew has it, without it otherwise."""
    return (f'<g data-overlay="lacks-rhyme_book" style="display:none">{bible_front(x0, book=False, idle=idle)}</g>'
            f'<g data-overlay="has-rhyme_book" style="display:none">{bible_front(x0, book=True, idle=idle)}</g>')


def portals_front(x0, idle="nod"):
    """Portals facing us: the paint-splattered denim jacket, afro with the yellow headband, the
    spray can in his hand, the bag of cans on his hip."""
    skin = "#5a3a24"
    afro = '<circle class="afro" cx="0" cy="-68" r="22" fill="#1e1410"/>'
    band = '<path class="headband" d="M-20 -73Q0 -81 20 -73" stroke="#ffd23f" stroke-width="5" fill="none"/>'
    splats = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in
                     ((-8, -30, 3, "#ffd23f"), (9, -18, 2.5, "#ff4f79"), (-2, -8, 2, "#7ed957"), (11, -38, 2, "#f4f4f4"), (-12, -14, 2, "#3fa9f5")))
    strap = '<path d="M14 -46L-12 -6" stroke="#6b4e2a" stroke-width="4"/>'
    can = ('<g class="spray-can"><rect x="18" y="-12" width="10" height="20" rx="2" fill="#ff4f79" stroke="#111" stroke-width="1"/>'
           '<rect x="20" y="-16" width="6" height="5" fill="#222"/></g>')
    bag = ('<rect x="-28" y="-10" width="22" height="20" rx="4" fill="#8b6b3a" stroke="#5a4020" stroke-width="1.5"/>'
           '<rect x="-24" y="-16" width="5" height="8" rx="1.5" fill="#7ed957"/><rect x="-17" y="-17" width="5" height="9" rx="1.5" fill="#3fa9f5"/>')
    return _front_figure("Portals (denim, spray can, bag full of cans)", x0, skin, "#3d6fb6", "#2a2a2a", "#f4f4f4",
                         _front_face(skin, back=afro, top=band), torso_extra=splats + strap, front=bag + can, idle=idle)


def reekz_front(x0, idle="nod", music=True):
    """Reekz facing us: the red tracksuit with white stripes, the white bucket hat, the
    ghettoblaster up on his shoulder (music=False: quiet)."""
    skin = "#4a2e1c"
    bucket = ('<g class="bucket"><path d="M-13 -75Q-12 -91 0 -91Q12 -91 13 -75Z" fill="#f4f4f4" stroke="#b5b5b5" stroke-width="1.5"/>'
              '<path d="M-24 -71Q0 -64 24 -71L19 -77H-19Z" fill="#f4f4f4" stroke="#b5b5b5" stroke-width="1.5"/></g>')
    stripes = '<path d="M-17 -46L-14 4M17 -46L14 4" stroke="#f4f4f4" stroke-width="3"/>'
    arms = (f'<rect x="-27" y="-46" width="9" height="40" rx="4.5" fill="#c0392b"/><path d="M-22.5 -44V-8" stroke="#f4f4f4" stroke-width="2"/>'
            f'<circle cx="-22.5" cy="-5" r="5.5" fill="{skin}"/>'
            '<path d="M20 -44L32 -62L30 -78" stroke="#c0392b" stroke-width="9" stroke-linecap="round" fill="none"/>')
    notes = "" if not music else "".join(
        f'<text x="{x}" y="-104" font-family="Arial, sans-serif" font-size="16" fill="#111" opacity="0">{n}'
        f'<animate attributeName="opacity" values="0;1;0" dur="1s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;-8 -20" dur="1s" begin="{b}s" repeatCount="indefinite"/></text>'
        for x, n, b in ((52, "♪", 0), (68, "♫", 0.5)))
    box = ('<g class="boombox"><path d="M14 -100V-108H56V-100" stroke="#222" stroke-width="4" fill="none"/>'
           '<rect x="10" y="-100" width="50" height="28" rx="4" fill="#c9ccd2" stroke="#111" stroke-width="2.5"/>'
           '<circle cx="22" cy="-86" r="9" fill="#222"/><circle cx="22" cy="-86" r="4" fill="#777"/>'
           '<circle cx="48" cy="-86" r="9" fill="#222"/><circle cx="48" cy="-86" r="4" fill="#777"/>'
           f'<rect x="31" y="-96" width="8" height="9" fill="#3a3a3a"/><circle cx="30" cy="-80" r="5.5" fill="{skin}"/>{notes}</g>')
    return _front_figure("Reekz (tracksuit, white bucket hat, ghettoblaster)", x0, skin, "#c0392b", "#c0392b", "#f4f4f4",
                         _front_face(skin, top=bucket), torso_extra=stripes, arms=arms, front=box, idle=idle)
