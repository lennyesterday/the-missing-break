"""Builds every SVG in assets/ from the shared scenery and crew.

    uv run python -m art.build
"""

import json
import math
from pathlib import Path

from art import crew, cypher
from logic import CHOKED_MESSAGE, CRAYON_MESSAGE, NO_MONEY_MESSAGE, ENDINGS, LOCKED_STATION_MESSAGE, LOST_BATTLE_MESSAGE, RECORDS, RHYME_BOOK_VERSE, SCENES, SONGS
from art.crew import Walk
from art.fonts import text_width
from art.scenery import DUSK, FONT, TAG_FONT, block_text, button_train, piece_parts, spinning_record, defs, el, piece, skyline, star, street, tag, train

ROOT = Path(__file__).resolve().parent.parent


def _svg(body, svg_id, end=None, cues=None, auto=None, attrs=""):
    """end: when the animation is finished (seconds), so the app can skip to it.
    cues: sound effects the page plays along with the animation (see intro_screen).
    auto: (action, secs): the page does this action by itself when the animation gets there."""
    end_attr = f' data-end="{end}"' if end is not None else ""
    if cues:
        end_attr += f" data-cues='{json.dumps(cues, separators=(',', ':'))}'"
    if auto:
        end_attr += f' data-auto-action="{auto[0]}" data-auto-delay="{auto[1]:.3f}"'
    end_attr += attrs
    return (f'<svg xmlns="http://www.w3.org/2000/svg" id="{svg_id}"{end_attr} viewBox="0 0 800 450" '
            f'width="800" height="450">\n{body}</svg>\n')


HQ_WALK = (130, 470, 4.5)  # Reekz (in front) starts at the HQ door, walks this far, in this long


def _hq_street():
    """The street from the crew's tenement (the HQ door down to the basement) to the basketball
    court, under the el: a laundromat in between, the court behind its chain-link fence."""
    return f'''
  <!-- the street from the HQ to the court -->
  <rect width="800" height="450" fill="url(#sky)"/>
  <circle cx="420" cy="60" r="36" fill="#fff1c1" opacity="0.7"/>
{skyline()}{train()}{el(columns=(300, 560))}
  <!-- the crew's tenement, with the stairs down to the basement: the HQ -->
  <rect x="0" y="150" width="260" height="190" fill="url(#bricks)"/>
  <rect x="0" y="146" width="260" height="8" fill="#5c2a1d"/>
  <g fill="#f6d27a"><rect x="24" y="168" width="30" height="36"/><rect x="104" y="168" width="30" height="36"/><rect x="184" y="168" width="30" height="36"/></g>
  {piece(12, 238, "GOODFELLAS", "gPinkYellow", size=24, rot=-3, fit=170)}
  {tag(190, 236, "Reekz", "#3fa9f5", 16, -10)}
  <g id="hq-door">
    <rect x="60" y="262" width="74" height="78" fill="#2a1a16"/>
    <path d="M60 262H134" stroke="#111" stroke-width="5"/>
    <text x="97" y="290" font-family="{FONT}" font-size="22" fill="#ffd23f" stroke="#111" stroke-width="1.5" text-anchor="middle" transform="rotate(-5 97 290)">HQ</text>
    <path d="M140 300L200 340M140 300V340M170 320V340" stroke="#222" stroke-width="4"/>
  </g>
  <!-- a laundromat -->
  <rect x="260" y="190" width="300" height="150" fill="#6e3a30"/>
  <rect x="276" y="206" width="268" height="30" fill="#111"/>
  <text x="410" y="228" font-family="{FONT}" font-size="18" fill="#7ef0ff" text-anchor="middle" letter-spacing="2">WASH &amp; DRY</text>
  <rect x="280" y="248" width="170" height="70" fill="#9fd3ff" opacity="0.55" stroke="#111" stroke-width="4"/>
  <g fill="#f4f4f4" stroke="#555" stroke-width="2">{"".join(f'<circle cx="{x}" cy="284" r="15"/>' for x in (310, 360, 410))}</g>
  <rect x="470" y="248" width="60" height="92" fill="#5a3e2a" stroke="#111" stroke-width="4"/>
  {tag(290, 334, "Sopranos", "#111", 13, -3)}{tag(470, 240, "BX", "#f4f4f4", 14, 6)}
  <!-- the basketball court behind its chain-link fence, the hoop -->
  <rect x="560" y="200" width="240" height="140" fill="#3e6e55"/>
  <g id="hoop">
    <rect x="690" y="206" width="70" height="44" rx="3" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
    <rect x="712" y="222" width="26" height="18" fill="none" stroke="#e8562a" stroke-width="2.5"/>
    <ellipse cx="725" cy="254" rx="18" ry="4" fill="none" stroke="#e8562a" stroke-width="3"/>
    <path d="M725 250V340" stroke="#555" stroke-width="5"/>
  </g>
  <rect x="560" y="150" width="240" height="190" fill="url(#chainlink)" opacity="0.9"/>
  <path d="M560 150H800M560 150V340M680 150V340M798 150V340" stroke="#5d626b" stroke-width="5"/>
  <g id="court-gate"><rect x="600" y="230" width="60" height="110" fill="#3e6e55" opacity="0.9"/>
    <path d="M600 230V340M660 230V340M600 230H660" stroke="#5d626b" stroke-width="4"/></g>
{street(tag(40, 440, "GoodFellas", "#ffd23f", 14, 0))}
  <!-- end street -->'''


def _walk_hq_block(back):
    start, dist, secs = HQ_WALK
    if back:  # the same street, the crew mirrored: from the court gate back to the HQ door, facing left
        walkers = (f'<g id="crew-walking-back" transform="translate(800 0) scale(-1 1)">'
                   f'{crew.walking_crew(800 - (start + dist), Walk(dist=dist, secs=secs), spacing=70)}</g>')
        caption = "BACK TO THE BASEMENT"
    else:
        walkers = crew.walking_crew(start, Walk(dist=dist, secs=secs), spacing=70)
        caption = "TO THE COURT"
    body = defs() + _hq_street() + f'''
{walkers}
  <g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" dur="{secs}s" fill="freeze"/>
    <rect x="16" y="12" width="300" height="40" rx="8" fill="#111" opacity="0.85"/>
    <text x="166" y="39" font-family="{FONT}" font-size="19" fill="#ffd23f" text-anchor="middle" letter-spacing="1">{caption}</text></g>
  <!-- SKIP: straight there -->
  <g data-action="enter" role="button" tabindex="0" aria-label="Skip the walk">
    <title>Skip</title>
    <rect x="684" y="60" width="100" height="38" rx="9" fill="#111" stroke="#f4f4f4" stroke-width="2.5" opacity="0.9"/>
    {piece(734, 88, "SKIP ▶▶", "gWhite", size=22, rot=-2, anchor="middle", fit=80)}
  </g>
'''
    return _svg(body, "walk-block-hq" if back else "walk-hq-block", end=f"{secs + 0.3:.1f}", auto=("enter", secs + 0.3))


def walk_hq_to_block():
    """From the basement to the block: the crew comes out of the HQ door and walks down the
    street, under the el, past the laundromat, to the basketball court. It goes on by itself."""
    return _walk_hq_block(back=False)


def walk_block_to_hq():
    """From the block back to the basement: the same street, the crew walking the other way,
    from the court to the HQ door. It goes on by itself."""
    return _walk_hq_block(back=True)


RICOS_WALK = (230, 440, 4)  # Reekz (in front) starts at the court gate, walks this far, in this long


def _ricos_street():
    """The street from the basketball court to Rico's Record Shop, under the el: the court
    behind its chain-link fence (the hoop), a pizzeria, a barbershop, a street lamp and a
    hydrant, and Rico's on the corner."""
    pole = "".join(f'<path d="M{454 + k * 0} {262 + k * 12}l12 -6" stroke="#d02b2b" stroke-width="4"/>' for k in range(5))
    return f'''
  <!-- the street from the court to Rico's -->
  <rect width="800" height="450" fill="url(#sky)"/>
  <circle cx="610" cy="60" r="38" fill="#fff1c1" opacity="0.7"/>
{skyline()}{train()}{el()}
  <!-- left: the basketball court behind its fence, the hoop -->
  <g id="court-side">
    <rect x="0" y="200" width="230" height="140" fill="#3e6e55"/>
    <g id="hoop">
      <rect x="40" y="206" width="70" height="44" rx="3" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
      <rect x="62" y="222" width="26" height="18" fill="none" stroke="#e8562a" stroke-width="2.5"/>
      <ellipse cx="75" cy="254" rx="18" ry="4" fill="none" stroke="#e8562a" stroke-width="3"/>
      <path d="M75 250V340" stroke="#555" stroke-width="5"/>
    </g>
    <rect x="0" y="150" width="230" height="190" fill="url(#chainlink)" opacity="0.9"/>
    <path d="M0 150H230M2 150V340M120 150V340M228 150V340" stroke="#5d626b" stroke-width="5"/>
    {tag(130, 300, "Sopranos", "#111", 14, -6)}
  </g>
  <!-- a pizzeria and a barbershop -->
  <rect x="230" y="190" width="160" height="150" fill="#6e3a30"/>
  <rect x="244" y="204" width="132" height="30" fill="#111"/>
  <text x="310" y="226" font-family="{FONT}" font-size="18" fill="#ffd23f" text-anchor="middle" letter-spacing="2">PIZZA 50¢</text>
  <rect x="248" y="246" width="124" height="64" fill="#f9e2a2" stroke="#111" stroke-width="4"/>
  <path d="M262 290L310 256L358 290Z" fill="#e8a33a" stroke="#8b4425" stroke-width="2"/>
  {tag(250, 334, "BX", "#f4f4f4", 13, -4)}
  <rect x="390" y="200" width="170" height="140" fill="#3b2f4a"/>
  <rect x="404" y="212" width="142" height="28" fill="#111"/>
  <text x="475" y="232" font-family="{FONT}" font-size="17" fill="#7ef0ff" text-anchor="middle" letter-spacing="2">BARBER</text>
  <rect x="448" y="256" width="14" height="70" rx="6" fill="#f4f4f4" stroke="#111" stroke-width="2"/>
  {pole}
  <rect x="472" y="252" width="70" height="88" fill="#9fd3ff" opacity="0.5" stroke="#111" stroke-width="3"/>
  {tag(400, 330, "Needle", "#d02b2b", 13, -3)}
  <!-- right: Rico's Record Shop -->
  <g id="ricos-shop">
    <rect x="560" y="160" width="240" height="180" fill="#3b2f4a"/>
    <rect x="560" y="156" width="240" height="8" fill="#2a2036"/>
    <rect x="575" y="172" width="215" height="32" fill="#111"/>
    <text x="682" y="196" font-family="{FONT}" font-size="22" fill="#ff4f79" text-anchor="middle" letter-spacing="1">RICO'S RECORDS</text>
    <path d="M565 208H795L785 228H575Z" fill="url(#awning)"/>
    <rect x="580" y="240" width="120" height="70" fill="#f9e2a2" stroke="#111" stroke-width="4"/>
    <circle cx="612" cy="275" r="20" fill="#111"/><circle cx="612" cy="275" r="6" fill="#ffd23f"/>
    <circle cx="668" cy="275" r="20" fill="#111"/><circle cx="668" cy="275" r="6" fill="#3fa9f5"/>
    <rect x="580" y="310" width="120" height="30" fill="url(#shutter)"/>
    {tag(588, 332, "Needle", "#d02b2b", 14, -2)}
    <rect x="715" y="244" width="60" height="96" fill="#5a3e2a" stroke="#111" stroke-width="4"/>
    <circle cx="763" cy="296" r="4" fill="#ffd23f"/>
    {tag(722, 268, "Rico", "#f4f4f4", 13, -6)}
  </g>
  <!-- the street lamp and a hydrant -->
  <path d="M400 340V215Q400 200 415 200H435" stroke="#2a2a2a" stroke-width="6" fill="none"/>
  <ellipse cx="438" cy="205" rx="12" ry="6" fill="#fff1c1"/>
  <g fill="#c0392b">
    <rect x="530" y="315" width="20" height="28" rx="4"/><rect x="524" y="322" width="32" height="7" rx="3"/>
    <rect x="533" y="308" width="14" height="9" rx="3"/>
  </g>
{street(tag(40, 440, "Sopranos rule", "#f4f4f4", 14, 0) + '<path d="M30 445H175" stroke="#d02b2b" stroke-width="3" opacity="0.9"/>')}
  <!-- end street -->'''


def _skip_walk():
    return f'''  <!-- SKIP: straight there -->
  <g data-action="enter" role="button" tabindex="0" aria-label="Skip the walk">
    <title>Skip</title>
    <rect x="684" y="60" width="100" height="38" rx="9" fill="#111" stroke="#f4f4f4" stroke-width="2.5" opacity="0.9"/>
    {piece(734, 88, "SKIP ▶▶", "gWhite", size=22, rot=-2, anchor="middle", fit=80)}
  </g>
'''


def walk_block_to_record_shop():
    """From the block to Rico's: the whole crew walks from the basketball court down the street,
    under the el, past the pizzeria and the barbershop, to Rico's door. ENTER RICO'S leads in;
    SKIP goes straight inside."""
    start, dist, secs = RICOS_WALK
    body = defs() + _ricos_street() + f'''
{crew.walking_crew(start, Walk(dist=dist, secs=secs), spacing=70)}
  <!-- caption fades in when the crew arrives -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{secs}s" dur="0.4s" fill="freeze"/>
    <rect x="16" y="12" width="360" height="40" rx="8" fill="#111" opacity="0.85"/>
    <text x="196" y="39" font-family="{FONT}" font-size="19" fill="#ffd23f" text-anchor="middle" letter-spacing="1">YO RICO! THE WHOLE CREW IS HERE!</text>
  </g>
  <!-- ENTER RICO'S: comes up when the crew is at the door, leads inside the shop -->
  <g data-action="enter" role="button" tabindex="0" aria-label="Enter Rico's record shop" visibility="hidden">
    <title>Enter Rico's record shop</title>
    <set attributeName="visibility" to="visible" begin="{secs}s"/>
    <rect x="590" y="398" width="200" height="44" rx="9" fill="#111" stroke="#ff6fa8" stroke-width="3" opacity="0.92"/>
    {piece(690, 429, "ENTER RICO'S ▶", "gPinkYellow", size=26, rot=-2, anchor="middle", fit=176)}
  </g>
  <!-- end enter -->
''' + _skip_walk()
    return _svg(body, "walk-block-record-shop")


def walk_record_shop_to_block():
    """From Rico's back to the block: the same street, the crew walking the other way, from
    Rico's door back to the court. It goes on to the block by itself (or SKIP)."""
    start, dist, secs = RICOS_WALK
    body = defs() + _ricos_street() + f'''
<g id="crew-walking-back" transform="translate(800 0) scale(-1 1)">{crew.walking_crew(800 - (start + dist), Walk(dist=dist, secs=secs), spacing=70)}</g>
  <g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" dur="{secs}s" fill="freeze"/>
    <rect x="16" y="12" width="300" height="40" rx="8" fill="#111" opacity="0.85"/>
    <text x="166" y="39" font-family="{FONT}" font-size="19" fill="#ffd23f" text-anchor="middle" letter-spacing="1">BACK TO THE COURT</text></g>
''' + _skip_walk()
    return _svg(body, "walk-record-shop-block", end=f"{secs + 0.3:.1f}", auto=("enter", secs + 0.3))


GATE_CREW_X = 512  # where Reekz, at the front of the crew, stands at the gate
STATION_TRAIN = (7.0, 18, 1.0)  # by the station the train takes this long to pass, comes every this many seconds, this far into each round


def _street_life():
    """What goes on in the street by the station: steam rising from a manhole, a newspaper
    blowing across, two pigeons on the station roof, a rat running along the curb now and then."""
    puffs = "".join(
        f'<circle cx="{560 + dx}" cy="390" r="7" fill="#e8e8ee" opacity="0">'
        f'<animate attributeName="cy" values="390;290" dur="3s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="r" values="7;22" dur="3s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0.45;0" dur="3s" begin="{b}s" repeatCount="indefinite"/></circle>'
        for dx, b in ((0, 0), (6, 1), (-4, 2)))

    def pigeon(x, extra):
        return (f'<g transform="translate({x} 150)">{extra}<ellipse rx="9" ry="6" fill="#7d828a"/>'
                '<circle cx="8" cy="-6" r="4" fill="#9a9fa8"/><path d="M11 -6l4 1.5l-4 1" fill="#c98a2a"/>'
                '<path d="M-9 0l-6 -3v6Z" fill="#5d626b"/><path d="M-2 6v4M2 6v4" stroke="#c98a2a" stroke-width="1.5"/></g>')
    bob = '<animateTransform attributeName="transform" type="rotate" values="0;8;0;0" dur="1.2s" repeatCount="indefinite" additive="sum"/>'
    hop = ('<animateTransform attributeName="transform" type="translate" values="0 0;0 0;14 -10;28 0;28 0;0 0" '
           'keyTimes="0;0.5;0.56;0.62;0.9;1" dur="7s" repeatCount="indefinite"/>')
    return f'''
  <!-- steam from a manhole in the street -->
  <g id="steam"><ellipse cx="560" cy="392" rx="20" ry="4.5" fill="#2a2a30" stroke="#55555c" stroke-width="2"/>{puffs}</g>
  <!-- end steam -->
  <!-- a newspaper blowing across the street -->
  <g id="newspaper"><g>
    <animateTransform attributeName="transform" type="translate" values="-60 432;180 404;420 436;860 410;860 410" keyTimes="0;0.2;0.42;0.75;1" dur="12s" repeatCount="indefinite"/>
    <g><animateTransform attributeName="transform" type="rotate" values="0;40;-20;60;0" dur="2.4s" repeatCount="indefinite"/>
      <path d="M-12 -8L12 -10L14 8L-10 10Z" fill="#e8e2d0" stroke="#9a9488" stroke-width="1"/>
      <path d="M-8 -4H8M-8 0H6M-8 4H8" stroke="#9a9488" stroke-width="1"/></g></g></g>
  <!-- end newspaper -->
  <!-- two pigeons on the station roof, one bobbing, one hopping -->
  <g id="pigeons">
    {pigeon(626, bob)}
    <g>{hop}{pigeon(700, "")}</g>
  </g>
  <!-- end pigeons -->
  <!-- a rat runs along the curb, now and then -->
  <g id="rat"><g>
    <animateTransform attributeName="transform" type="translate" values="820 376;820 376;-40 376;-40 376" keyTimes="0;0.6;0.75;1" dur="14s" repeatCount="indefinite"/>
    <ellipse rx="9" ry="4.5" fill="#4a4048"/><circle cx="-9" cy="-1" r="3.5" fill="#4a4048"/><circle cx="-11" cy="-2" r="1" fill="#111"/>
    <path d="M8 0Q18 -2 22 4" stroke="#8a6f78" stroke-width="1.5" fill="none"/>
    <path d="M-4 4v3M4 4v3" stroke="#4a4048" stroke-width="2"><animate attributeName="d" values="M-4 4v3M4 4v3;M-6 4l2 3M6 4l-2 3" dur="0.15s" repeatCount="indefinite"/></path>
  </g></g>
  <!-- end rat -->'''


def _station_street():
    """The street to the old 149th St station: under the el, past a shoe repair, the Sopranos'
    tags leading the way (more and more of them, the closer to the station). (The station house
    itself: _station_entrance; the street life around it: _street_life.)"""
    trail = "".join(tag(x, y, word, colour, size, rot) for x, y, word, colour, size, rot in (
        (30, 236, "Sopranos", "#111", 18, -6), (170, 270, "SF", "#d02b2b", 22, 8), (196, 236, "Krete", "#f4f4f4", 20, -4),
        (330, 300, "Sopranos", "#f4f4f4", 18, 4), (420, 232, "Krete 77", "#111", 18, -8), (470, 290, "SF", "#f4f4f4", 24, -6),
        (500, 214, "Sopranos", "#d02b2b", 20, 6), (530, 314, "SF", "#111", 20, 10)))
    crowns = "".join(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="#c0392b" '
                     f'transform="rotate({rot} {x} {y})">♛</text>' for x, y, size, rot in ((130, 250, 18, -8), (380, 270, 20, 6), (548, 250, 24, -10)))
    passing, every, at = STATION_TRAIN
    return f'''
  <!-- the street to the station -->
  <rect width="800" height="450" fill="url(#sky)"/>
  <circle cx="120" cy="64" r="34" fill="#fff1c1" opacity="0.7"/>
{skyline()}{train(f"{passing:g}s", every=every, at=at)}{el(columns=(200, 520))}
  <!-- the buildings along the way, and the Sopranos' tags leading to the station -->
  <rect x="0" y="180" width="300" height="160" fill="url(#bricks)"/>
  <rect x="0" y="176" width="300" height="8" fill="#5c2a1d"/>
  <g fill="#f6d27a"><rect x="30" y="196" width="28" height="32"/><rect x="230" y="196" width="28" height="32"/></g>
  <rect x="300" y="200" width="272" height="140" fill="#6e3a30"/>
  <rect x="320" y="270" width="150" height="70" fill="url(#shutter)"/>
  <rect x="320" y="226" width="150" height="30" fill="#111"/>
  <text x="395" y="247" font-family="{FONT}" font-size="15" fill="#9a9aa2" text-anchor="middle">SHOE REPAIR</text>
  <g id="sopranos-trail">{trail}{crowns}
    {piece(430, 196, "SOPRANOS", "gSteel", size=26, rot=-4, shadow="#c0392b", fit=136)}
  </g>
  <!-- end sopranos-trail -->
  <!-- the street lamp -->
  <path d="M290 340V215Q290 200 305 200H325" stroke="#2a2a2a" stroke-width="6" fill="none"/>
  <ellipse cx="328" cy="205" rx="12" ry="6" fill="#fff1c1"/>
{street(tag(40, 440, "Sopranos", "#f4f4f4", 14, 0) + tag(380, 432, "SF", "#d02b2b", 16, -4))}
  <!-- end station street -->'''


def _station_cues(extra=()):
    """The train on the el sounds whenever it passes by the station (as on the block)."""
    passing, every, at = STATION_TRAIN
    return [{"src": "app/static/audio/block/train.wav", "on": [[at, at + passing]], "every": every, "vol": 0.5}] + list(extra)


def _gate_locked_sign():
    """When the gate won't open: the message from the rules, and where to get the key."""
    return f'''
  <g data-overlay="rejected-enter_station" style="display:none">
    <rect x="410" y="150" width="384" height="62" rx="10" fill="#111" stroke="#d02b2b" stroke-width="3" opacity="0.95"/>
    <g transform="translate(430 168) scale(0.8)">
      <path d="M4 10V2A10 10 0 0 1 24 2V10" stroke="#b8bcc4" stroke-width="4" fill="none"/>
      <rect x="0" y="8" width="28" height="24" rx="3" fill="#c9a23a" stroke="#6b5214" stroke-width="2"/>
    </g>
    <text x="616" y="179" font-family="{FONT}" font-size="15" fill="#f4f4f4" text-anchor="middle" letter-spacing="1">{LOCKED_STATION_MESSAGE.upper()}</text>
    <text x="616" y="199" font-family="{FONT}" font-size="11" fill="#ffd23f" text-anchor="middle" letter-spacing="2">BACK TO THE BLOCK, THEN ASK RICO...</text>
  </g>
  <!-- end rejected -->
'''


def gate_scene():
    """Outside the old 149th St station (gate): the crew stands at the old station house, its
    arch shut with a scissor gate, chained and padlocked (they walked here from the block:
    walk_block_to_gate). OPEN THE GATE needs Rico's key (without it the rules' message comes
    up); BACK TO THE BLOCK leads back."""
    body = defs() + _station_street() + f'''
  {_station_entrance()}
{_street_life()}
{crew.walking_crew(GATE_CREW_X, None, spacing=70)}
  <!-- once the crew has the key: it glints at the lock -->
  <g data-overlay="has-service_key" style="display:none">
    {_key_icon(700, 372, 1.0)}
    <g><animate attributeName="opacity" values="0;1;0" dur="1.2s" repeatCount="indefinite"/>{star(738, 366, 7, "#fff4c4")}</g>
  </g>
  <!-- the ways on: back to the block, or open the gate -->
  {_way_out("go_block", "◀ BACK TO THE BLOCK", 8, "gBlueGreen", "#7ef0ff")}
  {_way_out("enter_station", "OPEN THE GATE ▶", 596, "gGold", "#7ed957")}
{_gate_locked_sign()}'''
    return _svg(body, "scene-gate", cues=_station_cues())


STATION_WALK = (360, 4.5)  # how far the crew walks between the block and the gate, in how long


def _station_walk(svg_id, caption, back, entrance):
    dist, secs = STATION_WALK
    if back:  # the same street, the crew mirrored: from the station back towards the block, facing left
        walkers = (f'<g id="crew-walking-back" transform="translate(800 0) scale(-1 1)">'
                   f'{crew.walking_crew(800 - GATE_CREW_X, Walk(dist=dist, secs=secs), spacing=70)}</g>')
    else:
        walkers = crew.walking_crew(GATE_CREW_X - dist, Walk(dist=dist, secs=secs), spacing=70)
    body = defs() + _station_street() + f'''
  {entrance}
{_street_life()}
{walkers}
  <g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" dur="{secs}s" fill="freeze"/>
    <rect x="16" y="12" width="330" height="40" rx="8" fill="#111" opacity="0.85"/>
    <text x="181" y="39" font-family="{FONT}" font-size="19" fill="#ffd23f" text-anchor="middle" letter-spacing="1">{caption}</text></g>
''' + _skip_walk()
    return _svg(body, svg_id, end=f"{secs + 0.3:.1f}", cues=_station_cues(), auto=("enter", secs + 0.3))


def walk_block_to_gate():
    """From the block to the old station: the whole crew walks down the street under the el,
    past the shoe repair, following the Sopranos' tags, to the station house. It goes on to the
    gate by itself (or SKIP)."""
    return _station_walk("walk-block-gate", "TO THE 149 ST STATION", False, _station_entrance())


def walk_gate_to_block():
    """From the gate back to the block: the same street, the crew walking the other way. The gate
    stays chained behind them. It goes on by itself (or SKIP)."""
    return _station_walk("walk-gate-block", "BACK TO THE BLOCK", True, _station_entrance())


def walk_station_to_block():
    """Out of the station, back to the block: the gate stands folded open, the crew comes out of
    the arch and walks the same street back. It goes on by itself (or SKIP)."""
    return _station_walk("walk-station-block", "OUT OF THE STATION", True, _station_entrance(opened=True))


UNLOCK_AT = 0.4  # when the key flies to the lock in the gate opening
UNLOCK_SOUNDS = {"key": UNLOCK_AT + 0.4, "padlock": UNLOCK_AT + 0.7, "chain": UNLOCK_AT + 0.85, "gate": UNLOCK_AT + 1.0}
UNLOCK_SECS = 1.8  # how long the sound of it is (art/ambience.py makes it from UNLOCK_SOUNDS)


def walk_gate_to_station():
    """With Rico's key: the crew at the gate, the key flies into the padlock, the padlock drops,
    the chain falls, the gate folds open: ENTER THE STATION (or SKIP). You hear all of it."""
    unlock = UNLOCK_AT
    key_to_lock = (f'<g id="unlock" opacity="0">'
                   f'<set attributeName="opacity" to="1" begin="{unlock:.1f}s"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="570 300;672 316" begin="{unlock:.1f}s" dur="0.4s" fill="freeze"/>'
                   f'<animate attributeName="opacity" values="1;0" begin="{unlock + 0.6:.1f}s" dur="0.3s" fill="freeze"/>'
                   f'{_key_icon(0, 0, 1.6)}</g>'
                   f'<g opacity="0"><animate attributeName="opacity" values="0;1;0" begin="{unlock + 0.4:.1f}s" dur="0.6s" fill="freeze"/>'
                   f'{star(686, 318, 14, "#fff4c4")}</g>\n  <!-- end unlock -->')
    body = defs() + _station_street() + f'''
  {_station_entrance(unlock_at=unlock)}
{_street_life()}
{crew.walking_crew(GATE_CREW_X, None, spacing=70)}
  {key_to_lock}
  <!-- caption when the gate opens -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{unlock + 0.4:.1f}s" dur="0.4s" fill="freeze"/>
    <rect x="16" y="12" width="380" height="40" rx="8" fill="#111" opacity="0.85"/>
    <text x="206" y="39" font-family="{FONT}" font-size="19" fill="#ffd23f" text-anchor="middle" letter-spacing="1">RICO&#39;S KEY FITS! THE GATE IS OPEN!</text>
  </g>
  <!-- ENTER THE STATION: comes up when the gate is open, leads down into the station -->
  <g data-action="enter" role="button" tabindex="0" aria-label="Enter the abandoned 149th St station" visibility="hidden">
    <title>Enter the abandoned 149th St station</title>
    <set attributeName="visibility" to="visible" begin="{unlock + 1.4:.1f}s"/>
    <rect x="566" y="398" width="226" height="44" rx="9" fill="#111" stroke="#7ed957" stroke-width="3" opacity="0.92"/>
    {piece(679, 429, "ENTER THE STATION ▶", "gGold", size=24, rot=-2, anchor="middle", fit=200)}
  </g>
  <!-- end enter -->
''' + _skip_walk()
    unlock_sound = {"src": "app/static/audio/station/unlock.wav", "on": [[unlock, round(unlock + UNLOCK_SECS, 2)]], "vol": 0.7}
    return _svg(body, "walk-gate-station", cues=_station_cues([unlock_sound]))


# Home screen timing: Portals sprays the title from left to right in SPRAY_SECS.
SPRAY_SECS = 3
PORTALS_START, PORTALS_DIST = 260, 380
NOZZLE_DX = 48  # spray nozzle, relative to Portals' hip
TITLE_X = 282  # (clear of Reekz's boombox)


def _missing_break_record(cx, cy, r):
    """A spinning record with a wedge broken out of it: the missing break."""
    import math
    a1, a2 = math.radians(-20), math.radians(40)  # the missing wedge
    p1 = (cx + r * math.cos(a2), cy - r * math.sin(a2))
    p2 = (cx + r * math.cos(a1), cy - r * math.sin(a1))
    pie = f"M{cx} {cy}L{p1[0]:.1f} {p1[1]:.1f}A{r} {r} 0 1 0 {p2[0]:.1f} {p2[1]:.1f}Z"
    grooves = "".join(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="#2c2c2c" stroke-width="1.5"/>'
                      for rr in (r - 6, r - 11, r - 16))
    return f'''  <!-- the missing break: a record with a piece broken out, spinning -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{SPRAY_SECS}s" dur="0.4s" fill="freeze"/>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="3s" repeatCount="indefinite"/>
      <path d="{pie}" fill="#111" stroke="#f4f4f4" stroke-width="2"/>
      <g clip-path="url(#recordPie)">{grooves}</g>
      <circle cx="{cx}" cy="{cy}" r="{r * 0.33:.0f}" fill="#ff4f79" stroke="#111" stroke-width="1.5"/>
      <circle cx="{cx}" cy="{cy}" r="2.5" fill="#111"/>
    </g>
  </g>
'''


def home_screen():
    """Title screen: dusk in the South Bronx. Portals sprays THE MISSING BREAK onto the wall
    while the crew watches, nodding to Reekz's ghettoblaster. The train pulls in and stops:
    the pieces on its cars are the START / RESUME / MENU buttons."""
    nozzle_start = PORTALS_START + NOZZLE_DX
    reveal_from = nozzle_start - (TITLE_X - 12)
    reveal_to = reveal_from + PORTALS_DIST
    clip = f'''    <clipPath id="sprayReveal">
      <rect x="{TITLE_X - 12}" y="160" width="{reveal_from}" height="180">
        <animate attributeName="width" from="{reveal_from}" to="{reveal_to}" dur="{SPRAY_SECS}s" fill="freeze"/>
      </rect>
    </clipPath>
    <clipPath id="recordPie"><circle cx="735" cy="212" r="32"/></clipPath>
'''
    drips = "".join(
        f'<path d="M{x} {y}V{y}" stroke="{c}" stroke-width="3">'
        f'<animate attributeName="d" from="M{x} {y}V{y}" to="M{x} {y}V{y + ln}" begin="{SPRAY_SECS}s" dur="0.8s" fill="freeze"/></path>'
        for x, y, c, ln in ((300, 220, "#2ecc71", 10), (392, 221, "#ff3d8b", 16), (455, 219, "#ff8a3d", 10),
                            (540, 216, "#ff3d8b", 18), (630, 213, "#ff8a3d", 12)))
    twinkles = "".join(
        f'<circle cx="{x}" cy="{y}" r="1.5" fill="#fff"><animate attributeName="opacity" values="0.2;1;0.2" dur="{d}s" repeatCount="indefinite"/></circle>'
        for x, y, d in ((40, 18, 1.5), (210, 12, 2.1), (300, 28, 1.8), (480, 10, 2.4), (560, 24, 1.6), (650, 14, 2.2), (780, 22, 1.9)))

    body = defs(DUSK, extra=clip) + f'''
  <rect width="800" height="450" fill="url(#sky)"/>
  {twinkles}
{skyline("#3a2346", "#2a1834", 0.9, windows=True)}
  <circle cx="250" cy="30" r="20" fill="#fff4d6"/>
  <circle cx="243" cy="25" r="4" fill="#e9dcb8"/><circle cx="257" cy="36" r="3" fill="#e9dcb8"/>
{button_train()}{el(columns=(120, 640))}
  <!-- the hall of fame wall -->
  <rect x="0" y="158" width="800" height="182" fill="url(#bricks)"/>
  <rect x="0" y="158" width="800" height="182" fill="#1f1238" opacity="0.25"/>
  {tag(20, 190, "Sopranos", "#111", 15, -8)}
  {tag(700, 300, "BX", "#f4f4f4", 16, 6)}
  {tag(694, 330, "Bible 1", "#7ed957", 14, -4)}
  {star(40, 300, 9, "#ffd23f")}

  <!-- the title, revealed as Portals sprays it -->
  <g clip-path="url(#sprayReveal)">
    {piece(TITLE_X, 214, "THE", "gBlueGreen", size=46, rot=-2)}
    {piece(TITLE_X + text_width("THE", 46) + 22, 214, "MISSING BREAK", "gPinkYellow", size=46, rot=-2, fit=330)}
    {star(TITLE_X + 2, 172, 9, "#7ed957")}
  </g>
  {drips}
{_missing_break_record(735, 212, 32)}
  <!-- subtitle -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{SPRAY_SECS + 0.3}s" dur="0.6s" fill="freeze"/>
    <rect x="332" y="244" width="270" height="26" rx="4" fill="#111" opacity="0.75"/>
    <text x="467" y="263" font-family="{FONT}" font-size="15" fill="#f4f4f4" text-anchor="middle" letter-spacing="4">SOUTH BRONX · SUMMER 1977</text>
  </g>
{street(tag(540, 440, "Think About It?", "#f4f4f4", 15, 0))}
  <!-- the crew watches, nodding to the beat -->
{crew.needle(34)}{crew.meyhem_front(94)}{crew.bible_front(150)}{crew.reekz(205)}
  <!-- Portals sprays the title, walking along the wall -->
{crew.portals(PORTALS_START, Walk(dist=PORTALS_DIST, secs=SPRAY_SECS), spraying=True)}

  <!-- "start over?" sign: hidden until START is pressed while a save exists -->
  <g data-overlay="confirm-restart" style="display:none">
    <rect width="800" height="450" fill="#0b0716" opacity="0.7"/>
    <rect x="130" y="110" width="540" height="230" rx="14" fill="url(#bricks)" stroke="#111" stroke-width="6"/>
    <rect x="130" y="110" width="540" height="230" rx="14" fill="#1f1238" opacity="0.25"/>
    {piece(400, 172, "START OVER?", "gPinkYellow", size=46, rot=-2, anchor="middle", fit=440)}
    {block_text(400, 212, [("YOUR SAVED GAME WILL BE REPLACED.", "#f4f4f4")], size=19, anchor="middle")}
    <g data-action="restart_yes" role="button" tabindex="0" aria-label="Yes, start over">
      <title>Yes, start over</title>
      <rect x="152" y="240" width="270" height="70" rx="12" fill="#111" stroke="#ffd23f" stroke-width="3"/>
      {piece(287, 285, "YES, START OVER", "gOrangeRed", size=28, rot=-2, anchor="middle", fit=232)}
    </g>
    <g data-action="restart_no" role="button" tabindex="0" aria-label="Cancel, keep my saved game">
      <title>Cancel</title>
      <rect x="442" y="240" width="206" height="70" rx="12" fill="#111" stroke="#7ef0ff" stroke-width="3"/>
      {piece(545, 285, "CANCEL", "gBlueGreen", size=30, rot=-2, anchor="middle", fit=170)}
    </g>
  </g>
'''
    return _svg(body, "home-screen")


# The story Portals sprays after START: (parts as (text, gradient), size, baseline y, seconds to spray).
# Every line starts at INTRO_X. Widths are estimated from the font (Impact is about 0.5 em per letter).
INTRO_X = 100
INTRO_LINES = [
    ([("SOUTH BRONX, SUMMER 1977", "gPinkYellow")], 44, 70, 1.8),
    ([("TWO DAYS BEFORE THE BOROUGH DJ BATTLE,", "gWhite")], 22, 113, 1.4),
    ([("THE ", "gWhite"), ("SOPRANOS", "gSteel"), (" STOLE ", "gWhite"), ("GOODFELLAS", "gGold"),
      (" CREW'S SECRET WEAPON:", "gWhite")], 22, 146, 1.6),
    ([("THE RECORD ", "gWhite"), ('LYN COLLINS – "THINK ABOUT IT".', "gPinkYellow")], 22, 179, 1.4),
    ([("DJ FANTASTIC NEEDLE", "gBlueGreen"), (" SAVED THIS UNHEARD BREAK", "gWhite")], 22, 212, 1.4),
    ([("FOR THE FINAL. IT'S HIS ", "gWhite"), ("SECRET JOINT.", "gOrangeRed")], 22, 245, 1.3),
    ([("HELP THE GOODFELLAS CREW", "gOrangeRed")], 34, 300, 1.3),
    ([("TO GET BACK THE RECORD.", "gOrangeRed")], 34, 343, 1.3),
]
GROUND_HIP = 372  # Portals' hip when he stands on the sidewalk
ARM = 58  # shoulder to the paint mist
REACH_FROM_GROUND = 280  # lines higher than this need the ladder
LADDER_PARK = 880  # off the right edge, where the ladder rolls to when he's done with it


def _text_width(parts, size):
    """How far the reveal has to go for this line: the letters as measured from the font,
    plus their outline and 3D block."""
    return int(text_width("".join(text for text, _ in parts), size) + size * 0.4) + 10


def _painter_route():
    """Where Portals is, how he holds the can and where the ladder is, over time.

    Returns (keyframes, paint_starts, total): keyframes are (t, x, hip_y, arm_angle, ladder_x, mist_on).
    For each line he gets into place (rolling the ladder, climbing, or walking), then sprays it from
    left to right: the mist at his can follows the edge of the letters as they appear.
    """
    frames = [(0.0, -70.0, GROUND_HIP, 70.0, -70.0, False)]
    starts = []

    def move(dt, x, hip, angle, ladder, mist=False):
        frames.append((frames[-1][0] + dt, x, hip, angle, ladder, mist))

    for parts, size, y, secs in INTRO_LINES:
        hit_y = y - size * 0.35
        on_ladder = hit_y < REACH_FROM_GROUND
        hip = hit_y + 46 if on_ladder else GROUND_HIP
        dy = hit_y - (hip - 46)
        dx = math.sqrt(max(ARM ** 2 - dy ** 2, 1))
        angle = math.degrees(math.atan2(dy, dx))
        x_start = INTRO_X - 6 - 16 - dx
        x_end = INTRO_X + _text_width(parts, size) - 16 - dx
        _, x, prev_hip, _, ladder, _ = frames[-1]
        if on_ladder:
            move(0.6, x_start, prev_hip, 60, x_start)  # roll the ladder (with him on it) to the line
            move(0.3 + abs(hip - prev_hip) / 300, x_start, hip, angle, x_start)  # climb up or down
            starts.append(frames[-1][0])
            move(secs, x_end, hip, angle, x_end, True)  # spray, the ladder rolls along
        else:
            if prev_hip != GROUND_HIP:
                move(0.3 + abs(GROUND_HIP - prev_hip) / 300, x, GROUND_HIP, 60, ladder)  # climb down
                move(0.8, x_start, GROUND_HIP, angle, LADDER_PARK)  # walk over, push the ladder away
            else:
                move(0.7, x_start, GROUND_HIP, angle, ladder)
            starts.append(frames[-1][0])
            move(secs, x_end, GROUND_HIP, angle, ladder if prev_hip == GROUND_HIP else LADDER_PARK, True)
    move(0.5, frames[-1][1], GROUND_HIP, 70, frames[-1][4])  # done: he lowers the can and glances back
    return frames, starts, frames[-1][0]


def _starts_at(svg, secs):
    """Make every animation in svg (that has no begin of its own) start secs after the page opens."""
    for tag_name in ("<animateTransform ", "<animate "):
        svg = svg.replace(tag_name, f'{tag_name}begin="{secs:.2f}s" ')
    return svg.replace(f'begin="{secs:.2f}s" begin=', "begin=")


def _police_chase(x_portals, t_run):
    """Portals runs off to the right, two police officers and their dog after him. Returns the
    SVG and when the last of them is out of the picture."""
    runs = [
        # (what, starts at, starts after t_run, distance, seconds)
        (crew.portals(x_portals, Walk(dist=900 - x_portals, secs=1.6, stride=0.35), idle="still"), 0.0, 1.6),
        (crew.police_dog(10, Walk(dist=1000, secs=2.6, stride=0.3)), 0.7, 2.6),
        (crew.police_officer(-60, Walk(dist=1000, secs=2.6, stride=0.4), shout="STOP! POLICE!", leash_to=70), 0.7, 2.6),
        (crew.police_officer(-150, Walk(dist=1090, secs=2.8, stride=0.4)), 0.9, 2.8),
    ]
    parts = []
    for svg, delay, secs in runs:
        start = t_run + delay
        parts.append(f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="{start:.2f}s"/>'
                     f'<set attributeName="visibility" to="hidden" begin="{start + secs:.2f}s"/>{_starts_at(svg, start)}</g>')
    end = max(t_run + delay + secs for _, delay, secs in runs) + 0.3
    # everyone stands on the intro's sidewalk (the crew is drawn for the street, 45 px higher)
    return (f'<g id="police-chase" transform="translate(0 45)">{"".join(parts)}</g>\n  <!-- end police-chase -->', end)


def intro_screen():
    """After START: Portals tells the story by painting it on the brick wall, line by line, in
    pieces like the ones on the train. For the top lines he climbs a rolling ladder and pushes it
    along; the bottom lines he paints from the sidewalk. When he is done he runs off to the right,
    two police officers and their dog after him. Then a LET'S GO piece appears."""
    frames, starts, total = _painter_route()
    chase, end = _police_chase(frames[-1][1], total)
    times = ";".join(f"{t / total:.4f}" for t, *_ in frames)

    def track(fn):
        return ";".join(fn(*f[1:]) for f in frames)

    clips, lines = [], []
    for i, ((parts, size, y, secs), start) in enumerate(zip(INTRO_LINES, starts)):
        width = _text_width(parts, size)
        clips.append(
            f'<clipPath id="line{i}"><rect x="{INTRO_X - 6}" y="{y - size - 8}" width="0" height="{size + 22}">'
            f'<animate attributeName="width" from="0" to="{width}" begin="{start:.2f}s" dur="{secs}s" fill="freeze"/>'
            f'</rect></clipPath>')
        lines.append(f'<g class="story-line" clip-path="url(#line{i})">{piece_parts(INTRO_X, y, parts, size)}</g>')
    clip_defs = "".join(f"    {c}\n" for c in clips)
    keys = f'keyTimes="{times}" dur="{total:.2f}s" fill="freeze"'
    painter_move = f'<animateTransform attributeName="transform" type="translate" values="{track(lambda x, h, a, l, m: f"{x:.1f} {h:.1f}")}" {keys}/>'
    arm = f'<animateTransform attributeName="transform" type="rotate" values="{track(lambda x, h, a, l, m: f"{a:.1f} 16 -46")}" {keys}/>'
    # in a discrete animation value i holds until frame i+1, so it is the flag of the segment after it
    spraying = ";".join("1" if f[5] else "0" for f in frames[1:]) + ";0"
    mist = (f'<animate attributeName="opacity" values="{spraying}" '
            f'keyTimes="{times}" dur="{total:.2f}s" calcMode="discrete" fill="freeze"/>')
    ladder_move = f'<animateTransform attributeName="transform" type="translate" values="{track(lambda x, h, a, l, m: f"{l:.1f} 0")}" {keys}/>'
    rungs = "".join(f'<path d="M-24 {y}H24" stroke="#9aa0a8" stroke-width="5"/>' for y in range(172, 400, 26))
    body = defs(DUSK, extra=clip_defs) + f"""
  <!-- the whole frame is the wall Portals paints on -->
  <rect width="800" height="450" fill="url(#bricks)"/>
  <rect width="800" height="450" fill="#1f1238" opacity="0.3"/>
  <g opacity="0.35">
    {tag(600, 40, "Sopranos", "#111", 18, -6)}
    {tag(740, 140, "BX", "#f4f4f4", 20, 8)}
    {tag(20, 300, "Reekz", "#3fa9f5", 16, -10)}
    {star(770, 60, 10, "#ffd23f")}
  </g>

  <!-- the story -->
  {"".join(lines)}
  <!-- end story -->

  <!-- sidewalk -->
  <rect y="385" width="800" height="65" fill="#9a9aa2"/>
  <path d="M0 385H800" stroke="#6e6e76" stroke-width="3"/>
  <g stroke="#7d7d85" stroke-width="2"><path d="M100 385V450M300 385V450M500 385V450M700 385V450"/></g>

  <!-- the rolling ladder he climbs for the top lines -->
  <g id="ladder">
    {ladder_move}
    <path d="M-24 150V402M24 150V402" stroke="#c9ccd2" stroke-width="6"/>
    {rungs}
    <circle cx="-24" cy="406" r="7" fill="#222"/><circle cx="24" cy="406" r="7" fill="#222"/>
  </g>

  <!-- Portals paints the story -->
  <g id="painter">
    <set attributeName="visibility" to="hidden" begin="{total:.2f}s"/>
    {painter_move}
{crew.portals_back(arm, mist)}
  </g>

  <!-- Portals is done and runs for it: the police are after him -->
  {chase}

  <!-- LET'S GO: appears when the story is on the wall, starts the game -->
  <g data-action="go" role="button" tabindex="0" aria-label="Let's go: start the game" opacity="0">
    <title>Let's go</title>
    <animate attributeName="opacity" from="0" to="1" begin="{end:.1f}s" dur="0.5s" fill="freeze"/>
    <rect x="606" y="290" width="180" height="52" rx="10" fill="#111" stroke="#ffd23f" stroke-width="3"/>
    {piece(696, 327, "LET'S GO ▶", "gBlueGreen", size=30, rot=-2, anchor="middle", fit=150)}
  </g>

  <!-- SKIP: jumps to the end (the whole story on the wall, LET'S GO there); gone once it's over -->
  <g data-action="skip" role="button" tabindex="0" aria-label="Skip to the end of the story">
    <title>Skip</title>
    <set attributeName="visibility" to="hidden" begin="{end:.1f}s"/>
    <rect x="684" y="60" width="100" height="38" rx="9" fill="#111" stroke="#f4f4f4" stroke-width="2.5" opacity="0.9"/>
    {piece(734, 88, "SKIP ▶▶", "gWhite", size=22, rot=-2, anchor="middle", fit=80)}
  </g>
"""
    return _svg(body, "intro-screen", end=f"{end:.1f}", cues=_intro_sounds(frames, total, end))


# The intro's sound effects, played by the page under the intro song (SONGS[INTRO_MUSIC] at 0.7).
# The volumes put them 6-10 dB below the song, measured from the files' loudness, so they stay
# in the background: the spray -15 dB, the shout -15 dB, the siren -13 dB, the (quiet) dog -21 dB.
INTRO_SOUNDS = {"spray": 0.3, "police_shout": 0.5, "siren": 0.28, "police_dog": 0.65}


def _intro_sounds(frames, total, end):
    """When each sound plays: the spray can hisses while Portals sprays a line (and goes on where it
    stopped for the next one); when he runs, the siren comes, the officer shouts STOP! POLICE!
    and the dog barks, until the chase is out of the picture."""
    spray = [[round(frames[i - 1][0], 2), round(frames[i][0], 2)] for i in range(1, len(frames)) if frames[i][5]]
    chase = {"siren": [total, end], "police_shout": [total + 0.7, min(total + 2.4, end)],
             "police_dog": [total + 0.7, end]}
    cues = [{"src": "app/static/audio/intro/spray.mp3", "on": spray, "vol": INTRO_SOUNDS["spray"], "resume": True}]
    for name, (a, b) in chase.items():
        cues.append({"src": f"app/static/audio/intro/{name}.mp3", "on": [[round(a, 2), round(b, 2)]],
                     "vol": INTRO_SOUNDS[name]})
    return cues


# --- the escape: from the story intro to the basement ---

PORTAL = (580, 425, 100, 24)  # the portal Portals sprays on the ground: centre, half width, half height
CEILING_PORTAL = (700, 34, 56, 14)  # where he drops into the basement (above his spot in the basement scene)
PORTALS_SAYS = "THEY CALL ME PORTALS FOR A REASON."
ESCAPE_END = 10.8


def _shown(a, b, svg):
    """svg shows from a to b seconds (b None: until the end)."""
    hide = f'<set attributeName="visibility" to="hidden" begin="{b:.2f}s"/>' if b is not None else ""
    return f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="{a:.2f}s"/>{hide}{svg}</g>'


def _ellipse_length(rx, ry):
    return math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))  # Ramanujan


def _portal(pid, cx, cy, rx, ry, t_open, t_close=None, down=False, beam=True):
    """A portal lying flat (on the ground, or on the ceiling with down=True), or standing on a
    wall (ry > rx, beam=False): it opens at t_open into a glowing tunnel, rings falling away into
    the depth, a swirl turning, sparks crackling along the rim, a beam of light and sparkles
    coming out of it."""
    show_beam = beam
    close = (f'<animate attributeName="rx" values="{rx - 6};0" begin="{t_close:.2f}s" dur="0.4s" fill="freeze"/>'
             f'<animate attributeName="ry" values="{ry - 2};0" begin="{t_close:.2f}s" dur="0.4s" fill="freeze"/>') if t_close else ""
    hole = (f'<clipPath id="{pid}Hole"><ellipse cx="{cx}" cy="{cy}" rx="0" ry="0">'
            f'<animate attributeName="rx" values="0;{rx - 6}" begin="{t_open:.2f}s" dur="0.8s" fill="freeze"/>'
            f'<animate attributeName="ry" values="0;{ry - 2}" begin="{t_open:.2f}s" dur="0.8s" fill="freeze"/>{close}'
            f'</ellipse></clipPath>')
    tunnel = "".join(
        f'<ellipse class="tunnel" cx="{cx}" cy="{cy + (-4 if down else 4)}" rx="{rx}" ry="{ry}" fill="none" stroke="{c}" stroke-width="3">'
        f'<animate attributeName="rx" values="{rx};{rx * 0.06:.1f}" dur="1.2s" begin="{t_open + b:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="ry" values="{ry};{ry * 0.06:.1f}" dur="1.2s" begin="{t_open + b:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;0" dur="1.2s" begin="{t_open + b:.2f}s" repeatCount="indefinite"/></ellipse>'
        for c, b in (("#7ef0ff", 0), ("#c58bff", 0.3), ("#ff6fd8", 0.6), ("#f4f4f4", 0.9)))
    arms = "".join(
        f'<path d="M0 0Q{k * 0.6:.0f} {-k * 0.2:.0f} {k} {-k * 0.9:.0f}" stroke="{c}" stroke-width="{w}" fill="none" '
        f'stroke-linecap="round" opacity="0.7" transform="rotate({a})"/>'
        for k, c, w, a in ((rx, "#7ef0ff", 8, 0), (rx, "#c58bff", 8, 120), (rx, "#ff6fd8", 8, 240),
                           (rx * 0.6, "#f4f4f4", 4, 60), (rx * 0.6, "#f4f4f4", 4, 180), (rx * 0.6, "#f4f4f4", 4, 300)))
    swirl = (f'<g transform="translate({cx} {cy}) scale(1 {ry / rx:.3f})"><g>'
             f'<animateTransform attributeName="transform" type="rotate" from="0" to="{-360 if down else 360}" dur="1.4s" repeatCount="indefinite"/>'
             f'{arms}</g></g>')
    rim = _ellipse_length(rx, ry)
    sparks = (f'<ellipse class="sparks" cx="{cx}" cy="{cy}" rx="{rx + 2}" ry="{ry + 1}" fill="none" stroke="#f4feff" stroke-width="3" '
              f'stroke-dasharray="4 26 10 34" stroke-linecap="round" opacity="0">'
              f'<animate attributeName="opacity" values="0;1" begin="{t_open:.2f}s" dur="0.3s" fill="freeze"/>'
              f'<animate attributeName="stroke-dashoffset" from="0" to="{-rim:.0f}" dur="1.1s" repeatCount="indefinite"/></ellipse>')
    reach = 300 if down else -300
    beam = (f'<polygon class="beam" points="{cx - rx},{cy} {cx + rx},{cy} {cx + rx * 0.55:.0f},{cy + reach} {cx - rx * 0.55:.0f},{cy + reach}" '
            f'fill="url(#{"beamDown" if down else "beamUp"})" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.8;0.55;0.8" keyTimes="0;0.3;0.65;1" begin="{t_open:.2f}s" dur="0.9s" fill="freeze"/></polygon>')
    beam = beam if show_beam else ""
    sparkles = "".join(
        f'<circle class="sparkle" cx="{cx + dx}" cy="{cy}" r="2.5" fill="{c}" opacity="0">'
        f'<animate attributeName="cy" values="{cy};{cy + (90 if down else -110) * k:.0f}" dur="1.3s" begin="{t_open + b:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;1;0" dur="1.3s" begin="{t_open + b:.2f}s" repeatCount="indefinite"/></circle>'
        for dx, c, k, b in ((-60, "#7ef0ff", 1, 0), (-25, "#f4f4f4", 0.7, 0.4), (10, "#ff6fd8", 1.1, 0.2), (45, "#c58bff", 0.8, 0.7),
                            (70, "#f4f4f4", 0.9, 1.0), (-80, "#ff6fd8", 0.6, 0.9), (30, "#7ef0ff", 1.2, 0.55)))
    closing = (f'<set attributeName="visibility" to="hidden" begin="{t_close + 0.4:.2f}s"/>') if t_close else ""
    return f'''<g id="{pid}">{closing}
    {hole}
    <ellipse cx="{cx}" cy="{cy}" rx="{rx + 40}" ry="{ry + 16}" fill="url(#portalGlow)" opacity="0">
      <animate attributeName="opacity" values="0;1;0.7;1" keyTimes="0;0.3;0.6;1" begin="{t_open:.2f}s" dur="1s" fill="freeze"/></ellipse>
    {beam}
    <g clip-path="url(#{pid}Hole)">
      <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#portalDepth)"/>
      {tunnel}{swirl}
    </g>
    {sparks}{sparkles}
  </g>
  <!-- end {pid} -->'''


def _night_alley():
    """A back alley in the Bronx at night: sky with stars and the moon over the skyline, a brick
    building with lit windows, a fire escape and posters, the alley floor with puddles, a steaming
    manhole, a dumpster, a street light, and the police car at the edge, its lights going."""
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f4f4f4" opacity="0.8">'
                    f'<animate attributeName="opacity" values="0.8;0.2;0.8" dur="{d}s" repeatCount="indefinite"/></circle>'
                    for x, y, r, d in ((40, 30, 1.5, 2.1), (160, 18, 1.2, 3.0), (300, 40, 1.6, 2.6), (420, 14, 1.2, 1.9),
                                       (520, 46, 1.4, 2.8), (610, 22, 1.2, 2.3), (770, 34, 1.5, 3.3), (250, 70, 1, 2.4)))
    windows = "".join(
        f'<rect x="{x}" y="{y}" width="44" height="56" fill="{"#ffd98a" if lit else "#1c1830"}" stroke="#3a2a2a" stroke-width="4"/>'
        f'<path d="M{x + 22} {y}V{y + 56}M{x} {y + 28}H{x + 44}" stroke="#3a2a2a" stroke-width="3"/>'
        + (f'<rect x="{x + 4}" y="{y + 4}" width="16" height="20" fill="#7a3170" opacity="0.5"/>' if lit else "")
        for x, y, lit in ((70, 176, True), (250, 176, False), (400, 176, True), (250, 262, True), (70, 262, False)))
    fire_escape = '''<g id="fire-escape" stroke="#141418" stroke-width="3" fill="none">
      <rect x="560" y="166" width="180" height="70" fill="#1c1830" stroke="#3a2a2a" stroke-width="4"/>
      <rect x="582" y="176" width="60" height="56" fill="#ffd98a" stroke="#3a2a2a" stroke-width="4"/>
      <path d="M548 240H752M548 228H752M548 228V240M752 228V240"/>
      <path d="M560 228V240M590 228V240M620 228V240M650 228V240M680 228V240M710 228V240M740 228V240" stroke-width="2"/>
      <path d="M548 320H752M548 308H752M548 308V320M752 308V320"/>
      <path d="M560 308V320M600 308V320M640 308V320M680 308V320M720 308V320" stroke-width="2"/>
      <path d="M600 240L700 308M610 240L710 308" stroke-width="3"/>
      <path d="M603 248L611 248M620 260L628 260M637 272L645 272M654 284L662 284M671 296L679 296" stroke-width="2"/>
      <path d="M720 320V380M740 320V380M720 336H740M720 352H740M720 368H740" stroke-width="2"/>
    </g>'''
    posters = f'''<g id="posters">
      <g transform="rotate(-3 150 330)"><rect x="118" y="290" width="74" height="62" fill="#ffd23f"/>
        <text x="155" y="312" font-family="{FONT}" font-size="15" fill="#c0392b" text-anchor="middle">BLOCK</text>
        <text x="155" y="330" font-family="{FONT}" font-size="15" fill="#c0392b" text-anchor="middle">PARTY</text>
        <text x="155" y="345" font-family="Arial, sans-serif" font-size="8" fill="#111" text-anchor="middle">SAT · 149TH ST</text>
        <path d="M180 352L192 340V352Z" fill="#2a1a20"/></g>
      <g transform="rotate(4 450 320)"><rect x="412" y="282" width="78" height="66" fill="#ff4f79"/>
        <text x="451" y="306" font-family="{FONT}" font-size="14" fill="#f4f4f4" text-anchor="middle">DISCO</text>
        <text x="451" y="324" font-family="{FONT}" font-size="14" fill="#f4f4f4" text-anchor="middle">FEVER</text>
        <text x="451" y="340" font-family="Arial, sans-serif" font-size="8" fill="#111" text-anchor="middle">DJ BATTLE · SATURDAY</text></g>
    </g>'''
    puddles = "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * 0.18:.1f}" fill="#2a2a3a"/>'
        f'<ellipse cx="{x}" cy="{y}" rx="{rx - 4}" ry="{rx * 0.14:.1f}" fill="#ff2b2b" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.5;0" dur="0.6s" repeatCount="indefinite"/></ellipse>'
        f'<ellipse cx="{x}" cy="{y}" rx="{rx - 4}" ry="{rx * 0.14:.1f}" fill="#2b6bff" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.5;0" dur="0.6s" begin="0.3s" repeatCount="indefinite"/></ellipse>'
        for x, y, rx in ((250, 400, 46), (420, 440, 34), (740, 412, 30)))
    steam = "".join(
        f'<ellipse cx="{180 + dx}" cy="430" rx="14" ry="8" fill="#c9ccd2" opacity="0">'
        f'<animate attributeName="cy" values="430;340" dur="2.4s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="rx" values="10;34" dur="2.4s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0.35;0" dur="2.4s" begin="{b}s" repeatCount="indefinite"/></ellipse>'
        for dx, b in ((0, 0), (8, 0.8), (-6, 1.6)))
    lights = "".join(
        f'<rect width="800" height="370" fill="{c}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.2;0" dur="0.6s" begin="{b}s" repeatCount="indefinite"/></rect>'
        for c, b in (("#ff2b2b", 0), ("#2b6bff", 0.3)))
    return f'''
  <!-- the night sky over the skyline -->
  <g id="night-sky"><rect width="800" height="200" fill="url(#sky)"/>{stars}
    <circle cx="560" cy="52" r="24" fill="#fff1c1"/><circle cx="569" cy="46" r="22" fill="url(#sky)" opacity="0.35"/></g>
{skyline(body="#1c1430", tower="#140e24", opacity=0.95, windows=True)}
  <!-- the building along the alley -->
  <rect y="150" width="800" height="222" fill="url(#bricks)"/>
  <rect y="150" width="800" height="222" fill="#0b0716" opacity="0.45"/>
  <rect y="142" width="800" height="12" fill="#2a1a20"/><rect y="152" width="800" height="4" fill="#4a3030"/>
  {windows}
  {fire_escape}
  <g opacity="0.5">{tag(30, 250, "Sopranos", "#111", 16, -6)}{tag(330, 370, "GoodFellas", "#7ed957", 17, -4)}{tag(500, 270, "BX 77", "#f4f4f4", 16, 8)}</g>
  {posters}
  <!-- the street light -->
  <g id="streetlight"><path d="M120 400V200Q120 182 148 182H172" stroke="#141418" stroke-width="7" fill="none"/>
    <path d="M160 186H196L188 196H168Z" fill="#3a3a40"/><path d="M168 196L110 400H270L188 196Z" fill="#ffe9a8" opacity="0.1"/></g>
  {lights}
  <!-- the alley floor -->
  <rect y="370" width="800" height="80" fill="url(#alleyFloor)"/>
  <path d="M0 372H800" stroke="#4a4a52" stroke-width="3"/>
  <path d="M60 420L110 412L130 426M520 446L560 436M640 392L700 398" stroke="#141418" stroke-width="2" fill="none"/>
  <g id="puddles">{puddles}</g>
  <g id="manhole"><ellipse cx="180" cy="432" rx="34" ry="8" fill="#141418" stroke="#4a4a52" stroke-width="2"/>
    <path d="M156 432H204M166 428H194M166 436H194" stroke="#2a2a32" stroke-width="2"/>{steam}</g>
  <g id="dumpster"><rect x="676" y="330" width="116" height="66" rx="4" fill="#2e5e3a" stroke="#141418" stroke-width="3"/>
    <path d="M670 330L798 322V334L670 340Z" fill="#244a2e" stroke="#141418" stroke-width="3"/>
    <text x="734" y="372" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#9ac0a2" text-anchor="middle">DSNY</text>
    <circle cx="690" cy="400" r="5" fill="#141418"/><circle cx="778" cy="400" r="5" fill="#141418"/>
    <ellipse cx="660" cy="392" rx="20" ry="14" fill="#141418"/><ellipse cx="642" cy="398" rx="14" ry="10" fill="#1c1c22"/></g>
  <!-- the police car at the edge, its lights going -->
  <g id="police-car">
    <path d="M-40 352H60Q74 352 84 366L104 368Q118 370 118 384V400H-40Z" fill="#f4f4f4" stroke="#141418" stroke-width="3"/>
    <path d="M-40 376H118" stroke="#1f3e8a" stroke-width="7"/>
    <path d="M-30 354H50L70 368H-30Z" fill="#2b3440"/>
    <text x="30" y="394" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#1f3e8a" text-anchor="middle">POLICE</text>
    <circle cx="0" cy="402" r="14" fill="#141418"/><circle cx="84" cy="402" r="14" fill="#141418"/>
    <circle cx="0" cy="402" r="5" fill="#9a9aa2"/><circle cx="84" cy="402" r="5" fill="#9a9aa2"/>
    <rect x="-10" y="342" width="22" height="10" rx="3" fill="#ff2b2b"><animate attributeName="opacity" values="1;0.2;1" dur="0.6s" repeatCount="indefinite"/></rect>
    <rect x="14" y="342" width="22" height="10" rx="3" fill="#2b6bff"><animate attributeName="opacity" values="0.2;1;0.2" dur="0.6s" repeatCount="indefinite"/></rect>
  </g>'''


def _basement_landing():
    """The basement exactly as the basement scene shows it (the same room, just nothing to click
    yet), with Portals' spot by the graffiti corner still empty. A portal opens in the ceiling,
    Portals drops out of it, lands, and goes back to spraying his corner."""
    cx, cy, rx, ry = CEILING_PORTAL
    land = 9.5
    fall = (f'<g><animateTransform attributeName="transform" type="translate" values="700 -60;700 327" '
            f'begin="9.0s" dur="0.5s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.5 0 1 1"/>'
            f'<g transform="translate(0 48)"><g>'
            f'<animateTransform attributeName="transform" type="scale" values="1 1;1.18 0.78;0.95 1.06;1 1" begin="{land}s" dur="0.4s" fill="freeze"/>'
            f'<g transform="translate(0 -48)">{crew.portals(0, None, y0=0, idle="still")}</g></g></g></g>')
    dust = "".join(
        f'<ellipse cx="{700 + dx}" cy="375" rx="6" ry="4" fill="#c9ccd2" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.7;0" begin="{land}s" dur="0.6s" fill="freeze"/>'
        f'<animate attributeName="cx" values="{700 + dx * 0.3};{700 + dx * 2}" begin="{land}s" dur="0.6s" fill="freeze"/>'
        f'<animate attributeName="rx" values="6;16" begin="{land}s" dur="0.6s" fill="freeze"/></ellipse>'
        for dx in (-30, -14, 14, 30))
    wow = "".join(f'<text x="{x}" y="200" font-family="{FONT}" font-size="26" fill="#ffd23f" stroke="#111" stroke-width="1.5" '
                  f'text-anchor="middle" opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" '
                  f'begin="{land + 0.1:.1f}s" dur="1.1s" fill="freeze"/>!</text>' for x in (178, 236, 454, 548))
    _, room = _basement_room(still=True)
    back_in_corner = crew.portals(700, None, spraying=True, idle="still")
    return f'''<g id="basement-landing" opacity="0">
    <animate attributeName="opacity" values="0;1" begin="8.4s" dur="0.4s" fill="freeze"/>
    {room}
    {wow}
    {_portal("ceiling-portal", cx, cy, rx, ry, 8.6, t_close=10.0, down=True)}
    <g id="portals-lands">{_shown(9.0, 10.0, fall)}{dust}</g>
    <!-- end portals-lands -->
    <g id="portals-back-in-his-corner">{_shown(10.0, None, back_in_corner)}</g>
    <!-- end portals-back-in-his-corner -->
  </g>
  <!-- end basement-landing -->'''


def escape_screen():
    """After LET'S GO: Portals runs into a back alley at night, the police right behind him. He
    sprays a ring on the ground ("They call me Portals for a reason."), it opens into a portal
    and he jumps straight in. The officers come too late (WHERE'D HE GO?!), the camera dives in
    after him, and he drops out of the basement ceiling and lands with the crew. Then the game
    starts in the basement (by itself, or with SKIP)."""
    cx, cy, rx, ry = PORTAL
    ring_len = _ellipse_length(rx, ry)
    px = 430  # where Portals stops and sprays
    run_in = crew.portals(-60, Walk(dist=px + 60, secs=1.4, stride=0.35), idle="still")
    arm = ('<animateTransform attributeName="transform" type="rotate" '
           'values="45 16 -46;80 16 -46;55 16 -46;80 16 -46;45 16 -46" dur="0.85s" begin="1.5s" repeatDur="2.5s" fill="freeze"/>')
    mist = '<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.03;0.04;0.98;1" begin="1.4s" dur="2.6s" fill="freeze"/>'
    spraying = f'<g transform="translate({px} 372)">{crew.portals_back(arm, mist)}</g>'
    says_from, says_to = 2.5, 5.35
    bubble_w = 372
    says = f'''<g id="portals-says">{_shown(says_from, says_to, f"""<g>
      <rect x="{px - 170}" y="214" width="{bubble_w}" height="36" rx="12" fill="#f4f4f4" stroke="#111" stroke-width="2.5"/>
      <path d="M{px - 6} 250L{px} 266L{px + 10} 250Z" fill="#f4f4f4" stroke="#111" stroke-width="2"/>
      <rect x="{px - 8}" y="246" width="20" height="5" fill="#f4f4f4"/>
      <text x="{px - 170 + bubble_w / 2:.0f}" y="237" font-family="Arial Black, Arial, sans-serif" font-weight="bold" font-size="14" fill="#111" text-anchor="middle">{PORTALS_SAYS}</text></g>""")}</g>
  <!-- end portals-says -->'''
    jump = (f'<g><animateTransform attributeName="transform" type="translate" values="{px} 372;{(px + cx) / 2:.0f} 300;{cx} {cy - 10}" '
            f'keyTimes="0;0.55;1" begin="5.4s" dur="0.7s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1.05;0.15 0.35" keyTimes="0;0.55;1" begin="5.4s" dur="0.7s" fill="freeze" additive="sum"/>'
            f'{crew.portals(0, None, y0=0, idle="still")}</g>')
    splash = (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#f4feff" stroke-width="4" opacity="0">'
              f'<animate attributeName="opacity" values="0;1;0" begin="6.1s" dur="0.5s" fill="freeze"/>'
              f'<animate attributeName="rx" values="{rx * 0.5};{rx + 40}" begin="6.1s" dur="0.5s" fill="freeze"/>'
              f'<animate attributeName="ry" values="{ry * 0.5};{ry + 10}" begin="6.1s" dur="0.5s" fill="freeze"/></ellipse>')
    ring = f'''<g id="portal-ring">
    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="url(#gPinkYellow)" stroke-width="12" stroke-linecap="round"
             stroke-dasharray="{ring_len:.1f}" stroke-dashoffset="{ring_len:.1f}">
      <animate attributeName="stroke-dashoffset" from="{ring_len:.1f}" to="0" begin="1.5s" dur="1.6s" fill="freeze"/></ellipse>
    <ellipse cx="{cx}" cy="{cy}" rx="{rx + 9}" ry="{ry + 4}" fill="none" stroke="#3fa9f5" stroke-width="4"
             stroke-dasharray="{_ellipse_length(rx + 9, ry + 4):.1f}" stroke-dashoffset="{_ellipse_length(rx + 9, ry + 4):.1f}">
      <animate attributeName="stroke-dashoffset" from="{_ellipse_length(rx + 9, ry + 4):.1f}" to="0" begin="3.1s" dur="0.9s" fill="freeze"/></ellipse>
  </g>
  <!-- end portal-ring -->'''

    def dog(x, motion, a, b, woof):
        svg = _starts_at(crew.police_dog(x, motion or Walk(dist=0, secs=0.1, stride=0.1), bark=False), a)
        if woof:
            svg += (f'<text x="{x + 34}" y="{327 + 30 - 42}" font-family="{FONT}" font-size="20" fill="#ffd23f" stroke="#111" '
                    f'stroke-width="1">WOOF!<animate attributeName="opacity" values="1;0;1" dur="0.5s" repeatCount="indefinite"/></text>')
        return _shown(a, b, svg)

    police = "".join([
        # they run in right behind him ...
        _shown(0.6, 2.6, _starts_at(crew.police_officer(-190, Walk(dist=370, secs=2.0, stride=0.4), shout="STOP! POLICE!", leash_to=70), 0.6)),
        dog(-120, Walk(dist=370, secs=2.0, stride=0.3), 0.6, 2.6, True),
        _shown(0.7, 2.8, _starts_at(crew.police_officer(-270, Walk(dist=360, secs=2.1, stride=0.4)), 0.7)),
        # ... and stop, scared of the glowing ring
        _shown(2.6, 6.1, crew.police_officer(180, None, leash_to=70)),
        dog(250, None, 2.6, 6.1, False),
        _shown(2.8, 6.2, crew.police_officer(90, None)),
        # when he's gone they run to it: too late
        _shown(6.1, 6.8, _starts_at(crew.police_officer(180, Walk(dist=170, secs=0.7, stride=0.35), leash_to=70), 6.1)),
        dog(250, Walk(dist=170, secs=0.7, stride=0.3), 6.1, 6.8, False),
        _shown(6.2, 6.9, _starts_at(crew.police_officer(90, Walk(dist=170, secs=0.7, stride=0.35)), 6.2)),
        _shown(6.8, None, crew.police_officer(350, None, shout="WHERE'D HE GO?!", leash_to=70)),
        dog(420, None, 6.8, None, True),
        _shown(6.9, None, crew.police_officer(260, None)),
    ])
    zoom, ease = 8, 'calcMode="spline" keyTimes="0;1" keySplines="0.55 0 0.85 1"'
    camera = (f'<animateTransform attributeName="transform" type="translate" values="0 0;{400 - zoom * cx} {225 - zoom * cy}" '
              f'begin="7.4s" dur="1.2s" fill="freeze" {ease}/>'
              f'<animateTransform attributeName="transform" type="scale" values="1;{zoom}" begin="7.4s" dur="1.2s" fill="freeze" additive="sum" {ease}/>')
    night = (("0", "#07051a"), ("0.6", "#1f1238"), ("1", "#4a2050"))
    room_defs, _ = _basement_room(still=True)
    extra = room_defs + '''    <linearGradient id="alleyFloor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34343e"/><stop offset="1" stop-color="#18181e"/></linearGradient>
    <radialGradient id="portalGlow"><stop offset="0.55" stop-color="#7ef0ff" stop-opacity="0.8"/><stop offset="1" stop-color="#c58bff" stop-opacity="0"/></radialGradient>
    <radialGradient id="portalDepth"><stop offset="0" stop-color="#f4feff"/><stop offset="0.25" stop-color="#7ef0ff"/>
      <stop offset="0.6" stop-color="#5b2a9a"/><stop offset="1" stop-color="#0b0716"/></radialGradient>
    <linearGradient id="beamUp" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#7ef0ff" stop-opacity="0.55"/><stop offset="1" stop-color="#c58bff" stop-opacity="0"/></linearGradient>
    <linearGradient id="beamDown" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7ef0ff" stop-opacity="0.55"/><stop offset="1" stop-color="#c58bff" stop-opacity="0"/></linearGradient>
'''
    body = defs(night, extra=extra) + f'''
  <g id="camera">
    {camera}
  {_night_alley()}

  {ring}
  {_portal("portal", cx, cy, rx, ry, 4.0)}

  <!-- Portals: runs in, sprays the portal on the ground, says his line, jumps straight in -->
  <g transform="translate(0 45)">{_shown(0, 1.4, _starts_at(run_in, 0))}</g>
  {_shown(1.4, 5.4, spraying)}
  {says}
  <g id="portals-jumps">{_shown(5.4, 6.1, jump)}{splash}</g>
  <!-- end portals-jumps -->

  <!-- the police, right behind him, and too late -->
  <g id="escape-police" transform="translate(0 45)">{police}</g>
  <!-- end escape-police -->
  </g>
  <!-- end camera -->

  <!-- through the portal: he drops into the basement -->
  {_basement_landing()}

  <!-- SKIP: straight to the basement (gone once we're there, out of the ceiling portal's way) -->
  <g data-action="arrive" role="button" tabindex="0" aria-label="Skip to the basement">
    <title>Skip</title>
    <set attributeName="visibility" to="hidden" begin="8.4s"/>
    <rect x="684" y="60" width="100" height="38" rx="9" fill="#111" stroke="#f4f4f4" stroke-width="2.5" opacity="0.9"/>
    {piece(734, 88, "SKIP ▶▶", "gWhite", size=22, rot=-2, anchor="middle", fit=80)}
  </g>
'''
    cues = [
        {"src": "app/static/audio/intro/siren.mp3", "on": [[0.0, 8.4]], "vol": INTRO_SOUNDS["siren"], "resume": True},
        {"src": "app/static/audio/intro/police_shout.mp3", "on": [[0.7, 2.4]], "vol": INTRO_SOUNDS["police_shout"]},
        {"src": "app/static/audio/intro/police_dog.mp3", "on": [[0.8, 2.5], [6.8, 8.4]], "vol": INTRO_SOUNDS["police_dog"]},
        {"src": "app/static/audio/intro/spray.mp3", "on": [[1.5, 4.0]], "vol": INTRO_SOUNDS["spray"], "resume": True},
        {"src": "app/static/audio/escape/portals_says.mp3", "on": [[says_from, says_to]], "vol": 1.0},
    ]
    return _svg(body, "escape-screen", end=f"{ESCAPE_END:.1f}", cues=cues, auto=("arrive", ESCAPE_END))


# Classic breaks of the time, scattered over the basement floor after the break-in:
# (title, artist, sleeve colour, x, y, rotation)
BASEMENT_SLEEVES = [
    ("apache", ["APACHE"], "#e8742a", 120, 374, -12),
    ("funky_drummer", ["FUNKY", "DRUMMER"], "#2e8b57", 232, 412, 8),
    ("its_just_begun", ["IT'S JUST", "BEGUN"], "#7d3cff", 292, 420, -6),
    ("impeach_the_president", ["IMPEACH THE", "PRESIDENT"], "#c0392b", 420, 420, 10),
    ("vitamin_c", ["VITAMIN C"], "#5aa832", 758, 386, -8),
    ("the_mexican", ["THE", "MEXICAN"], "#ffd23f", 36, 374, 6),
]
BASEMENT_DISCS = [(150, 400, "#ff4f79"), (252, 440, "#ffd23f"), (356, 440, "#7ef0ff"), (520, 440, "#7ed957"),
                  (560, 446, "#ff8a3d"), (782, 400, "#f4f4f4"), (205, 446, "#3fa9f5"), (238, 390, "#ff4f79"),
                  (372, 392, "#f4f4f4"), (470, 440, "#ff4f79")]


def _floor():
    """A concrete basement floor, with cracks and a darker strip along the back wall."""
    return ('<rect id="concrete-floor" y="340" width="800" height="110" fill="#4b4651"/>'
            '<rect y="340" width="800" height="22" fill="#0b0716" opacity="0.3"/>'
            '<path d="M60 396L120 404L150 420M300 446L340 430L372 438M690 360L720 372" stroke="#3a3540" stroke-width="2" fill="none"/>')


def _dance_floor(bottom=450, vp=(400, 160)):
    """A little black and white checkerboard dance floor in perspective, where Reekz breaks."""
    rows = [370, 382, 396, 412, 432]
    vx, vy = vp

    def at(xb, y):
        return vx + (xb - vx) * (y - vy) / (bottom - vy)

    tiles = []
    columns = list(range(440, 680, 40))
    for i in range(len(rows) - 1):
        y1, y2 = rows[i], rows[i + 1]
        for j, xb in enumerate(columns):
            colour = "#121212" if (i + j) % 2 else "#d9d2c3"
            pts = f"{at(xb, y1):.1f},{y1} {at(xb + 40, y1):.1f},{y1} {at(xb + 40, y2):.1f},{y2} {at(xb, y2):.1f},{y2}"
            tiles.append(f'<polygon points="{pts}" fill="{colour}"/>')
    edge = (f"{at(columns[0], rows[0]):.1f},{rows[0]} {at(columns[-1] + 40, rows[0]):.1f},{rows[0]} "
            f"{at(columns[-1] + 40, rows[-1]):.1f},{rows[-1]} {at(columns[0], rows[-1]):.1f},{rows[-1]}")
    return (f'<g id="checkerboard-floor">{"".join(tiles)}'
            f'<polygon points="{edge}" fill="none" stroke="#111" stroke-width="2"/></g>')


def _sleeve(record, lines, colour, x, y, rot, when="", still=False):
    """A record sleeve lying on the floor: title on one or two lines, artist underneath. Clicking it
    has Needle put the record on (pick:<record>); it is gone from the floor while he has it.
    when: more conditions for showing it (e.g. "has-vinyl"). still: just the picture of it."""
    artist = RECORDS[record]["artist"].upper()
    top = y - 4 - 4 * (len(lines) - 1)
    text = "".join(f'<text x="{x}" y="{top + k * 9}" font-family="{FONT}" font-size="8" fill="#111" text-anchor="middle">{line}</text>'
                   for k, line in enumerate(lines))
    button = "" if still else (f' data-action="pick:{record}" role="button" tabindex="0" '
                               f'aria-label="Put on {RECORDS[record]["title"]}"')
    overlay = "<g>" if still else f'<g data-overlay="{(when + " ") if when else ""}!pick-{record}">'
    return (f'{overlay}<g class="record" transform="rotate({rot} {x} {y})"{button}>'
            f'<title>{" ".join(lines)} – {artist}</title>'
            f'<rect x="{x - 25}" y="{y - 25}" width="50" height="50" fill="{colour}" stroke="#111" stroke-width="1.5"/>'
            f'<path d="M{x + 25} {y - 25}A12 12 0 0 1 {x + 13} {y - 13}" fill="none" stroke="#111" stroke-width="5" opacity="0.8"/>'
            f'{text}<text x="{x}" y="{y + 18}" font-family="Arial, sans-serif" font-size="4.2" font-weight="bold" fill="#111" text-anchor="middle"'
            + (' textLength="42" lengthAdjust="spacingAndGlyphs"' if len(artist) > 16 else "") + f'>{artist}</text>'
            '</g></g>')


def _disc(x, y, label):
    return (f'<g class="record"><ellipse cx="{x}" cy="{y}" rx="20" ry="7" fill="#111" stroke="#3a3a3a" stroke-width="1.5"/>'
            f'<ellipse cx="{x}" cy="{y}" rx="6" ry="2.2" fill="{label}"/></g>')


def _woofer(cx, cy, r, beat_delay=0):
    return (f'<g transform="translate({cx} {cy})">'
            f'<circle r="{r}" fill="#2a2a2a" stroke="#000" stroke-width="3"/>'
            f'<g><animateTransform attributeName="transform" type="scale" values="1;1.09;1" dur="0.5s" begin="{beat_delay}s" repeatCount="indefinite"/>'
            f'<circle r="{r * 0.82:.0f}" fill="#4a4a4a"/><circle r="{r * 0.55:.0f}" fill="#5c5c5c"/>'
            f'<circle r="{r * 0.22:.0f}" fill="#1a1a1a"/></g></g>')


# Who says what in the basement: name on the bubble, its colour, and the spot the bubble's
# tail points to (the speaker's head; Reekz is on the floor, breaking).
HQ_SPEAKERS = {
    "needle": ("FANTASTIC NEEDLE", "#d02b2b", (236, 238)),
    "bible": ("MC BIBLE", "#2e8b57", (454, 240)),
    "meyhem": ("MC MEYHEM", "#6b3fa8", (178, 240)),
    "portals": ("PORTALS", "#3d6fb6", (700, 236)),
    "reekz": ("REEKZ", "#c0392b", (548, 288)),
}


def _wrap(text, width=26):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def _dialogue(lines, speakers, kind="talk"):
    """One speech bubble per line, all hidden: the app shows the current one (data-overlay
    "<kind>-<n>"; kind "talk" for the first conversation, "back" for coming back), and a click on
    it (data-action "next") brings the next person in."""
    bubbles = []
    for i, (who, text) in enumerate(lines):
        name, colour, (hx, hy) = speakers[who]
        rows = _wrap(text)
        w = max(len(r) for r in rows) * 7.8 + 28
        h = 24 + 17 * len(rows)
        bottom = hy - 16 if who != "reekz" else hy - 24
        x = min(max(hx - w / 2, 8), 792 - w)
        y = bottom - h
        tail_x = min(max(hx, x + 18), x + w - 18)
        body = "".join(
            f'<text x="{x + w / 2:.1f}" y="{y + 36 + 17 * k}" font-family="{FONT}" font-size="14" fill="#111" '
            f'text-anchor="middle">{row.replace("&", "&amp;").replace("<", "&lt;").replace(chr(34), "&quot;")}</text>'
            for k, row in enumerate(rows))
        hint = "CLICK ▶" if i < len(lines) - 1 else "DONE ✓"
        bubbles.append(
            f'<g class="bubble" data-overlay="{kind}-{i}" style="display:none" data-action="next" role="button" '
            f'tabindex="0" aria-label="Next">'
            f'<path d="M{tail_x - 9:.1f} {bottom - 1}L{hx} {hy - 4}L{tail_x + 9:.1f} {bottom - 1}Z" fill="#f4f4f4" stroke="#111" stroke-width="2.5"/>'
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="10" fill="#f4f4f4" stroke="#111" stroke-width="2.5"/>'
            f'<path d="M{tail_x - 7:.1f} {bottom - 1}H{tail_x + 7:.1f}" stroke="#f4f4f4" stroke-width="4"/>'
            f'<text x="{x + 12:.1f}" y="{y + 16}" font-family="{FONT}" font-size="10" fill="{colour}" letter-spacing="1">{name}</text>'
            f'{body}<text x="{x + w - 10:.1f}" y="{y + 16}" font-family="{FONT}" font-size="9" fill="#888" '
            f'text-anchor="end" letter-spacing="1">{hint}</text></g>')
    if kind != "talk":  # e.g. coming back: its own group after the first conversation
        return f'''  <!-- the crew talks ({kind}) -->
  <g id="dialogue-{kind}">{"".join(bubbles)}</g>'''
    return f'''  <!-- the crew talks: one speech bubble at a time, the player clicks for the next one -->
  <g id="dialogue">{"".join(bubbles)}</g>
  <!-- end dialogue -->'''


# Where Needle stands to put a record on the right-hand turntable, and where that platter is.
DECK_STAND, DECK = 372, (411, 276)
THINK_COLOUR = "#ff6fa8"  # the pink sleeve of "Think (About It)"
NEEDLE_HOME = 236
WALK_SPEED = 150  # px per second


def _sleeve_icon(x, y, colour, w=22):
    """A small record sleeve (what Needle carries)."""
    return (f'<rect x="{x - w / 2}" y="{y - w / 2}" width="{w}" height="{w}" fill="{colour}" stroke="#111" stroke-width="1.5"/>'
            f'<circle cx="{x + w * 0.3}" cy="{y - w * 0.3}" r="{w * 0.22}" fill="#111"/>')


def _needle_walking(x_from, x_to, secs, trigger, start, carry=None):
    """Needle walking from x_from to x_to (either way), starting start seconds after trigger.
    carry: a sleeve colour he holds at his hand while walking."""
    dist = abs(x_to - x_from)
    walker = crew.needle(x_from, Walk(dist=dist, secs=secs), idle="still")
    if carry:
        walker += (f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{dist} 0" '
                   f'dur="{secs}s" fill="freeze"/>{_sleeve_icon(x_from + 22, 318, carry)}</g>')
    walker = _starts_on(trigger, walker, start)
    if x_to < x_from:  # walking left: the same walk, mirrored around where he starts
        walker = f'<g transform="translate({2 * x_from} 0) scale(-1 1)">{walker}</g>'
    return walker


def _window(trigger, a, b, svg):
    """Show svg from a to b seconds after trigger (b=None: and stay)."""
    hide = f'<set attributeName="visibility" to="hidden" begin="{trigger}.begin+{b:.2f}s"/>' if b is not None else ""
    return (f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="{trigger}.begin+{a:.2f}s"/>'
            f'{hide}{svg}</g>')


def _pick_record(record, x, colour):
    """Needle walks to the sleeve at x, bends down and picks it up, carries it to the turntable
    and puts the record on. Then the picture asks the app to show the turntable (data-auto-action)."""
    trigger = f"pick_{record}"
    t1 = max(0.5, abs(x - NEEDLE_HOME) / WALK_SPEED)
    t2 = t1 + 0.7
    t3 = t2 + max(0.5, abs(DECK_STAND - x) / WALK_SPEED)
    crouch = (f'<g transform="translate(0 12)">{crew.needle(x, idle="still")}</g>'
              f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -70" dur="0.7s" '
              f'fill="freeze"/>{_sleeve_icon(x + 10, 400, colour)}</g>')
    at_deck = (crew.needle(DECK_STAND, idle="nod") + spinning_record(*DECK, 26, colour, tilt=0.25)
               + f'{_sleeve_icon(DECK_STAND - 40, 300, colour)}')
    return (f'<g data-overlay="needle-busy pick-{record}" style="display:none" data-auto-action="play_record:{record}" '
            f'data-auto-delay="{t3 + 0.9:.2f}">'
            f'<animate id="{trigger}" attributeName="opacity" from="1" to="1" dur="0.1s" begin="indefinite"/>'
            + _window(trigger, 0, t1, _needle_walking(NEEDLE_HOME, x, t1, trigger, 0))
            + _window(trigger, t1, t2, _starts_on(trigger, crouch, t1))
            + _window(trigger, t2, t3, _needle_walking(x, DECK_STAND, t3 - t2, trigger, t2, carry=colour))
            + _window(trigger, t3, None, at_deck)
            + f'</g>\n  <!-- end pick-{record} -->')


TABLE_END, BEHIND_DECKS = 250, 360  # where Needle steps behind the DJ table, where he stands behind it


def _practice_walk_times():
    """Needle: home -> the sleeve (t1), picks it up (t2), -> the end of the table (t3), steps
    behind it and walks to the decks (t4)."""
    x = 368  # the sleeve of "Think About It"
    t1 = max(0.5, abs(x - NEEDLE_HOME) / WALK_SPEED)
    t2 = t1 + 0.7
    t3 = t2 + max(0.5, abs(x - TABLE_END) / WALK_SPEED)
    t4 = t3 + abs(BEHIND_DECKS - TABLE_END) / WALK_SPEED
    return x, t1, t2, t3, t4


def _practice_walk():
    """PRACTICE THE BREAK, in front of the table: Needle walks to the sleeve, picks it up and
    carries it to the end of the DJ table (then he is behind it: _needle_behind_decks). When he
    is ready at the decks the picture asks for the minigame (data-auto-action)."""
    trigger = "practiceGo"
    x, t1, t2, t3, t4 = _practice_walk_times()
    crouch = (f'<g transform="translate(0 12)">{crew.needle(x, idle="still")}</g>'
              f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -70" dur="0.7s" '
              f'fill="freeze"/>{_sleeve_icon(x + 10, 400, THINK_COLOUR)}</g>')
    return (f'<g data-overlay="practicing needle-busy" style="display:none" '
            f'data-auto-action="decks_ready" data-auto-delay="{t4 + 1.2:.2f}">'
            f'<animate id="{trigger}" attributeName="opacity" from="1" to="1" dur="0.1s" begin="indefinite"/>'
            + _window(trigger, 0, t1, _needle_walking(NEEDLE_HOME, x, t1, trigger, 0))
            + _window(trigger, t1, t2, _starts_on(trigger, crouch, t1))
            + _window(trigger, t2, t3, _needle_walking(x, TABLE_END, t3 - t2, trigger, t2, carry=THINK_COLOUR))
            + '</g>\n  <!-- end practicing -->')


def _needle_behind_decks():
    """Needle behind the DJ table (drawn before it, so the table is in front of him): he walks
    from its end to the decks, puts the record on and gets ready, nodding to the beat."""
    trigger = "practiceGo"
    _, _, _, t3, t4 = _practice_walk_times()
    ready = (crew.needle(BEHIND_DECKS, idle="nod")
             + '<path d="M348 268Q360 252 372 268" stroke="#222" stroke-width="4" fill="none"/>')  # headphones on
    return (f'<g id="needle-behind-decks" data-overlay="practicing" style="display:none">'
            + _window(trigger, t3, t4, _needle_walking(TABLE_END, BEHIND_DECKS, t4 - t3, trigger, t3, carry=THINK_COLOUR))
            + _window(trigger, t4, None, ready)
            + '</g>')


# one round on a deck: two loops of the drum break (so the switch still lands on a loop restart)
PRACTICE_BREAK = 2 * SONGS["think_about_it_break"]["loop_secs"]
# SPIN BACK counts in the last this many seconds of a round, smaller with every clean switch
PRACTICE_WINDOWS = (0.8, 0.6, 0.45, 0.35)  # four clean switches


def _deck(cx, cy, playing, colour):
    """A turntable from above with a copy of "Think About It": playing (spinning on), or the
    one that was just spun back to the start of the break and waits, cued up."""
    spin = ('<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
            'dur="1.8s" repeatCount="indefinite"/>' if playing else
            '<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};-540 {cx} {cy}" '
            'keyTimes="0;1" keySplines="0.2 0.8 0.4 1" calcMode="spline" dur="0.7s" fill="freeze"/>').format(cx=cx, cy=cy)
    grooves = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2a2a2a" stroke-width="1.2"/>' for r in range(48, 112, 8))
    return f'''<g>
      <rect x="{cx - 140}" y="{cy - 140}" width="280" height="280" rx="14" fill="#c9ccd2" stroke="#111" stroke-width="3"/>
      <circle cx="{cx}" cy="{cy}" r="124" fill="#2a2a2a" stroke="#111" stroke-width="2"/>
      <g>{spin}
        <circle cx="{cx}" cy="{cy}" r="115" fill="#111"/>{grooves}
        <path d="M{cx} {cy - 115}A115 115 0 0 1 {cx + 81} {cy - 81}" stroke="#4a4a4a" stroke-width="4" fill="none"/>
        <circle cx="{cx}" cy="{cy}" r="40" fill="{colour}" stroke="#111" stroke-width="1.5"/>
        <text x="{cx}" y="{cy - 4}" font-family="{FONT}" font-size="13" fill="#111" text-anchor="middle">THINK</text>
        <text x="{cx}" y="{cy + 10}" font-family="Arial, sans-serif" font-size="7" font-weight="bold" fill="#111" text-anchor="middle">LYN COLLINS</text>
        <path d="M{cx + 30} {cy - 30}L{cx + 40} {cy - 38}" stroke="#f4f4f4" stroke-width="3"/>
        <path class="crayon-mark" d="M{cx} {cy - 46}L{cx} {cy - 112}" stroke="#ffd23f" stroke-width="5" stroke-linecap="round"/>
      </g>
      <circle cx="{cx}" cy="{cy}" r="4" fill="#e8e8e8" stroke="#111"/>
      <path d="M{cx + 118} {cy - 110}L{cx + 108} {cy + 10}L{cx + 70} {cy + 60}" stroke="#e8e8e8" stroke-width="6" fill="none" stroke-linejoin="round"/>
    </g>'''


def practice_screen():
    """Needle practices, behind the decks (seen from above): two copies of "Think About It". The
    break plays on one deck (its bar runs down); SPIN BACK the other deck right before it runs
    out, and the break goes on from there. Three clean loops in a row and he's ready. The page
    judges the timing: SPIN BACK is loop_hit only in the last PRACTICE_WINDOWS[streak] seconds, loop_miss
    before; if the break runs out, the picture says so itself (loop_miss)."""
    decks = ""
    for deck, (cx, bar_x) in ((1, (190, 60)), (2, (610, 480))):
        other = 2 if deck == 1 else 1
        cxo = 610 if deck == 1 else 190
        decks += f'''
  <g data-overlay="deck-{deck}" style="display:none">
    {_deck(cx, 204, True, THINK_COLOUR)}
    {_deck(cxo, 204, False, THINK_COLOUR)}
    <text x="{cx}" y="58" font-family="{FONT}" font-size="14" fill="#7ed957" text-anchor="middle" letter-spacing="2">▶ PLAYING: THE BREAK</text>
    <text x="{cxo}" y="58" font-family="{FONT}" font-size="14" fill="#ffd23f" text-anchor="middle" letter-spacing="2">DECK {other}: CUED UP</text>
    <!-- how much of the break is left on the playing deck -->
    <rect x="{bar_x}" y="350" width="260" height="20" rx="6" fill="#111" stroke="#f4f4f4" stroke-width="2"/>
    {"".join(f'<rect data-overlay="streak-{n}" style="display:none" x="{bar_x + 260 * (1 - w / PRACTICE_BREAK):.1f}" y="350" width="{260 * w / PRACTICE_BREAK:.1f}" height="20" rx="4" fill="#7ed957" opacity="0.45"/>' for n, w in enumerate(PRACTICE_WINDOWS))}
    <rect x="{bar_x}" y="352" width="0" height="16" rx="5" fill="#ff4f79">
      <animate attributeName="width" from="0" to="260" dur="{PRACTICE_BREAK}s" fill="freeze"/></rect>
    <text x="{bar_x + 130}" y="392" font-family="{FONT}" font-size="12" fill="#f4f4f4" text-anchor="middle" letter-spacing="1">THE BREAK RUNS OUT →</text>
    <!-- the crossfader on this deck's side -->
    <rect x="{340 if deck == 1 else 420}" y="300" width="40" height="22" rx="4" fill="#e8e8e8" stroke="#111" stroke-width="2"/>
  </g>'''
    loops = len(PRACTICE_WINDOWS)
    dots = "".join(f'<g data-overlay="streak-{n}" style="display:none">'
                   + "".join(f'<circle cx="{400 - 11 * (loops - 1) + 22 * k}" cy="110" r="8" fill="{"#7ed957" if k < n else "#2a2a2a"}" stroke="#f4f4f4" stroke-width="2"/>' for k in range(loops))
                   + '</g>' for n in range(loops + 1))
    button = lambda action, glow: (
        f'<g data-defer="1" data-action="{action}" role="button" tabindex="0" aria-label="Spin back the other deck"><title>Spin back</title>'
        f'<rect x="300" y="384" width="200" height="54" rx="12" fill="{"#2e8b57" if glow else "#111"}" stroke="{"#7ed957" if glow else "#ff8a3d"}" stroke-width="4"/>'
        f'{piece(400, 422, "SPIN BACK ⟲", "gPinkYellow", size=26, rot=-2, anchor="middle", fit=180)}</g>')
    spin_backs = "".join(
        f'<g data-overlay="streak-{n}" style="display:none"><g id="spin-back-{n}">'
        f'<g><set attributeName="visibility" to="hidden" begin="{PRACTICE_BREAK - w:.2f}s"/>{button("loop_miss", False)}</g>'
        f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="{PRACTICE_BREAK - w:.2f}s"/>'
        f'<set attributeName="visibility" to="hidden" begin="{PRACTICE_BREAK:.2f}s"/>{button("loop_hit", True)}</g>'
        f'</g></g><!-- end spin-back-{n} -->' for n, w in enumerate(PRACTICE_WINDOWS))
    body = defs(DUSK) + f'''
  <!-- the DJ table from above: two decks, the mixer between them -->
  <rect width="800" height="450" fill="#3a2414"/>
  <path d="M0 60H800M0 150H800M0 240H800M0 330H800M0 420H800" stroke="#2c1a0e" stroke-width="3"/>
  <rect x="334" y="60" width="132" height="280" rx="10" fill="#2a2a2a" stroke="#111" stroke-width="3"/>
  <path d="M352 150V250M380 150V250M420 150V250M448 150V250" stroke="#555" stroke-width="5"/>
  <rect x="340" y="310" width="120" height="6" rx="3" fill="#555"/>
  {decks}
  <!-- the title, the loops so far -->
  <rect x="250" y="4" width="300" height="34" rx="8" fill="#111" opacity="0.9"/>
  <text x="400" y="28" font-family="{FONT}" font-size="18" fill="#ffd23f" text-anchor="middle" letter-spacing="2">KEEP THE BREAK GOING</text>
  <text x="400" y="86" font-family="{FONT}" font-size="11" fill="#f4f4f4" text-anchor="middle">LOOPS IN A ROW</text>
  {dots}
  {"".join(f'<text x="400" y="{138 + 13 * k}" font-family="Arial, sans-serif" font-size="9.5" fill="#f4f4f4" text-anchor="middle">{line}</text>'
           for k, line in enumerate(("SPIN BACK when", "the bar is green.", f"{len(PRACTICE_WINDOWS)} clean in a row,", "each one harder!")))}
  <g data-overlay="clean" style="display:none"><text x="400" y="290" font-family="{FONT}" font-size="30" fill="#7ed957" stroke="#111" stroke-width="1.2" text-anchor="middle" opacity="1">CLEAN!
    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.6;1" dur="1.2s" fill="freeze"/></text></g>
  <g data-overlay="break-died" style="display:none"><text x="400" y="290" font-family="{FONT}" font-size="24" fill="#ff4f79" stroke="#111" stroke-width="1.2" text-anchor="middle">THE BREAK DIED!
    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.7;1" dur="1.6s" fill="freeze"/></text></g>
  <!-- what he pressed shows at once; the decks switch when the loop starts over -->
  <g class="press-hit" style="display:none"><text x="400" y="290" font-family="{FONT}" font-size="22" fill="#7ed957" stroke="#111" stroke-width="1" text-anchor="middle">SPUN BACK ✓</text></g>
  <g class="press-miss" style="display:none"><text x="400" y="290" font-family="{FONT}" font-size="22" fill="#ff4f79" stroke="#111" stroke-width="1" text-anchor="middle">TOO EARLY ✗</text></g>
  <!-- SPIN BACK: too early until the bar reaches the green, right in the green (it counts on the
       loop's restart); the green gets smaller with every clean switch (one set per streak) -->
  {spin_backs}
  <!-- STOP: back to the basement, not practiced -->
  <g data-action="stop_practice" role="button" tabindex="0" aria-label="Stop practicing"><title>Stop</title>
    <rect x="8" y="400" width="110" height="40" rx="9" fill="#111" stroke="#7ef0ff" stroke-width="3"/>
    {piece(63, 429, "◀ STOP", "gBlueGreen", size=20, rot=-2, anchor="middle", fit=90)}
  </g>
'''
    # one round is one loop of the drum break, and the picture follows the music's clock (data-sync)
    return _svg(body, "practice-screen", end=f"{PRACTICE_BREAK:.3f}", auto=("loop_miss", PRACTICE_BREAK),
                attrs=f' data-sync="audio" data-loop="{PRACTICE_BREAK:.3f}"')


def _comic_poster(x, y, w, h, title, issue, bg, hero, rot):
    """A made-up 70s comic cover on the wall: title bar, halftone background, a hero and a POW burst."""
    dots = "".join(f'<circle cx="{x + 6 + i * 8}" cy="{y + 30 + j * 8}" r="1.6" fill="#111" opacity="0.18"/>'
                   for i in range(int((w - 8) / 8)) for j in range(int((h - 36) / 8)))
    burst = " ".join(f"{x + w - 22 + (14 if k % 2 == 0 else 7) * math.cos(k * math.pi / 8):.1f},"
                     f"{y + h - 24 + (14 if k % 2 == 0 else 7) * math.sin(k * math.pi / 8):.1f}" for k in range(16))
    return (f'<g class="comic-poster" transform="rotate({rot} {x + w / 2} {y + h / 2})">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" stroke="#111" stroke-width="2.5"/>{dots}'
            f'<rect x="{x}" y="{y}" width="{w}" height="22" fill="#111"/>'
            f'<text x="{x + w / 2}" y="{y + 16}" font-family="{FONT}" font-size="{min(13, (w - 8) / (len(title) * 0.55)):.1f}" fill="#ffd23f" text-anchor="middle">{title}</text>'
            f'<text x="{x + 5}" y="{y + 34}" font-family="{FONT}" font-size="8" fill="#111">{issue}</text>'
            f'{hero}'
            f'<polygon points="{burst}" fill="#ffd23f" stroke="#111" stroke-width="1.5"/>'
            f'<text x="{x + w - 22}" y="{y + h - 21}" font-family="{FONT}" font-size="8" fill="#d02b2b" text-anchor="middle">POW!</text>'
            '</g>')


def _comic_posters():
    """Three made-up comic covers on the basement walls (no real comics)."""
    breaker = ('<circle cx="62" cy="150" r="9" fill="#4a2e1c" stroke="#111"/>'
               '<path d="M54 148H70" stroke="#d02b2b" stroke-width="4"/>'
               '<path d="M62 158L62 182M62 166L44 154M62 166L82 176M62 182L48 196M62 182L80 192" stroke="#3fa9f5" stroke-width="5" stroke-linecap="round"/>'
               '<path d="M58 160L40 186L36 196" stroke="#d02b2b" stroke-width="3" fill="none"/>')
    sprayer = ('<circle cx="246" cy="74" r="8" fill="#7a4a2e" stroke="#111"/>'
               '<path d="M246 82V102M246 88L262 76M246 88L232 98M246 102L238 116M246 102L254 116" stroke="#7ed957" stroke-width="5" stroke-linecap="round"/>'
               '<rect x="261" y="66" width="6" height="11" rx="1.5" fill="#ff4f79" stroke="#111"/>'
               '<circle cx="270" cy="64" r="4" fill="#ff4f79" opacity="0.6"/><circle cx="274" cy="60" r="2.5" fill="#ff4f79" opacity="0.5"/>')
    party = ('<rect x="306" y="82" width="22" height="14" rx="2" fill="#2a2a2a" stroke="#111"/>'
             '<circle cx="312" cy="89" r="3.5" fill="#777"/><circle cx="321" cy="89" r="3.5" fill="#777"/>'
             '<path d="M332 88l4 -7l3 8l5 -5" stroke="#d02b2b" stroke-width="2" fill="none"/>'
             f'<text x="326" y="108" font-family="{FONT}" font-size="7" fill="#111" text-anchor="middle">DJs · MCs · B-BOYS</text>')
    return ('<g id="comic-posters">'
            # (the heroes a little lower and to the right, so they don't cover the issue number)
            + _comic_poster(22, 112, 82, 92, "B-BOY BLASTER", "No. 1 · 12¢", "#ff8a3d", f'<g transform="translate(8 7)">{breaker}</g>', -4)
            + _comic_poster(212, 42, 70, 84, "SPRAY CAN KID", "No. 7 · 15¢", "#7ef0ff", f'<g transform="translate(6 7)">{sprayer}</g>', 3)
            + _comic_poster(298, 42, 84, 74, "BLOCK PARTY", "TONIGHT IN THE PARK", "#f4e7c3", party, -2)
            + '</g>\n  <!-- end comic-posters -->')


def turntable_screen(record):
    """The turntable seen from above, playing one of the classics: the record and its label spin,
    the tonearm sits in the groove, and a NOW PLAYING panel says what it is."""
    info = RECORDS[record]
    colour = dict((s[0], s[2]) for s in BASEMENT_SLEEVES).get(record, THINK_COLOUR)
    title, artist = info["title"].upper(), info["artist"].upper()
    cx, cy = 250, 225
    grooves = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2a2a2a" stroke-width="1.2"/>'
                      for r in range(62, 148, 7))
    words = _wrap(title, 12)
    label_text = "".join(f'<text x="{cx}" y="{cy - 12 - 12 * (len(words) - 1) + 12 * k}" font-family="{FONT}" font-size="11" '
                         f'fill="#111" text-anchor="middle">{w}</text>' for k, w in enumerate(words))
    strobe = "".join(f'<rect x="{cx - 2 + 162 * math.cos(a):.1f}" y="{cy - 2 + 162 * math.sin(a):.1f}" width="4" height="4" fill="#c9ccd2"/>'
                     for a in (k * math.pi / 30 for k in range(60)))
    song = SONGS[info["song"]]["title"].upper() if info["song"] else "COMING SOON"
    body = defs(DUSK) + f'''
  <!-- the DJ table, from above -->
  <rect width="800" height="450" fill="#3a2414"/>
  <path d="M0 40H800M0 130H800M0 220H800M0 310H800M0 400H800" stroke="#2c1a0e" stroke-width="3"/>
  <g id="turntable-top">
    <rect x="40" y="22" width="420" height="406" rx="14" fill="#c9ccd2" stroke="#111" stroke-width="3"/>
    <rect x="48" y="30" width="404" height="390" rx="10" fill="none" stroke="#e8e8e8" stroke-width="2"/>
    <circle cx="{cx}" cy="{cy}" r="172" fill="#2a2a2a" stroke="#111" stroke-width="2"/>
    <g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="7.2s" repeatCount="indefinite"/>{strobe}</g>
    <g id="record-{record}">
      <title>{title} – {artist} ({info["year"]})</title>
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="1.8s" repeatCount="indefinite"/>
      <circle cx="{cx}" cy="{cy}" r="150" fill="#111"/>
      {grooves}
      <path d="M{cx} {cy - 150}A150 150 0 0 1 {cx + 106} {cy - 106}" stroke="#4a4a4a" stroke-width="5" fill="none"/>
      <circle cx="{cx}" cy="{cy}" r="52" fill="{colour}" stroke="#111" stroke-width="1.5"/>
      {label_text}
      <text x="{cx}" y="{cy + 22}" font-family="Arial, sans-serif" font-size="7" font-weight="bold" fill="#111" text-anchor="middle">{artist}</text>
      <text x="{cx}" y="{cy + 34}" font-family="Arial, sans-serif" font-size="7" fill="#111" text-anchor="middle">{info["year"]}</text>
    </g>
    <circle cx="{cx}" cy="{cy}" r="4" fill="#e8e8e8" stroke="#111"/>
    <path d="M{cx - 140} {cy - 60}A150 150 0 0 1 {cx - 60} {cy - 140}" stroke="#f4f4f4" stroke-width="6" fill="none" opacity="0.12"/>
    <!-- the tonearm, its needle in the groove -->
    <g id="tonearm">
      <circle cx="412" cy="72" r="22" fill="#8d9097" stroke="#111" stroke-width="2"/>
      <circle cx="412" cy="72" r="9" fill="#2a2a2a"/>
      <rect x="402" y="30" width="20" height="18" rx="4" fill="#2a2a2a"/>
      <path d="M412 72L404 230L366 300" stroke="#e8e8e8" stroke-width="7" fill="none" stroke-linejoin="round"/>
      <path d="M412 72L404 230L366 300" stroke="#8d9097" stroke-width="2" fill="none"/>
      <rect x="350" y="296" width="22" height="30" rx="3" fill="#2a2a2a" transform="rotate(32 361 311)"/>
    </g>
    <g data-action="toggle_play" role="button" tabindex="0" aria-label="Start or stop the record">
      <title>Start / stop</title>
      <circle cx="80" cy="390" r="20" fill="#8d9097" stroke="#111" stroke-width="2"/>
      <circle cx="80" cy="390" r="15" fill="#c9ccd2" stroke="#555" stroke-width="1.5"/>
      <text x="80" y="388" font-family="{FONT}" font-size="8" fill="#111" text-anchor="middle">START</text>
      <text x="80" y="398" font-family="{FONT}" font-size="7" fill="#111" text-anchor="middle">STOP</text>
    </g>
    <rect x="112" y="380" width="30" height="16" rx="3" fill="#ff4f79" stroke="#111"/><text x="127" y="392" font-family="{FONT}" font-size="9" fill="#111" text-anchor="middle">33</text>
    <rect x="148" y="380" width="30" height="16" rx="3" fill="#8d9097" stroke="#111"/><text x="163" y="392" font-family="{FONT}" font-size="9" fill="#111" text-anchor="middle">45</text>
    <rect x="432" y="250" width="12" height="150" rx="3" fill="#2a2a2a"/><rect x="428" y="316" width="20" height="10" rx="2" fill="#e8e8e8" stroke="#111"/>
    <circle cx="430" cy="400" r="5" fill="#ff4f79"><animate attributeName="opacity" values="1;0.4;1" dur="1s" repeatCount="indefinite"/></circle>
  </g>
  <!-- what is playing -->
  <rect x="482" y="36" width="304" height="300" rx="12" fill="#111" stroke="{colour}" stroke-width="3" opacity="0.94"/>
  {piece(634, 84, "NOW PLAYING", "gPinkYellow", size=34, rot=-2, anchor="middle", fit=270)}
  {"".join(f'<text x="634" y="{134 + 30 * k}" font-family="{FONT}" font-size="24" fill="{colour}" text-anchor="middle">{line}</text>' for k, line in enumerate(_wrap(title, 18)))}
  <text x="634" y="{164 + 30 * (len(_wrap(title, 18)) - 1)}" font-family="{FONT}" font-size="15" fill="#f4f4f4" text-anchor="middle" letter-spacing="1">{artist}</text>
  <text x="634" y="{190 + 30 * (len(_wrap(title, 18)) - 1)}" font-family="{FONT}" font-size="15" fill="#9a9aa2" text-anchor="middle" letter-spacing="2">{info["year"]}</text>
  <text x="634" y="300" font-family="{FONT}" font-size="14" fill="#ffd23f" text-anchor="middle" letter-spacing="1">♪ SONG: {song}</text>
  <g data-overlay="paused" style="display:none">
    <rect x="554" y="226" width="160" height="40" rx="8" fill="#2a2a2a" stroke="#f4f4f4" stroke-width="2"/>
    <text x="634" y="253" font-family="{FONT}" font-size="20" fill="#f4f4f4" text-anchor="middle" letter-spacing="3">❚❚ PAUSED</text>
  </g>
  {"".join(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="22" fill="#ffd23f" opacity="0">{n}<animate attributeName="opacity" values="0;1;0" dur="1.6s" begin="{b}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 0;{dx} -40" dur="1.6s" begin="{b}s" repeatCount="indefinite"/></text>' for x, y, n, dx, b in ((520, 250, "♪", 10, 0), (740, 260, "♫", -12, 0.8)))}
  <!-- back to the basement -->
  <g data-action="back" role="button" tabindex="0" aria-label="Back to the basement">
    <title>Back to the basement</title>
    <rect x="534" y="372" width="200" height="44" rx="9" fill="#111" stroke="#7ef0ff" stroke-width="3"/>
    {piece(634, 403, "◀ BACK", "gBlueGreen", size=26, rot=-2, anchor="middle", fit=170)}
  </g>
'''
    return _svg(body, f"turntable-{record}")


GF_WIDTH = text_width("GOODFELLAS", 40)  # the crew's piece in the basement


def _tag_fit(x, y, name, colour, size, rot, width):
    """A tag that fits into width px (the handstyle font, measured)."""
    return tag(x, y, name, colour, round(min(size, size * width / text_width(name, size, "tag")), 1), rot)


def _way_out(action, label, x, grad, edge):
    """A graffiti button in the picture that leads to another scene."""
    return (f'<g data-action="{action}" role="button" tabindex="0" aria-label="{label.strip("◀▶ ").title()}">'
            f'<title>{label.strip("◀▶ ").title()}</title>'
            f'<rect x="{x}" y="406" width="188" height="40" rx="9" fill="#111" stroke="{edge}" stroke-width="3" opacity="0.92"/>'
            f'{piece(x + 94, 435, label, grad, size=24, rot=-2, anchor="middle", fit=166)}</g>')


def _sign_button(action, label, x, edge, grad, aria):
    return (f'<g data-action="{action}" role="button" tabindex="0" aria-label="{aria}"><title>{aria}</title>'
            f'<rect x="{x}" y="292" width="140" height="42" rx="9" fill="#111" stroke="{edge}" stroke-width="3"/>'
            f'{piece(x + 70, 322, label, grad, size=24, rot=-2, anchor="middle", fit=110)}</g>')


def _inspect_sign(thing, info):
    """The sign that opens when the player clicks a thing: what it is, its song slot (if it has
    one) and what can be done with it: TAKE IT, READ IT, and CLOSE (LEAVE IT when it could be taken)."""
    rows = _wrap(info["text"], 46)
    text = "".join(f'<text x="400" y="{214 + 20 * k}" font-family="{FONT}" font-size="16" fill="#f4f4f4" '
                   f'text-anchor="middle">{row}</text>' for k, row in enumerate(rows))
    name = info["name"].replace(chr(34), "&quot;")
    song_y = 222 + 20 * len(rows)
    song_line = ""
    if "song" in info:
        song = SONGS[info["song"]]["title"].upper() if info["song"] else "COMING SOON"
        play = ("" if not info["song"] else
                f'<g data-action="play:{info["song"]}" role="button" tabindex="0" aria-label="Play the song"><title>Play</title>'
                f'<rect x="524" y="{song_y - 19}" width="92" height="26" rx="7" fill="#111" stroke="#ffd23f" stroke-width="2"/>'
                f'<text x="570" y="{song_y}" font-family="{FONT}" font-size="14" fill="#ffd23f" text-anchor="middle" letter-spacing="1">▶ PLAY</text></g>')
        song_line = (f'<text x="{370 if info["song"] else 400}" y="{song_y}" font-family="{FONT}" font-size="15" fill="#ffd23f" '
                     f'text-anchor="middle" letter-spacing="1">♪ SONG: {song}</text>{play}')
    buttons = []
    if info.get("take"):
        buttons.append((info["take"], "TAKE IT", "#7ed957", "gGold", "Take it"))
    if info.get("read"):
        buttons.append((f"read:{thing}", "READ IT", "#c58bff", "gPurple", "Read it"))
    for shot, label in info.get("shots", {}).items():  # e.g. the basketball: DUNK or 3-POINTER
        buttons.append((f"shoot:{shot}", label, "#ff8a3d", "gOrangeRed", label.title()))
    if info.get("join"):  # e.g. the cypher
        buttons.append((f"join:{thing}", "JOIN IN", "#c58bff", "gPurple", "Join in"))
    leave = info.get("take") or info.get("shots") or info.get("join")
    buttons.append(("close", "LEAVE IT" if leave else "CLOSE", "#ffd23f", "gBlueGreen",
                    "Leave it here" if leave else "Close"))
    left = 400 - (len(buttons) * 140 + (len(buttons) - 1) * 10) / 2
    row = "".join(_sign_button(a, label, left + k * 150, edge, grad, aria)
                  for k, (a, label, edge, grad, aria) in enumerate(buttons))
    return (f'<g data-overlay="inspect-{thing}" style="display:none">'
            '<rect width="800" height="450" fill="#0b0716" opacity="0.7"/>'
            '<rect x="140" y="118" width="520" height="230" rx="14" fill="url(#bricks)" stroke="#111" stroke-width="6"/>'
            '<rect x="140" y="118" width="520" height="230" rx="14" fill="#1f1238" opacity="0.35"/>'
            f'{piece(400, 176, name, "gPinkYellow", size=34, rot=-2, anchor="middle", fit=470)}'
            f'{text}{song_line}{row}'
            '</g>\n  <!-- end sign -->')


def _message_sign(overlay, title, text, edge, grad, end="", icon=""):
    """A banner over the top of a scene: what just happened, or why it didn't work."""
    rows = _wrap(text.upper().replace(chr(34), "&quot;"), 52)
    lines = "".join(f'<text x="400" y="{138 + 18 * k}" font-family="{FONT}" font-size="14" fill="#f4f4f4" '
                    f'text-anchor="middle" letter-spacing="1">{row}</text>' for k, row in enumerate(rows))
    full = text.upper().replace(chr(34), "&quot;")
    return (f'<g data-overlay="{overlay}" style="display:none"><title>{full}</title>'
            f'<rect x="150" y="70" width="500" height="{80 + 18 * len(rows)}" rx="12" fill="#111" stroke="{edge}" stroke-width="3" opacity="0.95"/>'
            f'{icon}{piece(400, 116, title, grad, size=32, rot=-2, anchor="middle", fit=440)}{lines}</g>'
            + (f"\n  <!-- {end} -->" if end else ""))


def hq_scene():
    """The Basement (hq): the GoodFellas' hip-hop HQ after the break-in. A proper sound system,
    the crew's tags in the graffiti corner, classic breaks all over the floor and a little
    checkerboard dance floor where Reekz breaks (headspin, 1990). The empty sleeve of Needle's
    secret joint lies at the crate, the Sopranos went over the GoodFellas piece on the wall.
    The rhyme book and the empty sleeve can be clicked; the conversation goes on with each click;
    the ways out are graffiti buttons in the picture."""
    extra, room = _basement_room()
    return _svg(defs(DUSK, extra=extra) + room, "scene-hq")


def _basement_room(still=False, later=False):
    """The basement and the crew in it: (its defs, its picture). still: the room as a new game
    finds it, as a plain picture (nothing to click, nothing for the page to show or hide, and
    without Portals): what he drops into at the end of the escape. later (with still): the room
    after the rap battle: Bible has his rhyme book, the record is back."""
    extra = '''    <pattern id="cinder" width="50" height="25" patternUnits="userSpaceOnUse">
      <rect width="50" height="25" fill="#4a4450"/>
      <path d="M0 0H50M0 12.5H50M25 0V12.5M0 12.5V25M50 12.5V25" stroke="#3a3540" stroke-width="2"/>
    </pattern>
    <clipPath id="basementWindow"><rect x="44" y="48" width="152" height="54"/></clipPath>
    <radialGradient id="bulbGlow" cx="0.5" cy="0" r="1">
      <stop offset="0" stop-color="#ffe9a8" stop-opacity="0.4"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/>
    </radialGradient>

'''
    legs = "".join(
        f'<g><animateTransform attributeName="transform" type="translate" values="-60 0;260 0" dur="5s" begin="{b}s" repeatCount="indefinite"/>'
        f'<rect x="0" y="62" width="9" height="40" fill="{c}"/><rect x="14" y="66" width="9" height="36" fill="{c}"/>'
        f'<rect x="-2" y="98" width="14" height="5" fill="#111"/><rect x="12" y="98" width="14" height="5" fill="#111"/></g>'
        for b, c in ((0, "#2d4f8a"), (2.6, "#7a2e1f")))
    notes = "".join(
        f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="20" fill="#ffd23f" opacity="0">{n}'
        f'<animate attributeName="opacity" values="0;1;0" dur="2s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} -40" dur="2s" begin="{b}s" repeatCount="indefinite"/></text>'
        for x, y, n, dx, b in ((150, 190, "♪", 14, 0), (152, 280, "♫", 18, 0.7), (12, 230, "♪", -6, 1.3)))
    cans = "".join(f'<rect x="{x}" y="{y}" width="11" height="22" rx="2" fill="{c}" stroke="#111" stroke-width="1"/>'
                   f'<rect x="{x + 3}" y="{y - 4}" width="5" height="4" fill="#222"/>'
                   for x, y, c in ((742, 354, "#ff4f79"), (755, 354, "#3fa9f5"), (768, 354, "#7ed957"),
                                   (748, 332, "#ffd23f"), (761, 332, "#ff8a3d"), (755, 310, "#f4f4f4")))
    splats = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * 0.35:.1f}" fill="{c}" opacity="0.85"/>'
                     for x, y, rx, c in ((690, 392, 14, "#ff4f79"), (722, 412, 10, "#3fa9f5"), (770, 384, 12, "#7ed957"),
                                         (668, 418, 8, "#ffd23f"), (790, 430, 9, "#ff8a3d")))
    sleeves = "".join(_sleeve(*s, still=still) for s in BASEMENT_SLEEVES)
    discs = "".join(_disc(*d) for d in BASEMENT_DISCS)
    boombox = f'''<g transform="translate(604 362)">
    <path d="M6 0V-8H50V0" stroke="#222" stroke-width="4" fill="none"/>
    <rect x="0" y="0" width="56" height="30" rx="4" fill="#c9ccd2" stroke="#111" stroke-width="2.5"/>
    <circle cx="13" cy="15" r="9" fill="#222"/><circle cx="43" cy="15" r="9" fill="#222"/>
    <rect x="24" y="5" width="8" height="9" fill="#3a3a3a"/>
    <text x="40" y="-12" font-family="Arial, sans-serif" font-size="16" fill="#f4f4f4" opacity="0">♫
      <animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="translate" values="0 0;8 -20" dur="1s" repeatCount="indefinite"/></text>
  </g>'''
    def clickable(attrs):
        return "" if still else " " + attrs

    body = f'''
  <!-- basement walls -->
  <rect width="800" height="340" fill="url(#cinder)"/>
  <rect width="800" height="340" fill="#0b0716" opacity="0.25"/>

  <!-- the graffiti corner: the right-hand wall, where every crew member has left their tag -->
  <g id="graffiti-corner">
    <rect x="655" y="0" width="145" height="340" fill="#5a5262" opacity="0.7"/>
    <path d="M655 0V340" stroke="#1a171d" stroke-width="5"/>
    {_tag_fit(664, 80, "Needle", "#ff4f4f", 30, -8, 124)}
    {_tag_fit(672, 118, "Bible 1", "#7ed957", 28, 5, 116)}
    {_tag_fit(662, 156, "Meyhem", "#c58bff", 28, -6, 126)}
    {_tag_fit(670, 194, "Reekz", "#f4f4f4", 30, 4, 118)}
    {_tag_fit(664, 232, "Portals 77", "#3fa9f5", 26, -4, 126)}
    {star(676, 40, 9, "#ffd23f")}{star(668, 280, 6, "#ff4f79")}
    <path d="M760 112V126M690 144V156M772 194V206" stroke="#f4f4f4" stroke-width="2.5"/>
    {cans}
  </g>
  <!-- end graffiti-corner -->

  <!-- pipe along the ceiling, dripping -->
  <rect x="0" y="22" width="800" height="12" fill="#6d7078"/>
  <rect x="300" y="18" width="16" height="20" fill="#55585f"/><rect x="620" y="18" width="16" height="20" fill="#55585f"/>
  <circle cx="540" cy="38" r="3.5" fill="#9fd3ff">
    <animate attributeName="cy" values="38;38;338" keyTimes="0;0.55;1" dur="2.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.97;1" dur="2.4s" repeatCount="indefinite"/>
  </circle>

  <!-- the basement window at street level: feet walk past -->
  <rect x="40" y="44" width="160" height="62" fill="#111" stroke="#2a2a2a" stroke-width="4"/>
  <rect x="44" y="48" width="152" height="54" fill="#f08a4b" opacity="0.5"/>
  <g clip-path="url(#basementWindow)">
    <rect x="44" y="96" width="152" height="6" fill="#9a9aa2"/>
    {legs}
  </g>
  <path d="M82 46V104M120 46V104M158 46V104" stroke="#2a2a2a" stroke-width="4"/>

  <!-- comic posters on the wall -->
  {_comic_posters()}

  <!-- the crew's piece and the battle flyer -->
  {piece(262, 160, "GOODFELLAS", "gPinkYellow", size=40, rot=-3, fit=236)}
  {tag(262, 182, "est. 1975", "#7ef0ff", 13, -3)}
  <!-- the Sopranos went over it: an X across the name and their own piece on top,
       GOODFELLAS still readable underneath -->
  <g id="sopranos-crossout">
    <path class="slash" d="M258 120Q{262 + GF_WIDTH / 2:.0f} 142 {262 + GF_WIDTH + 4:.0f} 168" stroke="#111" stroke-width="5" stroke-linecap="round" fill="none" opacity="0.85"/>
    <path class="slash" d="M260 168Q{262 + GF_WIDTH / 2:.0f} 146 {262 + GF_WIDTH + 2:.0f} 118" stroke="#111" stroke-width="5" stroke-linecap="round" fill="none" opacity="0.85"/>
    <path d="M296 130V146M346 137V155M{262 + GF_WIDTH - 40:.0f} 150V164M306 162V176M{262 + GF_WIDTH - 70:.0f} 140V152" stroke="#111" stroke-width="3" opacity="0.85"/>
    {piece(330, 204, "SOPRANOS", "gSteel", size=30, rot=-5, shadow="#c0392b", fit=GF_WIDTH * 0.6)}
    <text x="{262 + GF_WIDTH - 6:.0f}" y="200" font-family="Arial, sans-serif" font-size="22" fill="#c0392b" transform="rotate(10 {262 + GF_WIDTH - 6:.0f} 200)">♛</text>
  </g>
  <!-- end sopranos-crossout -->
  <g transform="rotate(3 565 145)">
    <rect x="518" y="92" width="94" height="108" fill="#f4e7c3" stroke="#111" stroke-width="2"/>
    <text x="565" y="116" font-family="{FONT}" font-size="13" fill="#c0392b" text-anchor="middle">DISCO FEVER</text>
    <text x="565" y="141" font-family="{FONT}" font-size="20" fill="#111" text-anchor="middle">DJ BATTLE</text>
    <text x="565" y="162" font-family="{FONT}" font-size="11" fill="#111" text-anchor="middle">BOROUGH FINAL</text>
    <text x="565" y="188" font-family="{FONT}" font-size="15" fill="#3d6fb6" text-anchor="middle">SATURDAY</text>
  </g>
  <circle cx="565" cy="96" r="4" fill="#c0392b"/>

  <!-- concrete floor, a little checkerboard dance floor, paint in the graffiti corner -->
  {_floor()}
  {_dance_floor()}
  {splats}

  <!-- the swinging bulb and its light -->
  <g>
    <animateTransform attributeName="transform" type="rotate" values="-5 400 0;5 400 0;-5 400 0" dur="4s" repeatCount="indefinite"/>
    <path d="M400 0V70" stroke="#111" stroke-width="2"/>
    <polygon points="392,82 408,82 620,430 180,430" fill="url(#bulbGlow)"/>
    <rect x="394" y="66" width="12" height="8" fill="#555"/>
    <circle cx="400" cy="82" r="10" fill="#fff4c4"/>
  </g>

  <!-- classic breaks all over the floor: the Sopranos turned the place over -->
  <g id="vinyls">{discs}{sleeves}</g>
  <!-- end vinyls -->

  <!-- the sound system: two cabinets, woofers pumping to the beat -->
  <g id="soundsystem" transform="translate(10 344) scale(0.5) translate(-10 -376)">
    <rect x="22" y="140" width="116" height="20" rx="3" fill="#c9ccd2" stroke="#111" stroke-width="2"/>
    <circle cx="36" cy="150" r="4" fill="#333"/><circle cx="50" cy="150" r="4" fill="#333"/>
    {"".join(f'<rect x="{70 + k * 9}" y="146" width="6" height="10" fill="{c}"><animate attributeName="height" values="3;10;5;9;3" dur="{0.5 + k * 0.1:.1f}s" repeatCount="indefinite"/></rect>' for k, c in enumerate(("#7ed957", "#7ed957", "#ffd23f", "#ffd23f", "#ff4f79", "#ff4f79")))}
    <rect x="16" y="160" width="128" height="92" rx="4" fill="#1b1b1b" stroke="#000" stroke-width="3"/>
    {_woofer(50, 196, 22, 0.25)}{_woofer(110, 196, 22, 0.25)}
    <rect x="60" y="228" width="40" height="16" rx="3" fill="#2a2a2a" stroke="#555" stroke-width="2"/>
    <rect x="10" y="252" width="140" height="124" rx="4" fill="#1b1b1b" stroke="#000" stroke-width="3"/>
    {_woofer(80, 308, 46)}
    <text x="80" y="370" font-family="{FONT}" font-size="10" fill="#f4f4f4" text-anchor="middle" letter-spacing="2">GOODFELLAS SOUND</text>
    {notes}
  </g>
  <!-- end soundsystem -->

  <!-- the couch on the back wall, with MC Bible's rhyme book still on it -->
  <g id="couch">
    <rect x="488" y="280" width="150" height="54" rx="12" fill="#a0522d" stroke="#5a2e1a" stroke-width="3"/>
    <rect x="482" y="322" width="162" height="30" rx="8" fill="#b5653a" stroke="#5a2e1a" stroke-width="3"/>
    <rect x="474" y="302" width="22" height="52" rx="9" fill="#8b4425" stroke="#5a2e1a" stroke-width="3"/>
    <rect x="630" y="302" width="22" height="52" rx="9" fill="#8b4425" stroke="#5a2e1a" stroke-width="3"/>
    <rect x="490" y="352" width="9" height="20" fill="#3a2414"/><rect x="627" y="352" width="9" height="20" fill="#3a2414"/>
  </g>
{"" if later else f'''  {"<g>" if still else '<g data-overlay="offer-take_rhyme_book" style="display:none">'}
  <g transform="translate(88 0)"><!-- at the far end of the couch, clear of Reekz on the dance floor -->
  <g id="rhyme-book" transform="rotate(-10 517 300)"{clickable('data-action="inspect:rhyme_book" role="button" tabindex="0" aria-label="MC Bible&#39;s rhyme book"')}>
    <title>MC Bible's rhyme book</title>
    <rect x="497" y="276" width="40" height="48" rx="3" fill="#7a2e1f" stroke="#111" stroke-width="2"/>
    <rect x="497" y="276" width="6" height="48" fill="#4f1d13"/>
    <rect x="504" y="281" width="31" height="34" fill="none" stroke="#ffd23f" stroke-width="1.2"/>
    <text x="519.5" y="295" font-family="{FONT}" font-size="11" fill="#ffd23f" text-anchor="middle">RHYME</text>
    <text x="519.5" y="308" font-family="{FONT}" font-size="11" fill="#ffd23f" text-anchor="middle">BOOK</text>
  </g>
  <g><animate attributeName="opacity" values="0;1;0" dur="1.6s" repeatCount="indefinite"/>{star(549, 272, 7, "#fff4c4")}</g>
  <g><animate attributeName="opacity" values="0;1;0" dur="1.6s" begin="0.8s" repeatCount="indefinite"/>{star(493, 290, 5, "#fff4c4")}</g>
  </g></g>
'''}  <!-- end couch-book -->

  {"" if still else _needle_behind_decks()}
  <!-- the DJ table with two turntables -->
  <rect x="262" y="298" width="200" height="10" fill="#5a3e2a"/>
  <rect x="272" y="308" width="10" height="66" fill="#3a2414"/><rect x="442" y="308" width="10" height="66" fill="#3a2414"/>
  <text x="367" y="306.5" font-family="{FONT}" font-size="8" fill="#f4f4f4" text-anchor="middle" letter-spacing="1">BREAKS ▼</text>
  <g id="turntables">
    <rect x="269" y="276" width="82" height="22" rx="3" fill="#2a2a2a" stroke="#111" stroke-width="2"/>
    <ellipse cx="307" cy="276" rx="30" ry="7" fill="#111" stroke="#555" stroke-width="1.5"/>
    <circle cx="307" cy="276" r="2" fill="#888"/>
    <path d="M343 270L329 276" stroke="#c9ccd2" stroke-width="2.5"/>
    <rect x="353" y="280" width="18" height="18" fill="#3a3a3a"/>
    <circle cx="359" cy="286" r="2" fill="#ffd23f"/><circle cx="365" cy="292" r="2" fill="#ff4f79"/>
    <rect x="373" y="276" width="82" height="22" rx="3" fill="#2a2a2a" stroke="#111" stroke-width="2"/>
    <ellipse cx="411" cy="276" rx="30" ry="7" fill="#111" stroke="#555" stroke-width="1.5"/>
    <circle cx="411" cy="276" r="2" fill="#888"/>
    <path d="M447 270L433 276" stroke="#c9ccd2" stroke-width="2.5"/>
  </g>

  <!-- the empty record crate under the table -->
  <g id="empty-crate">
    <rect x="332" y="322" width="70" height="52" fill="#2e6fb0" stroke="#1d4a78" stroke-width="3"/>
    <path d="M332 340H402M332 357H402M349 322V374M367 322V374M385 322V374" stroke="#1d4a78" stroke-width="2"/>
    <rect x="337" y="326" width="60" height="10" fill="#111" opacity="0.6"/>
  </g>
  <!-- the empty sleeve of Needle's secret joint, pulled out of the crate: the record is gone -->
{"" if later else f'''  {"<g>" if still else '<g data-overlay="lacks-vinyl" style="display:none">'}
  <g id="empty-sleeve"{clickable('data-action="inspect:empty_sleeve" role="button" tabindex="0" aria-label="The empty sleeve of Think About It"')}>
    <title>LYN COLLINS – THINK ABOUT IT (empty sleeve)</title>
    <g id="missing-record">
      <animate attributeName="opacity" values="0.35;1;0.35" dur="1.6s" repeatCount="indefinite"/>
      <circle cx="368" cy="336" r="18" fill="#0b0716" fill-opacity="0.35" stroke="#fff4c4" stroke-width="2.5" stroke-dasharray="5 4"/>
      <circle cx="368" cy="336" r="6" fill="none" stroke="#fff4c4" stroke-width="1.5" stroke-dasharray="2 3"/>
      <text x="368" y="342" font-family="{FONT}" font-size="16" fill="#ffd23f" text-anchor="middle" stroke="#111" stroke-width="0.8">?</text>
      <path d="M368 356V362" stroke="#fff4c4" stroke-width="2" stroke-dasharray="2 3"/>
    </g>
    <g transform="rotate(-6 368 386)">
      <rect x="345" y="363" width="46" height="46" fill="#ff6fa8" stroke="#111" stroke-width="2"/>
      <path d="M345 375H391M345 395H391" stroke="#ffd23f" stroke-width="5"/>
      <path d="M347 364H389" stroke="#111" stroke-width="3"/>
      <text x="368" y="386" font-family="{FONT}" font-size="10" fill="#111" text-anchor="middle">THINK</text>
      <text x="368" y="396" font-family="{FONT}" font-size="7" fill="#111" text-anchor="middle">ABOUT IT</text>
      <text x="368" y="405" font-family="Arial, sans-serif" font-size="5" font-weight="bold" fill="#111" text-anchor="middle">LYN COLLINS</text>
    </g>
  </g>
  </g>
'''}  <!-- end empty-sleeve -->
  <!-- once the crew has won it back, the full sleeve is there: Needle can put it on -->
  {_sleeve("think_about_it", ["THINK", "(ABOUT IT)"], THINK_COLOUR, 368, 386, -6, still=True) if later else
   "" if still else _sleeve("think_about_it", ["THINK", "(ABOUT IT)"], THINK_COLOUR, 368, 386, -6, when="has-vinyl !practicing")}

  <!-- the crew: Needle is furious, Bible points at his book, Portals sprays his corner -->
{crew.meyhem_front(178)}
  <g id="needle-furious"{"" if still else ' data-overlay="!needle-busy"'}>
{crew.needle(236, idle="angry")}
  </g>
'''
    if still:
        body += f'''{crew.bible(454, book=later, idle="still")}
  {boombox}
{crew.reekz_breaking(548, 402)}'''
        return extra, body
    body += f'''  <!-- Needle puts on a record: one walk per classic on the floor -->
  {"".join(_pick_record(r, x, c) for r, _, c, x, _, _ in BASEMENT_SLEEVES)}{_pick_record("think_about_it", 368, THINK_COLOUR)}
  <!-- PRACTICE THE BREAK: he takes the record behind the decks -->
  {_practice_walk()}
{crew.bible_either(454)}
{crew.portals(700, None, spraying=True, idle="still")}
  {boombox}
{crew.reekz_breaking(548, 402)}
  <!-- the ways out: graffiti buttons -->
  {_way_out("go_block", "◀ HIT THE BLOCK", 8, "gBlueGreen", "#7ef0ff")}
{_dialogue(SCENES["hq"]["dialogue"], HQ_SPEAKERS)}
{_dialogue(SCENES["hq"]["dialogue_back"]["lines"], HQ_SPEAKERS, kind="back")}
  <!-- what the player sees when they click a thing -->
  {"".join(_inspect_sign(t, info) for t, info in SCENES["hq"]["things"].items())}
  {_message_sign("done-take_rhyme_book", "YOU GOT THE RHYME BOOK!", "MC Bible's rhyme book: every verse he ever wrote.", "#e0b84a", "gGold")}
  <!-- the plot twist: with the record back, Needle has to practice the break here before Disco Fever.
       First he tries and can't catch the break ... -->
  <g data-overlay="has-vinyl !stuck" style="display:none">
    <g data-action="try_practice" role="button" tabindex="0" aria-label="Practice the break"><title>Practice the break</title>
      <rect x="282" y="8" width="236" height="42" rx="9" fill="#111" stroke="#ff4f79" stroke-width="3" opacity="0.94"/>
      {piece(400, 38, "PRACTICE THE BREAK ▶", "gPinkYellow", size=22, rot=-2, anchor="middle", fit=212)}
    </g>
  </g>
  <!-- ... so Portals opens a portal to Grandmaster Flash, on the wall of his corner -->
  <g data-overlay="stuck" style="display:none">
    <g data-action="go_flash" role="button" tabindex="0" aria-label="Portals opens a portal to Grandmaster Flash"><title>Portal to Flash</title>
      <rect x="526" y="8" width="180" height="42" rx="9" fill="#111" stroke="#7ef0ff" stroke-width="3" opacity="0.94"/>
      {piece(616, 38, "◎ PORTAL TO FLASH", "gBlueGreen", size=19, rot=-2, anchor="middle", fit=160)}
    </g>
  </g>
  {_message_sign("done-try_practice", "HE CAN'T CATCH IT!", next(a["message"] for a in SCENES["hq"]["actions"] if a["id"] == "try_practice"), "#7ef0ff", "gBlueGreen")}
  {_message_sign("rejected-practice", "THE CRAYON...", CRAYON_MESSAGE, "#e0b84a", "gGold", end="end rejected")}
  <!-- ... and after Flash, with crayons, he practices for real -->
  <g data-overlay="met-flash !practiced" style="display:none">
    <g data-action="practice" role="button" tabindex="0" aria-label="Practice the break"><title>Practice the break</title>
      <rect x="282" y="8" width="236" height="42" rx="9" fill="#111" stroke="#ff4f79" stroke-width="3" opacity="0.94"/>
      {piece(400, 38, "PRACTICE THE BREAK ▶", "gPinkYellow", size=22, rot=-2, anchor="middle", fit=212)}
    </g>
  </g>
  {_message_sign("done-practice", "READY FOR THE FINAL!", next(a["message"] for a in SCENES["hq"]["actions"] if a["id"] == "practice"), "#ff4f79", "gPinkYellow")}
'''
    return extra, body


# Who says what in the record shop, and where their heads are (Rico stands behind the counter).
SHOP_SPEAKERS = {
    "rico": ("RICO", "#e8742a", (690, 182)),
    "portals": ("PORTALS", "#3d6fb6", (120, 236)),
    "bible": ("MC BIBLE", "#2e8b57", (178, 240)),
    "needle": ("FANTASTIC NEEDLE", "#d02b2b", (236, 238)),
    "meyhem": ("MC MEYHEM", "#6b3fa8", (294, 240)),
    "reekz": ("REEKZ", "#c0392b", (340, 236)),
}
SHOP_BINS = ["SOUL", "FUNK", "BREAKS", "LATIN", "DISCO"]
SHOP_SLEEVE_COLOURS = ["#e8742a", "#2e8b57", "#7d3cff", "#c0392b", "#3fa9f5", "#ffd23f", "#ff4f79",
                       "#7ed957", "#f4f4f4", "#8b4425", "#111", "#7ef0ff"]


def _key_icon(x, y, scale=1.0):
    """An old brass key."""
    return (f'<g transform="translate({x} {y}) scale({scale})">'
            '<circle cx="0" cy="0" r="7" fill="none" stroke="#e0b84a" stroke-width="3.5"/>'
            '<path d="M7 0H30M22 0V6M27 0V5" stroke="#e0b84a" stroke-width="3.5" stroke-linecap="square"/>'
            '</g>')


def record_shop_scene():
    """Inside Rico's Record Shop: walls of records, bins sorted SOUL / FUNK / BREAKS / LATIN /
    DISCO, a neon sign, a ceiling fan, and Rico behind the counter with a record spinning on the
    listening deck. The old MTA key is in his half-open drawer until the crew takes it."""
    extra = '''    <pattern id="wallpaper" width="24" height="24" patternUnits="userSpaceOnUse">
      <rect width="24" height="24" fill="#5a2f3a"/><rect width="12" height="24" fill="#62343f"/>
    </pattern>
    <pattern id="planks" width="120" height="22" patternUnits="userSpaceOnUse">
      <rect width="120" height="22" fill="#6b4a2e"/>
      <path d="M0 0H120M0 11H120M40 0V11M100 11V22" stroke="#553a22" stroke-width="2"/>
    </pattern>
    <filter id="neonGlow" x="-20%" y="-40%" width="140%" height="180%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
'''
    shelves = []
    for row, y in enumerate((84, 134, 184)):
        shelves.append(f'<rect x="118" y="{y + 40}" width="426" height="6" fill="#3a2414"/>')
        for k in range(15):
            c = SHOP_SLEEVE_COLOURS[(k * 5 + row * 3) % len(SHOP_SLEEVE_COLOURS)]
            x = 122 + k * 28
            shelves.append(f'<rect x="{x}" y="{y + 12}" width="26" height="28" fill="{c}" stroke="#111" stroke-width="1"/>')
            if (k + row) % 3 == 0:
                shelves.append(f'<circle cx="{x + 13}" cy="{y + 26}" r="8" fill="#111" opacity="0.8"/>'
                               f'<circle cx="{x + 13}" cy="{y + 26}" r="2.5" fill="#f4f4f4"/>')
            elif (k + row) % 3 == 1:
                shelves.append(f'<path d="M{x} {y + 22}H{x + 26}M{x} {y + 30}H{x + 26}" stroke="#111" stroke-width="2" opacity="0.5"/>')
    bins = []
    for k, genre in enumerate(SHOP_BINS):
        x = 410 + k * 36
        for j in range(3):
            c = SHOP_SLEEVE_COLOURS[(k * 3 + j * 4) % len(SHOP_SLEEVE_COLOURS)]
            bins.append(f'<rect x="{x + 3 + j * 9}" y="{290 + (j % 2) * 4}" width="18" height="24" fill="{c}" '
                        f'stroke="#111" stroke-width="1" transform="rotate({-8 + j * 7} {x + 12 + j * 9} 306)"/>')
        bins.append(f'<rect x="{x}" y="312" width="36" height="62" fill="#8b5a2b" stroke="#3a2414" stroke-width="2"/>'
                    f'<text x="{x + 18}" y="332" font-family="{FONT}" font-size="9" fill="#f4e7c3" text-anchor="middle">{genre}</text>')
    notes = "".join(
        f'<text x="{x}" y="244" font-family="Arial, sans-serif" font-size="16" fill="#ffd23f" opacity="0">{n}'
        f'<animate attributeName="opacity" values="0;1;0" dur="1.6s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} -34" dur="1.6s" begin="{b}s" repeatCount="indefinite"/></text>'
        for x, n, dx, b in ((640, "♪", 8, 0), (656, "♫", 14, 0.8)))
    body = defs(DUSK, extra=extra) + f'''
  <!-- walls, floor -->
  <rect width="800" height="340" fill="url(#wallpaper)"/>
  <rect width="800" height="340" fill="#0b0716" opacity="0.2"/>
  <rect y="340" width="800" height="110" fill="url(#planks)"/>
  <rect y="340" width="800" height="16" fill="#0b0716" opacity="0.3"/>

  <!-- the front door: the street outside -->
  <rect x="8" y="88" width="94" height="252" fill="#3a2414" stroke="#111" stroke-width="3"/>
  <rect x="18" y="98" width="74" height="120" fill="#f08a4b" opacity="0.75"/>
  <rect x="18" y="186" width="74" height="32" fill="#9a9aa2" opacity="0.8"/>
  <path d="M55 98V218" stroke="#3a2414" stroke-width="4"/>
  <rect x="28" y="232" width="54" height="22" rx="4" fill="#111"/>
  <text x="55" y="248" font-family="{FONT}" font-size="13" fill="#7ed957" text-anchor="middle" filter="url(#neonGlow)">OPEN</text>
  <circle cx="88" cy="280" r="4" fill="#e0b84a"/>

  <!-- the neon sign -->
  <g id="neon-sign" filter="url(#neonGlow)">
    <animate attributeName="opacity" values="1;1;0.55;1;1;0.75;1" keyTimes="0;0.6;0.62;0.64;0.9;0.92;1" dur="5s" repeatCount="indefinite"/>
    <text x="330" y="58" font-family="{TAG_FONT}" font-size="40" fill="none" stroke="#ff6fa8" stroke-width="2.5" text-anchor="middle">Rico's Records</text>
    <text x="330" y="76" font-family="{FONT}" font-size="11" fill="#7ef0ff" text-anchor="middle" letter-spacing="4">SOUTH BRONX · SINCE 1969</text>
  </g>

  <!-- the ceiling fan -->
  <g transform="translate(640 26)">
    <path d="M0 -26V-8" stroke="#2a2a2a" stroke-width="3"/>
    <g><animateTransform attributeName="transform" type="scale" values="1 1;-1 1;1 1" dur="0.7s" repeatCount="indefinite"/>
      <ellipse cx="-38" cy="0" rx="38" ry="5" fill="#5a3e2a"/><ellipse cx="38" cy="0" rx="22" ry="4" fill="#4a3220"/></g>
    <circle r="7" fill="#c9ccd2"/>
  </g>

  <!-- the wall of records -->
  <g id="record-wall">{"".join(shelves)}</g>

  <!-- the battle flyer, on the wall behind the counter -->
  <g transform="rotate(-4 600 140)">
    <rect x="560" y="92" width="80" height="94" fill="#f4e7c3" stroke="#111" stroke-width="2"/>
    <text x="600" y="113" font-family="{FONT}" font-size="11" fill="#c0392b" text-anchor="middle">DISCO FEVER</text>
    <text x="600" y="136" font-family="{FONT}" font-size="17" fill="#111" text-anchor="middle">DJ BATTLE</text>
    <text x="600" y="156" font-family="{FONT}" font-size="9" fill="#111" text-anchor="middle">BOROUGH FINAL</text>
    <text x="600" y="176" font-family="{FONT}" font-size="13" fill="#3d6fb6" text-anchor="middle">SATURDAY</text>
  </g>

  <!-- Rico behind his counter, turned towards the crew -->
  <g transform="translate(1390 0) scale(-1 1)">
{crew.rico(695, y0=268)}
  </g>

  <!-- the counter: register, listening deck, and the drawer -->
  <g id="counter">
    <rect x="596" y="262" width="204" height="12" fill="#8b5a2b" stroke="#3a2414" stroke-width="2"/>
    <rect x="602" y="274" width="198" height="102" fill="#6b3f1f" stroke="#3a2414" stroke-width="2"/>
    <path d="M602 300H800M602 344H800" stroke="#553218" stroke-width="2"/>
    <rect x="726" y="226" width="60" height="36" rx="3" fill="#2a2a2a" stroke="#111" stroke-width="2"/>
    <rect x="734" y="232" width="44" height="12" fill="#7ed957" opacity="0.8"/>
    <text x="756" y="242" font-family="{FONT}" font-size="10" fill="#111" text-anchor="middle">$ 0.00</text>
  </g>
  <g id="listening-deck">
    <rect x="612" y="250" width="72" height="12" rx="2" fill="#2a2a2a" stroke="#111" stroke-width="1.5"/>
    {spinning_record(642, 250, 22, "#ff4f79")}
    <path d="M676 246L664 250" stroke="#c9ccd2" stroke-width="2"/>
    {notes}
  </g>
  <g id="drawer">
    <rect x="620" y="282" width="84" height="34" fill="#7a4a24" stroke="#3a2414" stroke-width="2"/>
    <rect x="652" y="296" width="20" height="6" rx="2" fill="#e0b84a"/>
  </g>
  <!-- the key: in the half-open drawer until the crew takes it -->
  <g data-overlay="offer-take_service_key" style="display:none" data-action="take_service_key" role="button" tabindex="0" aria-label="Take the old MTA service key">
    <title>Take the old MTA service key</title>
    <rect x="612" y="290" width="100" height="40" fill="#8b5a2b" stroke="#3a2414" stroke-width="2"/>
    <rect x="618" y="290" width="88" height="10" fill="#2a1a10"/>
    <rect x="652" y="312" width="20" height="6" rx="2" fill="#e0b84a"/>
    {_key_icon(638, 293, 0.9)}
    <g><animate attributeName="opacity" values="0;1;0" dur="1.4s" repeatCount="indefinite"/>{star(690, 284, 7, "#fff4c4")}</g>
    <g><animate attributeName="opacity" values="0;1;0" dur="1.4s" begin="0.7s" repeatCount="indefinite"/>{star(626, 284, 5, "#fff4c4")}</g>
  </g>
  <!-- end key -->

  <!-- the record bins -->
  <g id="record-bins">{"".join(bins)}</g>

  <!-- the crew, listening to Rico -->
{crew.portals(120, idle="still")}{crew.bible_either(178)}{crew.needle(236, idle="still")}{crew.meyhem(294)}{crew.reekz_front(340)}
  <!-- the way out -->
  {_way_out("go_block", "◀ BACK TO THE BLOCK", 8, "gBlueGreen", "#7ef0ff")}
{_dialogue(SCENES["record_shop"]["dialogue"], SHOP_SPEAKERS)}
  <!-- after taking the key -->
  <g data-overlay="done-take_service_key" style="display:none">
    <rect x="220" y="96" width="360" height="86" rx="12" fill="#111" stroke="#e0b84a" stroke-width="3" opacity="0.95"/>
    {_key_icon(262, 128, 1.4)}
    {piece(420, 138, "YOU GOT THE KEY!", "gGold", size=32, rot=-2, anchor="middle", fit=250)}
    <text x="420" y="166" font-family="{FONT}" font-size="14" fill="#f4f4f4" text-anchor="middle" letter-spacing="2">OLD MTA SERVICE KEY</text>
  </g>
'''
    return _svg(body, "scene-record-shop")


# Who says what on the block, and where their heads are.
NEEDLE_COURT_X, BIBLE_COURT_X, MEYHEM_X = 180, 545, 400  # Bible's spot is behind the three-point line  # where Needle starts his run, where Bible shoots from
BLOCK_SPEAKERS = {
    "needle": ("FANTASTIC NEEDLE", "#d02b2b", (NEEDLE_COURT_X, 238)),
    "bible": ("MC BIBLE", "#2e8b57", (BIBLE_COURT_X, 240)),
    "portals": ("PORTALS", "#3d6fb6", (110, 236)),
    "meyhem": ("MC MEYHEM", "#6b3fa8", (400, 240)),
    "reekz": ("REEKZ", "#c0392b", (465, 236)),
}


def _station_entrance(unlock_at=None, opened=False):
    """The old 149th St station from outside: a little IRT station house of cream glazed brick
    with a green copper roof, its name in a mosaic tablet over the arch, two green globes (the
    right one broken, flickering). Through the arch the stairs go down into the dark, a light
    flickering far below. The arch is shut with a scissor gate, chained and padlocked, a STATION
    CLOSED notice on it. unlock_at: when the key opens it (the padlock drops, the chain falls,
    the gate folds open). opened: the gate stands folded open, no chain, no padlock, no notice."""
    def drop(dy, secs):
        if unlock_at is None:
            return ""
        return (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {dy}" begin="{unlock_at + secs:.1f}s" dur="0.4s" fill="freeze"/>'
                f'<animate attributeName="opacity" values="1;0" begin="{unlock_at + secs + 0.2:.1f}s" dur="0.3s" fill="freeze"/>')
    left, right, top = 628, 744, 262  # the arch's opening
    if opened:
        fold = '<animateTransform attributeName="transform" type="scale" values="0.15 1" dur="0.1s" fill="freeze"/>'
    elif unlock_at is not None:
        fold = f'<animateTransform attributeName="transform" type="scale" values="1 1;0.15 1" begin="{unlock_at + 0.8:.1f}s" dur="0.6s" fill="freeze"/>'
    else:
        fold = ""
    bars = "".join(f'<path d="M{x} {top}V340" stroke="#8a8f98" stroke-width="3"/>' for x in range(left, right + 1, 12))
    lattice = "".join(f'<path d="M{x} {top + 4}L{x + 12} 300L{x} 336M{x + 12} {top + 4}L{x} 300L{x + 12} 336" '
                      f'stroke="#5d626b" stroke-width="1.6" fill="none"/>' for x in range(left, right - 11, 12))
    gate_class = ' class="open"' if opened else ""
    gate = (f'<g id="scissor-gate"{gate_class}><g transform="translate({left} 0)"><g>{fold}<g transform="translate(-{left} 0)">'
            f'<path d="M{left} {top + 2}H{right}M{left} 338H{right}" stroke="#6d727b" stroke-width="4"/>{bars}{lattice}</g></g></g></g>')
    chain = "".join(f'<ellipse cx="{x}" cy="{306 + 7 * math.sin((x - left) / (right - left) * math.pi):.1f}" rx="6.5" ry="3.8" '
                    f'fill="none" stroke="#c4c8d0" stroke-width="2.5"/>' for x in range(left + 4, right - 2, 10))
    lock = "" if opened else f'''
    <g id="chain">{drop(40, 0.4)}{chain}</g>
    <g id="padlock">{drop(60, 0.3)}
      <path d="M673 316V308A9 9 0 0 1 691 308V316" stroke="#c4c8d0" stroke-width="3.5" fill="none"/>
      <rect x="669" y="314" width="26" height="22" rx="3" fill="#c9a23a" stroke="#6b5214" stroke-width="2"/>
      <circle cx="682" cy="324" r="3" fill="#3a2e0a"/><path d="M682 326V330" stroke="#3a2e0a" stroke-width="2"/>
    </g>'''
    notice = "" if opened else (
        f'<g><title>STATION CLOSED</title>{drop(80, 0.9)}<g transform="rotate(-5 701 282)"><rect x="684" y="270" width="34" height="24" fill="#f4f0e2" stroke="#9a9488" stroke-width="1"/>'
        f'<text x="701" y="280" font-family="{FONT}" font-size="6.5" fill="#c0392b" text-anchor="middle">STATION</text>'
        f'<text x="701" y="289" font-family="{FONT}" font-size="6.5" fill="#c0392b" text-anchor="middle">CLOSED</text>'
        '<path d="M686 270l6 -3M712 270l6 -3" stroke="#d9cfa8" stroke-width="4" opacity="0.8"/></g></g>')
    # the stairs down, seen through the arch: steps getting narrower and darker towards the bottom
    shades = ("#6e6a62", "#57534c", "#45423d", "#36342f", "#2a2926", "#21201e", "#191917", "#131312")
    steps, y = [], 340.0
    for k, shade in enumerate(shades):
        h, w = 12 * 0.8 ** k, 112 * 0.86 ** k
        y -= h
        steps.append(f'<rect x="{686 - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{shade}"/>'
                     f'<path d="M{686 - w / 2:.1f} {y:.1f}H{686 + w / 2:.1f}" stroke="#8a857a" stroke-width="1" opacity="0.6"/>')
    flicker = 'keyTimes="0;0.5;0.53;0.56;0.6;0.63;1" dur="3.4s" repeatCount="indefinite"'
    stairs = f'''<g id="stairs">
      <clipPath id="archClip"><path d="M{left} 340V{top + 26}A58 28 0 0 1 {right} {top + 26}V340Z"/></clipPath>
      <g clip-path="url(#archClip)">
        <rect x="{left}" y="{top - 10}" width="{right - left}" height="{350 - top}" fill="#0b0b0e"/>
        <!-- a fluorescent tube far down below, flickering -->
        <ellipse cx="686" cy="296" rx="40" ry="16" fill="#d8f5c8" opacity="0.14"><animate attributeName="opacity" values="0.14;0.14;0.02;0.14;0.02;0.14;0.14" {flicker}/></ellipse>
        <rect x="672" y="282" width="28" height="4" rx="2" fill="#d8f5c8"><animate attributeName="opacity" values="1;1;0.2;1;0.1;1;1" {flicker}/></rect>
        <!-- the tiled walls of the stairwell, the handrails -->
        <path d="M{left} 340L670 292V{top}H{left}Z" fill="#c9c1a6" opacity="0.32"/><path d="M{right} 340L702 292V{top}H{right}Z" fill="#c9c1a6" opacity="0.32"/>
        <path d="M{left} 314L670 284M{right} 314L702 284" stroke="#6e8a4a" stroke-width="2.5"/>
        {"".join(steps)}
      </g>
    </g>
    <!-- end stairs -->'''

    def globe(gid, x, broken):
        glow = ('<animate attributeName="opacity" values="1;1;0.15;1;0.3;0.15;1;1" keyTimes="0;0.4;0.42;0.46;0.5;0.53;0.57;1" dur="2.6s" repeatCount="indefinite"/>'
                if broken else '<animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>')
        return (f'<g id="{gid}"><path d="M{x} 340V262" stroke="#1f5d3a" stroke-width="6"/><rect x="{x - 7}" y="260" width="14" height="6" fill="#1f5d3a"/>'
                f'<circle cx="{x}" cy="250" r="11" fill="#7ed957">{glow}</circle><circle cx="{x}" cy="250" r="19" fill="#7ed957" opacity="0.18"/></g>')
    tile = lambda x, y, c: f'<rect x="{x}" y="{y}" width="6" height="6" fill="{c}"/>'
    tiles = ("".join(tile(x, y, "#8b2a1a" if ((x - 616) // 7) % 2 else "#c9a23a") for y in (204, 234) for x in range(616, 756, 7))
             + "".join(tile(x, y, "#c9a23a") for x in (616, 750) for y in range(211, 234, 7)))
    return f'''<g id="station-entrance">
    <!-- the station house -->
    <g id="headhouse">
      <rect x="574" y="190" width="226" height="150" fill="#e6dcc0"/>
      <path d="{"".join(f"M574 {y}H800" for y in range(200, 340, 10))}" stroke="#d2c6a4" stroke-width="1.2"/>
      <rect x="574" y="190" width="18" height="150" fill="#2f6b4a"/><rect x="782" y="190" width="18" height="150" fill="#2f6b4a"/>
      <rect x="566" y="184" width="242" height="10" fill="#2f6b4a"/><rect x="570" y="330" width="234" height="10" fill="#4f4b44"/>
      {tag(752, 324, "SF", "#c0392b", 15, -8)}
    </g>
    <path id="station-roof" d="M562 186L590 160H786L800 172V186Z" fill="#5f9e86" stroke="#3d7a63" stroke-width="2"/>
    <path d="M590 160H786" stroke="#86c2a8" stroke-width="3"/>
    <!-- the name, in a mosaic tablet over the arch -->
    <rect x="616" y="204" width="140" height="36" fill="#efe8d2"/>{tiles}
    <text x="686" y="229" font-family="Georgia, serif" font-size="20" font-weight="bold" fill="#1f3a6a" text-anchor="middle" letter-spacing="2">149 ST</text>
    <rect x="626" y="244" width="120" height="12" rx="2" fill="#1f3a2a"/>
    <text x="686" y="253" font-family="Helvetica, Arial, sans-serif" font-size="8" font-weight="bold" fill="#f4f4f4" text-anchor="middle" letter-spacing="1.5">GRAND CONCOURSE</text>
    <!-- the arch, and the stairs down through it -->
    {stairs}
    <path id="station-arch" d="M{left - 4} 340V{top + 26}A62 31 0 0 1 {right + 4} {top + 26}V340" fill="none" stroke="#2f6b4a" stroke-width="8"/>
    <ellipse cx="686" cy="344" rx="70" ry="5" fill="#d8f5c8" opacity="0.1"/>
    {gate}
    {lock}
    {notice}
    {tag(634, 292, "keep out", "#d02b2b", 14, -6)}
    <text x="762" y="230" font-family="Arial, sans-serif" font-size="16" fill="#d02b2b">♛</text>
    {globe("globe-left", 602, False)}
    {globe("globe-right", 772, True)}
  </g>
  <!-- end station-entrance -->'''


def _corner_store():
    """A 1970s bodega on the corner: green awning, a window full of cans and boxes, a blinking
    OPEN sign, milk crates, a newspaper box and a payphone outside."""
    goods = "".join(f'<rect x="{x}" y="{y}" width="12" height="16" rx="2" fill="{c}" stroke="#111" stroke-width="1"/>'
                    for x, y, c in ((618, 268, "#d02b2b"), (632, 268, "#ffd23f"), (646, 268, "#3fa9f5"), (660, 268, "#7ed957"),
                                    (674, 268, "#ff8a3d"), (618, 286, "#f4f4f4"), (632, 286, "#c58bff"), (646, 286, "#d02b2b"),
                                    (660, 286, "#ffd23f"), (674, 286, "#3fa9f5")))
    return f'''<g id="corner-store">
    <rect x="590" y="150" width="210" height="200" fill="url(#bricks)"/>
    <rect x="590" y="150" width="210" height="200" fill="#2a1a20" opacity="0.25"/>
    <rect x="600" y="166" width="190" height="34" fill="#f4e7c3" stroke="#111" stroke-width="3"/>
    <text x="695" y="190" font-family="{FONT}" font-size="19" fill="#c0392b" text-anchor="middle" letter-spacing="1">CORNER STORE</text>
    <path d="M594 204H796L786 228H604Z" fill="#2e8b57"/>
    <path d="M614 204L610 228M640 204L638 228M666 204L666 228M692 204L694 228M718 204L722 228M744 204L750 228M770 204L778 228" stroke="#f4f4f4" stroke-width="9" opacity="0.9"/>
    <rect x="608" y="236" width="98" height="86" fill="#f9e2a2" stroke="#111" stroke-width="4"/>
    {goods}
    <rect x="618" y="244" width="64" height="20" rx="4" fill="#111"/>
    <text x="650" y="259" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#ff4f79" text-anchor="middle">OPEN
      <animate attributeName="opacity" values="1;1;0.2;1" dur="1.6s" repeatCount="indefinite"/></text>
    <text x="657" y="311" font-family="Arial, sans-serif" font-size="8" font-weight="bold" fill="#111" text-anchor="middle" textLength="90" lengthAdjust="spacingAndGlyphs">COLD SODA · HEROES · LOTTO</text>
    <rect x="718" y="240" width="58" height="110" fill="#5a3e2a" stroke="#111" stroke-width="4"/>
    <rect x="726" y="250" width="42" height="46" fill="#9fd3ff" opacity="0.6"/>
    <circle cx="766" cy="300" r="3.5" fill="#ffd23f"/>
    {tag(600, 340, "SF", "#111", 16, -6)}
  </g>
  <g id="crates">
    <rect x="612" y="356" width="28" height="22" fill="#2e6fb0" stroke="#1d4a78" stroke-width="2"/>
    <rect x="614" y="336" width="24" height="20" fill="#d02b2b" stroke="#7a1a1a" stroke-width="2"/>
    <path d="M612 367H640M626 356V378" stroke="#1d4a78" stroke-width="1.5"/>
  </g>
  <g id="payphone">
    <rect x="782" y="240" width="16" height="42" rx="2" fill="#9aa0a8" stroke="#111" stroke-width="2"/>
    <rect x="785" y="246" width="10" height="12" fill="#2a2a2a"/>
    <path d="M790 282V350" stroke="#555" stroke-width="3"/>
  </g>
  <!-- end corner-store -->'''


BALL_SPOT = (250, 388)  # where the basketball lies on the court until someone takes it
HOOP = (300, 206)  # where the ball goes in


def _once(attr, keys, secs, extra=""):
    """An animation through (t, value) keys that plays once when the player picks the shot
    (begin="indefinite": the page starts it when the shot comes up)."""
    values = ";".join(v for _, v in keys)
    times = ";".join(f"{t / secs:.4f}" for t, _ in keys)
    kind = "animateTransform" if attr in ("translate", "rotate", "scale") else "animate"
    what = f'attributeName="transform" type="{attr}"' if kind == "animateTransform" else f'attributeName="{attr}"'
    return f'<{kind} {what} values="{values}" keyTimes="{times}" dur="{secs}s" begin="indefinite" fill="freeze"{extra}/>'


def _hoop_front(swish_at=None, secs=None):
    """The front of the rim and the net, drawn over the ball, so it drops into the rim and you
    see it through the net (the back of the rim stays behind it, in the hoop). swish_at: when
    the ball goes through, the net stretches down for a moment (swish)."""
    swish = ""
    if swish_at is not None:
        swish = _once("scale", [(0, "1 1"), (swish_at, "1 1"), (swish_at + 0.15, "1 1.3"), (swish_at + 0.45, "1 1"), (secs, "1 1")], secs)
    net = ('<g stroke="#b9bec7" stroke-width="2.5" stroke-dasharray="4 3">'
           '<path d="M276 223L286 254M288 227L292 256M300 228V257M312 227L308 256M324 223L314 254"/></g>')
    return ('<g class="hoop-front"><path d="M274 222A26 6 0 0 0 326 222" stroke="#e8562a" stroke-width="4" fill="none"/>'
            f'<g transform="translate(300 223)"><g class="swish">{swish}<g transform="translate(-300 -223)">{net}</g></g></g></g>')


def _ball_drawing():
    return ('<circle r="11" fill="#e8742a" stroke="#5a2a10" stroke-width="2"/>'
            '<path d="M-11 0H11M0 -11V11M-7 -8Q-2 0 -7 8M7 -8Q2 0 7 8" stroke="#5a2a10" stroke-width="1.5" fill="none"/>')


def _arc(t0, t1, start, top, end, steps=6):
    """Points of the ball's flight from start over top to end (a curve), from t0 to t1."""
    (sx, sy), (cx, cy), (ex, ey) = start, top, end
    return [(t0 + (t1 - t0) * k / steps,
             (1 - k / steps) ** 2 * sx + 2 * (1 - k / steps) * (k / steps) * cx + (k / steps) ** 2 * ex,
             (1 - k / steps) ** 2 * sy + 2 * (1 - k / steps) * (k / steps) * cy + (k / steps) ** 2 * ey)
            for k in range(1, steps + 1)]


SHOT_SOUNDS = {}  # what each shot sounds like, and when (art/ambience.py makes the sound from it)


def _shot_sound(name, secs, moves, ball_keys, swish_at, dunk):
    """When the ball hits the ground (it comes down to the court), goes through the net, and
    when the shooter's sneakers squeak (he turns round); for the dunk: he lands, off the rim."""
    bounces = [t for (t, _, y), (_, _, before) in zip(ball_keys[1:], ball_keys) if y >= 380 > before and t < secs - 0.2]  # (not as it comes to rest)
    squeaks, last = [], 0
    for (t0, x0, _), (_, x1, _) in zip(moves, moves[1:]):
        if x1 != x0:
            if last and (x1 > x0) != (last > 0):
                squeaks.append(t0)
            last = x1 - x0
    lands = next((t for (t, _, y), (_, _, before) in zip(moves[1:], moves) if dunk and y == 0 > before), None)
    SHOT_SOUNDS[name] = {"secs": secs, "bounces": bounces, "swish_at": swish_at, "dunk": dunk,
                         "squeaks": squeaks, "lands": lands}
    return f'app/static/audio/block/{name}.wav'


def _shot(name, secs, figure, moves, arm_keys, ball_keys, flash, flash_at, sleeve, skin, mirror_x=None, gid=None, extra="",
          ball_id=None, swish_at=None, in_front=False):
    """One shot, played once when the player picks it: the shooter runs to the ball, takes it,
    dribbles (to the hoop or the three-point line), dunks or shoots, the ball goes in (SLAM! /
    SWISH!) and rolls back to its spot; when it's over the page says so (shot_done)."""
    arm = ('<g transform="translate(0 -44)">'
           + _once("rotate", [(t, f"{a}") for t, a in arm_keys], secs, ' additive="sum"')
           + f'<rect x="-5" y="0" width="10" height="38" rx="5" fill="{sleeve}"/><circle cy="40" r="6" fill="{skin}"/></g>')
    body = f'<g{f" id={chr(34)}{gid}{chr(34)}" if gid else ""}>{_once("translate", [(t, f"{x} {y}") for t, x, y in moves], secs)}{figure(arm)}</g>'
    if mirror_x is not None:  # he faces the hoop on his left
        body = f'<g transform="translate({2 * mirror_x} 0) scale(-1 1)">{body}</g>'
    ball = (f'<g{f" id={chr(34)}{ball_id}{chr(34)}" if ball_id else ""}>'
            f'{_once("translate", [(t, f"{x:.0f} {y:.0f}") for t, x, y in ball_keys], secs)}{_ball_drawing()}</g>')
    text, colour = flash
    shine = (f'<text x="{HOOP[0] + (38 if text == "SLAM!" else -74)}" y="196" font-family="{FONT}" font-size="24" fill="{colour}" '
             f'stroke="#111" stroke-width="1.2" text-anchor="middle" opacity="0">{text}'
             + _once("opacity", [(0, "0"), (flash_at, "0"), (flash_at + 0.05, "1"), (flash_at + 0.7, "1"), (flash_at + 0.75, "0"), (secs, "0")], secs)
             + '</text>')
    sound = _shot_sound(name, secs, moves, ball_keys, swish_at, dunk=text == "SLAM!")
    return (f'<g data-overlay="{name}" data-auto-action="shot_done" data-auto-delay="{secs}" data-sound="{sound}" style="display:none">'
            # in_front: the shooter is drawn over the front of the rim (dunking in front of the hoop)
            + (f'<g id="{name}">{extra}{ball}{_hoop_front(swish_at, secs)}{body}{shine}</g></g>' if in_front else
               f'<g id="{name}">{extra}{body}{ball}{_hoop_front(swish_at, secs)}{shine}</g></g>')
            + f'\n  <!-- end {name} -->')


def _shots():
    """The three shots the player can pick: Needle dunks; Bible shoots a three (from the right-hand
    line, facing the hoop); with his book in his hands, Needle takes the three (from the left)."""
    bx, by = BALL_SPOT
    n, b = NEEDLE_COURT_X, BIBLE_COURT_X
    # the dunk, an alley-oop: Bible walks over to the ball (facing left), picks it up, goes back to
    # the three-point line (his spot) and lobs it up at the rim; Needle runs in, jumps, catches it
    # in the air and dunks it, hangs on the rim, drops down and jogs back
    pick, secs = bx + 12, 7.2

    def bible_passes(book):
        def mirrored(svg):  # facing left, towards the ball and the hoop
            return f'<g transform="translate({2 * b} 0) scale(-1 1)">{svg}</g>'
        over = mirrored(_starts_on("dunkGo", crew.bible(b, Walk(dist=b - pick, secs=1.1, stride=0.6), book=book)))
        back = _starts_on("dunkGo", crew.bible(pick, Walk(dist=b - pick, secs=1.1, stride=0.6), book=book), 1.3)
        lob = mirrored(crew.bible(b, book=book, idle="still"))
        return (f'<g data-overlay="{"has" if book else "lacks"}-rhyme_book" style="display:none">'
                f'<g><set attributeName="visibility" to="hidden" begin="dunkGo.begin+1.3s" end="dunkGo.end"/>{over}</g>'
                f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="dunkGo.begin+1.3s" end="dunkGo.end"/>'
                f'<set attributeName="visibility" to="hidden" begin="dunkGo.begin+2.4s" end="dunkGo.end"/>{back}</g>'
                f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="dunkGo.begin+2.4s" end="dunkGo.end"/>{lob}</g>'
                '</g>\n  <!-- end dunk-bible -->')
    passer = (f'<animate id="dunkGo" attributeName="opacity" from="1" to="1" dur="{secs}s" begin="indefinite"/>'
              + bible_passes(False) + bible_passes(True))
    release, catch = (528, 290), (300, 198)
    dunk = _shot(
        "shot-dunk-needle", secs, lambda arm: crew.needle(n, idle="still", front_arm=arm),
        [(0, 0, 0), (2.5, 0, 0), (3.1, 90, 0), (3.4, 105, -45), (3.6, 107, -40), (4.0, 105, -43), (4.4, 107, -46),
         (4.8, 103, -44), (5.3, 105, -45), (5.6, 115, 0), (5.8, 115, 0), (7.0, 0, 0), (secs, 0, 0)],
        [(0, 0), (3.0, 0), (3.3, -155), (5.3, -155), (5.6, 0), (secs, 0)],
        [(0, bx, by), (1.1, bx, by), (1.3, pick - 10, 330), (2.4, b - 14, 320), (2.6, *release)]
        + _arc(2.6, 3.4, release, (420, 80), catch)
        + [(3.6, 302, 226), (3.8, 300, 262), (4.1, 300, 382), (4.5, 285, 350), (5.0, bx, by), (secs, bx, by)],
        ("SLAM!", "#ff4f79"), 3.6, "#f2c230", "#4a2e1c", gid="dunk-needle", extra=passer, ball_id="dunk-ball", swish_at=3.6,
        in_front=True)
    release = (509, 222)
    three_bible = _shot(
        "shot-three-bible", 4.6, lambda arm: crew.bible(b, book=False, idle="still", shooting_arm=arm),
        [(0, 0, 0), (1.0, 275, 0), (2.2, 25, 0), (2.4, 25, -16), (2.6, 25, 0), (3.6, 25, 0), (4.2, 0, 0), (4.6, 0, 0)],
        [(0, 0), (1.0, -60), (2.2, -60), (2.4, -165), (2.8, -165), (3.2, 0), (4.6, 0)],
        [(0, bx, by), (1.0, bx, by), (1.3, 300, 362), (1.6, 360, 384), (1.9, 430, 362), (2.2, 505, 300), (2.4, *release)]
        + _arc(2.4, 3.2, release, (410, 60), HOOP) + [(3.5, 300, 262), (3.7, 300, 382), (4.2, 262, by), (4.6, bx, by)],
        ("SWISH!", "#7ed957"), 3.25, "#161616", "#7a4a2e", mirror_x=b, swish_at=3.2)
    release = (77, 231)
    three_needle = _shot(
        "shot-three-needle", 3.8, lambda arm: crew.needle(n, idle="still", front_arm=arm),
        [(0, 0, 0), (0.5, 60, 0), (1.6, -120, 0), (1.8, -120, -16), (2.0, -120, 0), (2.6, -120, 0), (3.6, 0, 0), (3.8, 0, 0)],
        [(0, 0), (1.5, 0), (1.8, -155), (2.2, -155), (2.5, 0), (3.8, 0)],
        [(0, bx, by), (0.5, bx, by), (0.7, 220, 362), (0.9, 190, 384), (1.1, 150, 362), (1.3, 110, 384), (1.6, 80, 320), (1.8, *release)]
        + _arc(1.8, 2.6, release, (190, 60), HOOP) + [(2.9, 300, 262), (3.1, 300, 382), (3.4, 272, 360), (3.8, bx, by)],
        ("SWISH!", "#7ed957"), 2.65, "#f2c230", "#4a2e1c", swish_at=2.6)
    return dunk + "\n  " + three_bible + "\n  " + three_needle


def _ball_on_the_court():
    """The ball, lying on the court until a shot is picked: it glows a little, click it."""
    bx, by = BALL_SPOT
    return (f'<g data-overlay="!shooting"><g id="basketball" data-action="inspect:basketball" role="button" tabindex="0" '
            f'aria-label="The basketball: dunk or three"><title>The basketball</title>'
            f'<ellipse cx="{bx}" cy="{by + 10}" rx="14" ry="4" fill="#000" opacity="0.25"/>'
            f'<circle cx="{bx}" cy="{by}" r="17" fill="none" stroke="#fff4c4" stroke-width="2.5">'
            f'<animate attributeName="opacity" values="0.2;1;0.2" dur="1.4s" repeatCount="indefinite"/></circle>'
            f'<g transform="translate({bx} {by})">{_ball_drawing()}</g></g></g>\n  <!-- end basketball -->')


def _cypher():
    """A breaking crew cyphering on the sidewalk in front of the corner store, in the background:
    a b-boy toprocks on a flattened cardboard box, the others stand round him nodding to the
    music from a boombox on the milk crates."""
    scale, left, feet = 0.6, 596, 352
    def lx(world_x):  # where a world x is inside the (scaled) cypher
        return round((world_x - left) / scale)
    notes = "".join(f'<text x="{lx(x)}" y="300" font-family="Arial, sans-serif" font-size="26" fill="#ffd23f" opacity="0">{n}'
                    f'<animate attributeName="opacity" values="0;1;0" dur="1.6s" begin="{b}s" repeatCount="indefinite"/>'
                    f'<animateTransform attributeName="transform" type="translate" values="0 0;10 -50" dur="1.6s" begin="{b}s" repeatCount="indefinite"/></text>'
                    for x, n, b in ((628, "♪", 0), (640, "♫", 0.8)))
    return f'''<g id="cypher" transform="translate({left} {feet - scale * 375:.0f}) scale({scale})" data-action="inspect:cypher" role="button" tabindex="0" aria-label="The cypher: join in">
    <title>The cypher</title>
    <g id="cardboard"><path d="M{lx(704) - 70} 382L{lx(704) - 54} 366H{lx(704) + 70}L{lx(704) + 54} 382Z" fill="#b08a5a" stroke="#6b4e2a" stroke-width="2"/>
      <path d="M{lx(704) - 30} 368L{lx(704) - 40} 380M{lx(704) + 20} 368L{lx(704) + 10} 380" stroke="#8b6b3a" stroke-width="2"/></g>
    <g id="cypher-boombox" transform="translate({lx(612)} 318)">
      <path d="M6 0V-8H50V0" stroke="#222" stroke-width="4" fill="none"/>
      <rect width="56" height="30" rx="4" fill="#c9ccd2" stroke="#111" stroke-width="2.5"/>
      <circle cx="13" cy="15" r="9" fill="#222"/><circle cx="43" cy="15" r="9" fill="#222"/>
    </g>
    {notes}
{crew.bboy(lx(656), "kangol")}{crew.bboy(lx(680), "bucket hat")}
{crew.bboy(lx(732), "headband")}{crew.bboy(lx(762), "cap")}
{crew.bboy(lx(704), "toprock", dancing=True)}
  </g>
  <!-- end cypher -->'''


BLOCK_TRAIN = (7.0, 20)  # on the block the train takes this long to pass, and comes every this many seconds


def block_scene():
    """The block: the basketball court, its wall covered in the Sopranos' fresh tags, and a
    corner store at the corner. The 149 ST STATION button walks the crew to the old station.
    Portals studies the tags; a basketball bounces; the train goes by on the el."""
    portals_arm = ('<animateTransform attributeName="transform" type="rotate" values="-24 16 -46;-34 16 -46;-24 16 -46" '
                   'dur="3s" repeatCount="indefinite"/>')
    body = defs() + f'''
  <rect width="800" height="450" fill="url(#sky)"/>
  <circle cx="660" cy="70" r="36" fill="#fff1c1" opacity="0.7"/>
{skyline()}{train(f"{BLOCK_TRAIN[0]:g}s", every=BLOCK_TRAIN[1])}{el(columns=(150, 560))}
  <!-- the chain-link fence on top of the court wall -->
  <rect id="fence" x="0" y="112" width="590" height="40" fill="url(#chainlink)" opacity="0.9"/>
  <path d="M0 112H590M10 112V152M200 112V152M400 112V152M585 112V152" stroke="#5d626b" stroke-width="4"/>

  <!-- the court wall, covered in the Sopranos' fresh tags; their arrows point to the station -->
  <rect x="0" y="150" width="590" height="200" fill="url(#bricks)"/>
  <g id="sopranos-wall">
    {piece(24, 198, "SOPRANOS", "gSteel", size=40, rot=-4, shadow="#c0392b", fit=200)}
    {piece(40, 232, "FAMILY", "gSteel", size=28, rot=3, shadow="#c0392b", fit=124)}
    <text x="214" y="186" font-family="Arial, sans-serif" font-size="26" fill="#c0392b" transform="rotate(-8 214 186)">♛</text>
    <text x="520" y="200" font-family="Arial, sans-serif" font-size="22" fill="#c0392b" transform="rotate(10 520 200)">♛</text>
    {tag(380, 190, "Krete", "#f4f4f4", 24, -6)}
    {tag(440, 236, "Sopranos", "#111", 22, 4)}
    {tag(500, 176, "SF", "#d02b2b", 26, -10)}
    {tag(30, 316, "Krete 77", "#111", 20, -3)}
    {tag(236, 300, "SF", "#f4f4f4", 22, 6)}
    {tag(360, 336, "Sopranos", "#f4f4f4", 18, -2)}
  </g>
  <!-- end sopranos-wall -->

  <!-- the hoop, with a chain net -->
  <g id="hoop">
    <path d="M285 205L300 220L315 205" stroke="#333" stroke-width="5" fill="none"/>
    <rect x="252" y="160" width="96" height="58" rx="3" fill="#f4f4f4" stroke="#222" stroke-width="3"/>
    <rect x="282" y="182" width="36" height="26" fill="none" stroke="#e8562a" stroke-width="3"/>
    <ellipse cx="300" cy="222" rx="26" ry="6" fill="none" stroke="#e8562a" stroke-width="4"/>
    <g stroke="#b9bec7" stroke-width="2.5" stroke-dasharray="4 3">
      <path d="M276 223L286 254M288 227L292 256M300 228V257M312 227L308 256M324 223L314 254"/>
    </g>
  </g>

  <!-- the court, and the sidewalk at the corner store -->
  <g id="court">
    <rect y="350" width="590" height="100" fill="#3e6e55"/>
    <path d="M0 350H590" stroke="#2c5040" stroke-width="4"/>
    <g stroke="#f2f2f2" stroke-width="4" fill="none">
      <path d="M40 350A260 80 0 0 0 560 350"/>
      <path d="M245 350L230 430H370L355 350"/>
      <path d="M230 430A70 15 0 0 0 370 430"/>
    </g>
    <path d="M245 350H355L370 430H230Z" fill="#c0392b" opacity="0.35"/>
  </g>
  <rect x="590" y="350" width="210" height="100" fill="#9a9aa2"/>
  <path d="M590 350H800" stroke="#6e6e76" stroke-width="3"/>

  <!-- the corner store: a bodega on the corner of the block, a cypher in front of it -->
  {_corner_store()}
  <g data-overlay="met-flash" style="display:none">{_cypher()}</g>
  <!-- in through the corner store's door -->
  <g data-action="go_store" role="button" tabindex="0" aria-label="Into the corner store"><title>Into the corner store</title>
    <rect x="718" y="240" width="58" height="110" fill="#fff" fill-opacity="0.01"/>
    <rect x="712" y="234" width="70" height="22" rx="6" fill="#111" stroke="#ffd23f" stroke-width="2"/>
    <text x="747" y="250" font-family="{FONT}" font-size="13" fill="#ffd23f" text-anchor="middle">STORE ▶</text>
  </g>
  <!-- once the crew has the key: it glints over the way to the station -->
  <g data-overlay="has-service_key" style="display:none">
    {_key_icon(742, 380, 1.0)}
    <g><animate attributeName="opacity" values="0;1;0" dur="1.2s" repeatCount="indefinite"/>{star(780, 374, 7, "#fff4c4")}</g>
  </g>

  <!-- the crew; Portals studies the Sopranos' piece from close up -->
  <!-- Needle and Bible (as long as his hands are free) shoot hoops when the player picks a shot -->
  <g data-overlay="!needle-shooting">{crew.needle(NEEDLE_COURT_X, idle="still")}</g>
  <g data-overlay="lacks-rhyme_book !bible-shooting" style="display:none">{crew.bible(BIBLE_COURT_X, book=False, idle="still")}</g>
  <g data-overlay="has-rhyme_book !bible-shooting" style="display:none">{crew.bible(BIBLE_COURT_X, book=True)}</g>
  {_ball_on_the_court()}
  <g transform="translate(110 327)">
{crew.portals_back(portals_arm, '<set attributeName="opacity" to="0" begin="0s"/>')}
  </g>
{crew.meyhem_front(MEYHEM_X)}{crew.reekz_front(465)}
  <!-- the shots the player can pick (whoever shoots is in front of everyone) -->
  {_shots()}
  <!-- the front of the rim and the net, over the court (in a shot it comes with the shot) -->
  <g data-overlay="!shooting">{_hoop_front()}</g>
  <!-- the ways out -->
  {_way_out("go_hq", "◀ BACK TO THE BASEMENT", 8, "gBlueGreen", "#7ef0ff")}
  {_way_out("go_record_shop", "RICO'S RECORDS ▶", 204, "gPinkYellow", "#ff6fa8")}
  {_way_out("go_battle", "DISCO FEVER ▶", 400, "gPurple", "#c58bff")}
  {_way_out("go_gate", "149 ST STATION ▶", 596, "gGold", "#7ed957")}
{_dialogue(SCENES["block"]["dialogue"], BLOCK_SPEAKERS)}
  {_message_sign("done-win_cypher", "$10 FOR THE CREW!", next(a["message"] for a in SCENES["block"]["actions"] if a["id"] == "win_cypher"), "#7ed957", "gGold")}
  {"".join(_inspect_sign(t, info) for t, info in SCENES["block"]["things"].items())}
'''
    passing, every = BLOCK_TRAIN
    train_sound = [{"src": "app/static/audio/block/train.wav", "on": [[0, passing]], "every": every, "vol": 0.5}]
    return _svg(body, "scene-block", cues=train_sound)


# Who says what in the station, and where their heads are (Krete sits on his crate).
# Where everyone stands round the mic at the rap battle, in a half circle like a cypher: (x, feet,
# scale). The GoodFellas on the left, the ones further back smaller; the Sopranos on the right.
STATION_SPOTS = {"reekz": (330, 346, 0.85), "meyhem": (282, 351, 0.87), "bible": (226, 361, 0.91),
                 "needle": (168, 378, 0.96), "portals": (110, 400, 1.02)}
SOPRANOS_SPOTS = [(668, 356, 0.88, "#c0392b"), (738, 382, 0.96, "#111")]
MIC = (382, crew.FEET_Y)  # where the rapper stands at the mic


def _head(who):
    x, feet, scale = STATION_SPOTS[who]
    return (x, round(feet - crew.HEAD_ABOVE_FEET * scale))


STATION_SPEAKERS = {
    "krete": ("KING KRETE", "#e0b84a", (607, 214)),
    "portals": ("PORTALS", "#3d6fb6", _head("portals")),
    "bible": ("MC BIBLE", "#2e8b57", _head("bible")),
    "needle": ("FANTASTIC NEEDLE", "#d02b2b", _head("needle")),
    "meyhem": ("MC MEYHEM", "#6b3fa8", _head("meyhem")),
    "reekz": ("REEKZ", "#c0392b", _head("reekz")),
}


def _at_spot(who, svg_at_x):
    x, feet, scale = STATION_SPOTS[who]
    return crew.placed(svg_at_x, who, x, feet, scale)


def _to_the_mic(who, walking_at_0, secs, trigger):
    """The rapper walks out of the circle to the mic: forward and nearer (bigger), from his spot."""
    x, feet, scale = STATION_SPOTS[who]
    return (f'<g><animateTransform attributeName="transform" type="translate" values="{x:g} {feet:g};{MIC[0]:g} {MIC[1]:g}" dur="{secs}s" begin="{trigger}.begin" fill="freeze"/>'
            f'<g><animateTransform attributeName="transform" type="scale" values="{scale:g};1" dur="{secs}s" begin="{trigger}.begin" fill="freeze"/>'
            f'<g transform="translate(0 -{crew.FEET_Y})">{_starts_on(trigger, walking_at_0)}</g></g></g>')


def _mosaic_sign(x, y, w, h, text):
    """A classic NYC subway mosaic name tablet, a few tiles missing."""
    border = []
    step = 8
    for i in range(0, w, step):
        for j in (0, h - step):
            missing = (i * 7 + j) % 53 == 0
            border.append(f'<rect x="{x + i}" y="{y + j}" width="{step - 1}" height="{step - 1}" '
                          f'fill="{"#2a2a2a" if missing else ("#8b2a1a" if (i // step) % 2 else "#c9a23a")}"/>')
    for j in range(step, h - step, step):
        for i in (0, w - step):
            border.append(f'<rect x="{x + i}" y="{y + j}" width="{step - 1}" height="{step - 1}" '
                          f'fill="{"#8b2a1a" if (j // step) % 2 else "#c9a23a"}"/>')
    return (f'<g id="mosaic-sign"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#e8e0c8"/>{"".join(border)}'
            f'<text x="{x + w / 2}" y="{y + h / 2 + 11}" font-family="Georgia, serif" font-size="30" font-weight="bold" '
            f'fill="#1f3a6a" text-anchor="middle" letter-spacing="3">{text}</text>'
            '</g>\n  <!-- end mosaic-sign -->')


# The audience at the rap battle sits on and in the abandoned car: windows, open doors, roof.
CAR_WINDOWS = [20, 70, 270, 320, 380]
CAR_DOORS = [130, 196]
ROOF_CROWD = [60, 112, 262, 330]


def _train_crowd():
    """People from the block came down to watch: looking out of the car's windows, standing in
    its two open doors, and sitting on its roof with their legs dangling."""
    looks = crew.LOOKS
    windows = "".join(
        f'<rect x="{x}" y="132" width="36" height="36" rx="3" fill="#1a1a1e" stroke="#555" stroke-width="2"/>'
        + crew.spectator_in_window(x + 18, 134, looks[k % len(looks)], k)
        for k, x in enumerate(CAR_WINDOWS))
    doors = "".join(
        f'<g class="open-door"><rect x="{x}" y="130" width="44" height="114" fill="#141418" stroke="#555" stroke-width="2"/>'
        f'<rect x="{x - 10}" y="130" width="12" height="114" fill="#9a9da4" stroke="#555" stroke-width="1.5"/>'
        f'<rect x="{x + 42}" y="130" width="12" height="114" fill="#9a9da4" stroke="#555" stroke-width="1.5"/>'
        + crew.spectator_in_door(x + 22, 244, looks[(k + 5) % len(looks)], k + 5) + "</g>"
        for k, x in enumerate(CAR_DOORS))
    roof = "".join(crew.spectator_on_roof(x, 122, looks[(k + 7) % len(looks)], k + 7) for k, x in enumerate(ROOF_CROWD))
    return (f'  <!-- the audience inside the car: in the windows and the open doors -->\n'
            f'  <g id="train-crowd">{windows}{doors}</g>\n  <!-- end train-crowd -->\n',
            f'  <!-- the audience on the roof of the car -->\n'
            f'  <g id="car-roof-crowd">{roof}</g>\n  <!-- end car-roof-crowd -->\n')


def _starts_on(trigger, svg, delay=0):
    """Make every animation in svg start when the trigger starts (plus delay seconds), instead of
    when the page loads. Animations that already have their own begin keep it."""
    start = f'{trigger}.begin+{delay:.2f}s' if delay else f'{trigger}.begin'
    for tag_name in ("<animateTransform ", "<animate "):
        svg = svg.replace(tag_name, f'{tag_name}begin="{start}" ')
    return svg.replace(f'begin="{start}" begin=', "begin=")


def _station_message(action_id):
    return next(a["message"] for a in SCENES["station"]["actions"] if a["id"] == action_id)


def _pick_rapper(action, who, label, colour):
    """Click the rapper himself: a ring pulses round him (in his spot) while the choice is open."""
    x, feet, scale = STATION_SPOTS[who]
    return (f'<g data-action="{action}" role="button" tabindex="0" aria-label="{label}"><title>{label}</title>'
            f'<ellipse cx="{x}" cy="{feet - 64 * scale:.0f}" rx="{32 * scale:.0f}" ry="{68 * scale:.0f}" fill="#fff" fill-opacity="0.01" stroke="{colour}" stroke-width="3" stroke-dasharray="8 6">'
            f'<animate attributeName="stroke-opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite"/></ellipse></g>')


def _performs(who, x, walking, on_mic, colour, walk_secs, waves=True):
    """While he raps ("rapping-<who>"): he walks from his spot to the mic, then raps on it
    (waves: sound waves at the mic; none when nothing comes out)."""
    begin = f"{who}In".replace("_", "")
    waves = "" if not waves else "".join(f'<circle cx="410" cy="254" r="8" fill="none" stroke="{colour}" stroke-width="3">'
                    f'<animate attributeName="r" values="8;60" dur="0.8s" begin="{b}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="1;0" dur="0.8s" begin="{b}s" repeatCount="indefinite"/></circle>'
                    for b in (0, 0.27, 0.54))
    return f'''<g data-overlay="rapping-{who}" style="display:none"><g id="{who}-performs">
    <animate id="{begin}" attributeName="opacity" from="1" to="1" dur="0.1s" begin="indefinite"/>
    <g><set attributeName="visibility" to="hidden" begin="{begin}.begin+{walk_secs}s" fill="freeze"/>
{_to_the_mic(who.replace("_chokes", ""), walking, walk_secs, begin)}
    </g>
    <g visibility="hidden"><set attributeName="visibility" to="visible" begin="{begin}.begin+{walk_secs}s" fill="freeze"/>
{on_mic}
      {waves}
    </g>
  </g></g>
  <!-- end {who}-performs -->'''


def station_scene():
    """The abandoned 149th St station, the Sopranos' hideout: dirty tiles with the mosaic
    name sign, an abandoned graffiti-covered car on the track, flickering lights, dust, a fire
    in an oil drum. King Krete sits on a crate with "Think About It" under his arm, two
    Sopranos behind him; the crew has just come in."""
    extra = '''    <pattern id="tiles" width="22" height="11" patternUnits="userSpaceOnUse">
      <rect width="22" height="11" fill="#cfc8b8"/><path d="M0 0H22M0 0V11" stroke="#9e9786" stroke-width="1.5"/>
    </pattern>
    <radialGradient id="fireGlow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#ffb347" stop-opacity="0.55"/><stop offset="1" stop-color="#ffb347" stop-opacity="0"/>
    </radialGradient>
'''
    lights = "".join(
        f'<g><animate attributeName="opacity" values="{v}" dur="{d}s" repeatCount="indefinite"/>'
        f'<rect x="{x}" y="22" width="90" height="7" rx="3" fill="#f4f8e8"/>'
        f'<polygon points="{x},29 {x + 90},29 {x + 130},230 {x - 40},230" fill="#f4f8e8" opacity="0.08"/></g>'
        f'<path d="M{x + 10} 0V22M{x + 80} 0V22" stroke="#2a2a2a" stroke-width="2"/>'
        for x, v, d in ((120, "1;1;0.2;1;0.3;1;1", 3.1), (470, "1;0.9;1;1;0.1;1", 4.3)))
    dust = "".join(
        f'<circle cx="{x}" cy="{y}" r="1.6" fill="#f4f8e8" opacity="0.5">'
        f'<animate attributeName="cy" values="{y};{y - 60};{y}" dur="{d}s" repeatCount="indefinite"/>'
        f'<animate attributeName="cx" values="{x};{x + 14};{x}" dur="{d}s" repeatCount="indefinite"/></circle>'
        for x, y, d in ((150, 200, 7), (210, 160, 9), (520, 190, 8), (560, 140, 10), (330, 120, 11), (700, 170, 9)))
    flames = "".join(
        f'<path d="M{x - w} 322Q{x} {322 - h} {x + w} 322Z" fill="{c}">'
        f'<animateTransform attributeName="transform" type="scale" values="1 1;1 {s};1 1" dur="{d}s" repeatCount="indefinite" additive="sum"/></path>'
        for x, w, h, c, s, d in ((24, 18, 52, "#ff6b2b", 1.08, 0.5), (36, 12, 64, "#ffb347", 0.92, 0.4), (16, 9, 40, "#fff07a", 1.1, 0.35)))
    record = f'''<g id="stolen-record" data-action="inspect:stolen_record" role="button" tabindex="0" aria-label="The stolen record">
    <title>LYN COLLINS – THINK ABOUT IT (the stolen record)</title>
    <g transform="rotate(-8 586 300)">
      <rect x="566" y="282" width="38" height="38" fill="#ff6fa8" stroke="#111" stroke-width="2"/>
      <path d="M566 292H604M566 309H604" stroke="#ffd23f" stroke-width="4"/>
      <text x="585" y="304" font-family="{FONT}" font-size="9" fill="#111" text-anchor="middle">THINK</text>
      <circle cx="600" cy="286" r="9" fill="#111"/><circle cx="600" cy="286" r="3" fill="#ff4f79"/>
    </g>
    <g><animate attributeName="opacity" values="0;1;0" dur="1.4s" repeatCount="indefinite"/>{star(612, 276, 6, "#fff4c4")}</g>
  </g>
  <!-- end stolen-record -->'''
    train_crowd, roof_crowd = _train_crowd()
    body = defs(DUSK, extra=extra) + f'''
  <!-- the tiled walls, dirty and dark -->
  <rect width="800" height="250" fill="url(#tiles)"/>
  <rect width="800" height="250" fill="#0b0716" opacity="0.55"/>
  <path d="M0 60H800" stroke="#1f3a6a" stroke-width="6" opacity="0.6"/>
  {_mosaic_sign(474, 82, 176, 56, "149 ST")}
  {tag(680, 120, "Sopranos", "#c0392b", 24, -6)}
  {tag(690, 170, "SF", "#f4f4f4", 26, 8)}
  {tag(250, 52, "Krete", "#f4f4f4", 20, -4)}

  <!-- the track, and an abandoned car on it, covered in the Sopranos' pieces -->
  <g id="tracks">
    <rect y="250" width="800" height="54" fill="#18171c"/>
    <path d="M0 274H800M0 292H800" stroke="#5d626b" stroke-width="4"/>
    <path d="M0 284H800" stroke="#3a3a3a" stroke-width="2" stroke-dasharray="10 14"/>
  </g>
  <g id="abandoned-car">
    <rect x="-10" y="122" width="440" height="128" rx="8" fill="#8d9097" stroke="#4a4a4a" stroke-width="3"/>
    <rect x="-10" y="122" width="440" height="128" rx="8" fill="#5a3a24" opacity="0.25"/>
    {piece(254, 222, "SOPRANOS", "gSteel", size=36, rot=-3, shadow="#c0392b", fit=168)}
    <text x="400" y="200" font-family="Arial, sans-serif" font-size="26" fill="#c0392b" transform="rotate(8 400 200)">♛</text>
    {tag(16, 206, "Krete 77", "#111", 18, -3)}
{train_crowd}
    <circle cx="40" cy="252" r="9" fill="#2a2a2a"/><circle cx="80" cy="252" r="9" fill="#2a2a2a"/>
    <circle cx="330" cy="252" r="9" fill="#2a2a2a"/><circle cx="370" cy="252" r="9" fill="#2a2a2a"/>
  </g>
{roof_crowd}

  <!-- the platform -->
  <rect id="platform-edge" y="304" width="800" height="9" fill="#e8c840"/>
  <path d="M0 308.5H800" stroke="#a88a20" stroke-width="2" stroke-dasharray="3 5"/>
  <rect y="313" width="800" height="137" fill="#5c5a60"/>
  <path d="M60 360L120 372M400 420L470 410M620 440L700 430" stroke="#46444a" stroke-width="3"/>
  <!-- columns -->
  <g fill="#1f2e3a" stroke="#111" stroke-width="2">
    <rect x="440" y="0" width="18" height="304"/><rect x="780" y="0" width="18" height="304"/>
  </g>

  <!-- the mic stand in the middle of the platform -->
  <g id="mic-stand">
    <path d="M410 376V262M410 376L396 380M410 376L424 380" stroke="#8d9097" stroke-width="3"/>
    <g data-overlay="!rapping">
      <rect x="406" y="250" width="8" height="16" rx="2" fill="#2a2a2a"/>
      <circle cx="410" cy="246" r="7" fill="#c9ccd2" stroke="#555" stroke-width="1.5"/>
    </g>
  </g>
  <!-- end mic-stand -->

  <!-- the lights flicker, dust hangs in the air -->
  <g id="flicker-lights">{lights}</g>
  <g id="dust">{dust}</g>

  <!-- the fire in an oil drum, at the edge -->
  <g id="fire-barrel">
    <circle cx="26" cy="320" r="70" fill="url(#fireGlow)">
      <animate attributeName="r" values="66;74;66" dur="0.9s" repeatCount="indefinite"/></circle>
    {flames}
    <rect x="2" y="322" width="48" height="56" rx="4" fill="#6b3a1e" stroke="#2a1608" stroke-width="2"/>
    <path d="M2 336H50M2 362H50" stroke="#3a2010" stroke-width="3"/>
  </g>

  <!-- the battle DJ provides the beats, next to the mic -->
{crew.battle_dj(518, 330)}

  <!-- King Krete on his crate with the record, two Sopranos behind him -->
{"".join(crew.placed(f'<g transform="translate({2 * x} 0) scale(-1 1)">{crew.sopranos_member(x, bandana=b)}</g>', f"sopranos-{k}", x, feet, sc)
          for k, (x, feet, sc, b) in enumerate(SOPRANOS_SPOTS))}
  <rect x="582" y="334" width="62" height="44" fill="#8b5a2b" stroke="#3a2414" stroke-width="2"/>
  <path d="M582 356H644M603 334V378M623 334V378" stroke="#5a3a1a" stroke-width="2"/>
  <g transform="translate(1214 0) scale(-1 1)">
{crew.king_krete(607, 334)}
  </g>
  <g data-overlay="lacks-vinyl" style="display:none">{record}</g>
  <g data-overlay="has-vinyl" style="display:none">
    <g transform="rotate(-10 166 316)">
      <rect x="148" y="298" width="36" height="36" fill="#ff6fa8" stroke="#111" stroke-width="2"/>
      <path d="M148 308H184M148 324H184" stroke="#ffd23f" stroke-width="4"/>
      <text x="166" y="320" font-family="{FONT}" font-size="9" fill="#111" text-anchor="middle">THINK</text>
    </g>
    <g><animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite"/>{star(190, 294, 7, "#fff4c4")}</g>
  </g>

  <!-- the crew round the mic, in a half circle (whoever is on the mic is not in his spot) -->
{_at_spot("reekz", crew.reekz_front(STATION_SPOTS["reekz"][0], idle="still", music=False))}
  <g data-overlay="!mic-meyhem">{_at_spot("meyhem", crew.meyhem(STATION_SPOTS["meyhem"][0], idle="still"))}</g>
{_at_spot("bible", crew.bible_either(STATION_SPOTS["bible"][0], hide_when="mic-bible"))}
{_at_spot("needle", crew.needle(STATION_SPOTS["needle"][0], idle="angry"))}
{_at_spot("portals", crew.portals(STATION_SPOTS["portals"][0], idle="still"))}
  <!-- the rapper walks out of the circle, grabs the mic and raps; the crowd throws its arms up -->
  {_performs("meyhem", 0, crew.meyhem(0, Walk(dist=0, secs=1.5)), crew.meyhem_on_mic(MIC[0]), "#c58bff", 1.5)}
  {_performs("bible", 0, crew.bible(0, Walk(dist=0, secs=2), book=True), crew.bible_on_mic(MIC[0]), "#e0b84a", 2)}
  <!-- Bible without his rhyme book: he chokes at the mic, the crowd boos him off -->
  {_performs("bible_chokes", 0, crew.bible(0, Walk(dist=0, secs=2), book=False), crew.bible_choking(MIC[0]), "#d02b2b", 2, waves=False)}
  <g data-overlay="booing" style="display:none"><g id="crowd-boos">
    {"".join(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="#d02b2b" stroke="#111" stroke-width="1" transform="rotate({rot} {x} {y})">BOOO!<animate attributeName="opacity" values="1;0.2;1" dur="{d}s" repeatCount="indefinite"/></text>' for x, y, size, rot, d in ((40, 112, 22, -8, 0.9), (210, 104, 26, 6, 1.1), (330, 140, 20, -4, 0.8), (150, 196, 18, 8, 1.0), (470, 236, 22, -6, 1.2)))}
    {"".join(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="22">👎<animateTransform attributeName="transform" type="translate" values="0 0;0 6;0 0" dur="0.5s" repeatCount="indefinite"/></text>' for x, y in ((96, 150), (270, 180), (380, 110)))}
    <rect x="470" y="160" width="250" height="36" rx="12" fill="#f4f4f4" stroke="#111" stroke-width="2.5"/>
    <path d="M600 196L606 210L614 196Z" fill="#f4f4f4" stroke="#111" stroke-width="2"/>
    <text x="595" y="184" font-family="Arial Black, Arial, sans-serif" font-weight="bold" font-size="14" fill="#111" text-anchor="middle">WHERE&#39;S YOUR BOOK, BIBLE?</text>
  </g></g>
  <!-- end crowd-boos -->
  <!-- while Meyhem raps, Krete can't keep up -->
  <g data-overlay="rapping-meyhem" style="display:none">
    <text x="560" y="230" font-family="{FONT}" font-size="30" fill="#ffd23f" stroke="#111" stroke-width="1">?!
      <animateTransform attributeName="transform" type="translate" values="0 0;3 -2;-3 0;0 0" dur="0.3s" repeatCount="indefinite"/></text>
  </g>
  <!-- the way out -->
  {_way_out("go_block", "◀ BACK TO THE BLOCK", 8, "gBlueGreen", "#7ef0ff")}
  <!-- who goes first? click the rapper, or his button -->
  <g data-overlay="battle-open !rapping" style="display:none"><g id="who-goes-first">
    <rect x="236" y="14" width="328" height="44" rx="10" fill="#111" stroke="#ffd23f" stroke-width="3" opacity="0.92"/>
    {piece(400, 46, "WHO GOES FIRST?", "gPinkYellow", size=28, rot=-2, anchor="middle", fit=300)}
    {_pick_rapper("meyhem_first", "meyhem", "Meyhem goes first", "#c58bff")}
    {_pick_rapper("bible_first", "bible", "Bible goes first", "#e0b84a")}
    {_way_out("meyhem_first", "MEYHEM FIRST ▶", 406, "gPurple", "#c58bff")}
    {_way_out("bible_first", "BIBLE FIRST ▶", 604, "gGold", "#e0b84a")}
  </g></g>
  <!-- end who-goes-first -->
  <!-- Meyhem has thrown Krete: Bible finishes him -->
  <g data-overlay="battle-meyhem_went_first !rapping" style="display:none">
    {_pick_rapper("bible_finishes", "bible", "Bible finishes him", "#e0b84a")}
    {_way_out("bible_finishes", "BIBLE, FINISH HIM ▶", 590, "gGold", "#e0b84a")}
  </g>
  <!-- SKIP: the verse stops (and the outcome comes up) -->
  <g data-overlay="rapping" style="display:none"><g id="skip-verse" data-action="skip_verse" role="button" tabindex="0" aria-label="Skip the verse">
    <title>Skip the verse</title>
    <rect x="684" y="60" width="100" height="38" rx="9" fill="#111" stroke="#f4f4f4" stroke-width="2.5" opacity="0.9"/>
    {piece(734, 88, "SKIP ▶▶", "gWhite", size=22, rot=-2, anchor="middle", fit=80)}
  </g></g>
  <!-- end skip-verse -->
{_dialogue(SCENES["station"]["dialogue"], STATION_SPEAKERS)}
  <!-- what happened, once the rapping is over -->
  {_message_sign("done-meyhem_first !rapping", "MEYHEM GOES FIRST!", _station_message("meyhem_first"), "#c58bff", "gPurple")}
  {_message_sign("done-bible_finishes !rapping", "BIBLE FINISHES HIM!", _station_message("bible_finishes") + " You got the record back!", "#e0b84a", "gGold")}

  {"".join(_inspect_sign(t, info) for t, info in SCENES["station"]["things"].items())}
'''
    return _svg(body, "scene-station")


# Who says what at Disco Fever, and where their heads are.
BATTLE_SPEAKERS = {
    "host": ("THE HOST", "#7d3cff", (360, 196)),
    "krete": ("KING KRETE", "#e0b84a", (648, 214)),
    "needle": ("FANTASTIC NEEDLE", "#d02b2b", (290, 238)),
    "reekz": ("REEKZ", "#c0392b", (230, 236)),
}
CLUB_LIGHTS = ["#ff4f79", "#7ef0ff", "#ffd23f", "#7ed957", "#c58bff"]


def _club(sky, floor_glow=True, neon=True):
    """Disco Fever: dark club walls, the neon sign, the disco ball and its moving light spots,
    a stage with the DJ booth, and a light-up dance floor. neon=False: without the sign (the
    endings put their title there)."""
    spots = "".join(
        f'<circle r="{r}" fill="{c}" opacity="0.35"><animateMotion dur="{d}s" repeatCount="indefinite" '
        f'path="M{x} {y}Q{x + 180} {y - 60} {x + 320} {y + 40}T{x} {y}"/></circle>'
        for (x, y, r, d), c in zip(((60, 120, 26, 7), (420, 90, 20, 9), (200, 200, 30, 8), (560, 150, 22, 6),
                                    (300, 60, 18, 10)), CLUB_LIGHTS))
    floor = []
    for i in range(4):
        for j in range(16):
            c = CLUB_LIGHTS[(i + j) % len(CLUB_LIGHTS)]
            floor.append(f'<rect x="{j * 50}" y="{380 + i * 18}" width="50" height="18" fill="{c}" opacity="0.25">'
                         + (f'<animate attributeName="opacity" values="0.15;0.6;0.15" dur="1s" begin="{((i * 3 + j) % 5) * 0.2:.1f}s" repeatCount="indefinite"/>'
                            if floor_glow else "") + '</rect>')
    rays = "".join(f'<path d="M620 78L{x} 380" stroke="{c}" stroke-width="2" opacity="0.18"/>'
                   for x, c in zip((80, 260, 440, 700, 790), CLUB_LIGHTS))
    return f'''
  <rect width="800" height="450" fill="{sky}"/>
  <rect y="300" width="800" height="150" fill="#14101c"/>
  <g id="light-spots">{spots}</g>
  <!-- the neon sign -->
  <g filter="url(#neonGlow)"{"" if neon else ' display="none"'}>
    <animate attributeName="opacity" values="1;0.8;1" dur="1.2s" repeatCount="indefinite"/>
    <text x="250" y="70" font-family="{TAG_FONT}" font-size="54" fill="none" stroke="#ff4f4f" stroke-width="3" text-anchor="middle">Disco Fever</text>
    <text x="250" y="96" font-family="{FONT}" font-size="12" fill="#7ef0ff" text-anchor="middle" letter-spacing="5">BOROUGH FINAL · TONIGHT</text>
  </g>
  <!-- the disco ball -->
  <path d="M620 0V40" stroke="#c9ccd2" stroke-width="2"/>
  <g id="disco-ball">
    <circle cx="620" cy="70" r="30" fill="#c9ccd2" stroke="#8d9097" stroke-width="2"/>
    <g clip-path="url(#ballClip)">
      <g><animateTransform attributeName="transform" type="translate" values="0 0;-16 0" dur="0.8s" repeatCount="indefinite"/>
        {"".join(f'<path d="M{590 + k * 8} 40V100" stroke="#8d9097" stroke-width="1.2"/>' for k in range(12))}
      </g>
      {"".join(f'<path d="M590 {44 + k * 8}H650" stroke="#8d9097" stroke-width="1.2"/>' for k in range(8))}
    </g>
    <circle cx="610" cy="60" r="7" fill="#fff" opacity="0.7"><animate attributeName="opacity" values="0.2;0.9;0.2" dur="0.6s" repeatCount="indefinite"/></circle>
  </g>
  {rays}
  <!-- the stage and the DJ booth -->
  <rect x="300" y="250" width="420" height="50" fill="#2a2036" stroke="#111" stroke-width="2"/>
  <g id="dj-booth">
    <rect x="420" y="220" width="190" height="44" rx="4" fill="#1b1b1b" stroke="#111" stroke-width="2"/>
    <text x="515" y="252" font-family="{FONT}" font-size="14" fill="#ff4f79" text-anchor="middle" letter-spacing="3">DISCO FEVER</text>
    <rect x="428" y="210" width="76" height="12" rx="2" fill="#2a2a2a"/><rect x="526" y="210" width="76" height="12" rx="2" fill="#2a2a2a"/>
    <ellipse cx="466" cy="210" rx="26" ry="5" fill="#111"/><ellipse cx="564" cy="210" rx="26" ry="5" fill="#111"/>
  </g>
  <g id="dance-floor">{"".join(floor)}</g>
'''


def _crowd(jump=False, shrug=False):
    """The crowd at the front: silhouettes nodding (or jumping, at the legends' ending)."""
    people = []
    for k, x in enumerate(range(330, 800, 38)):
        c = CLUB_LIGHTS[k % len(CLUB_LIGHTS)]
        move = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-18 if jump else -4};0 0" '
                f'dur="{0.45 if jump else 0.5}s" begin="{(k % 4) * 0.1:.1f}s" repeatCount="indefinite"/>') if not shrug else ""
        arms = (f'<path d="M{x - 12} 402L{x - 20} 372M{x + 12} 402L{x + 20} 372" stroke="#0b0716" stroke-width="7" stroke-linecap="round"/>'
                if jump else "")
        people.append(f'<g>{move}{arms}<circle cx="{x}" cy="{392 + (k % 3) * 6}" r="14" fill="#0b0716"/>'
                      f'<rect x="{x - 18}" y="{404 + (k % 3) * 6}" width="36" height="50" rx="12" fill="#0b0716"/>'
                      f'<circle cx="{x}" cy="{392 + (k % 3) * 6}" r="14" fill="none" stroke="{c}" stroke-width="2" opacity="0.6"/></g>')
    return f'<g id="crowd">{"".join(people)}</g>'


# the front of the DJ booth again, drawn over the DJ so he stands behind his decks
BOOTH_FRONT = ('<rect x="420" y="220" width="190" height="100" rx="4" fill="#1b1b1b" stroke="#111" stroke-width="2"/>'
               f'<text x="515" y="252" font-family="{FONT}" font-size="14" fill="#ff4f79" text-anchor="middle" letter-spacing="3">DISCO FEVER</text>')


CLUB_DEFS = '''    <filter id="neonGlow" x="-20%" y="-40%" width="140%" height="180%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="ballClip"><circle cx="620" cy="70" r="30"/></clipPath>
'''


def battle_scene():
    """Disco Fever, battle night: the Sopranos are on the decks, King Krete sits on a speaker,
    the crowd waits. The crew comes in; Needle steps up. START THE BATTLE plays it out."""
    body = defs(DUSK, extra=CLUB_DEFS) + _club("#1a1028") + f'''
  <!-- a speaker stack on stage, King Krete sits on it -->
  <rect x="628" y="268" width="62" height="40" fill="#1b1b1b" stroke="#000" stroke-width="2"/>
  <circle cx="659" cy="288" r="13" fill="#2a2a2a" stroke="#000" stroke-width="2"/>
  <g transform="translate(1304 -34) scale(-1 1)">
{crew.king_krete(652, 302)}
  </g>
  <!-- a Soprano on the decks -->
  <g transform="translate(1030 -58) scale(-1 1)">
{crew.sopranos_member(515)}
  </g>
  {BOOTH_FRONT}<!-- (in front of him: he is behind his decks) -->
  <!-- the host -->
  <g transform="translate(0 -58)">
{crew.host(360)}
  </g>
  <!-- the crew has just come in; Needle steps up -->
{crew.portals(40, idle="still")}{crew.bible_either(98)}{crew.meyhem(156)}{crew.reekz_front(214)}{crew.needle(290, idle="still")}
{_crowd()}
  <!-- the battle -->
  <g data-action="start_battle" role="button" tabindex="0" aria-label="Start the battle">
    <title>Start the battle</title>
    <rect x="574" y="398" width="218" height="44" rx="9" fill="#111" stroke="#ff4f79" stroke-width="3" opacity="0.95"/>
    {piece(683, 429, "START THE BATTLE ▶", "gPinkYellow", size=26, rot=-2, anchor="middle", fit=190)}
  </g>
{_dialogue(SCENES["battle"]["dialogue"], BATTLE_SPEAKERS)}
'''
    return _svg(body, "scene-battle")


def _ending_panel(ending, grad, edge, button=("to_start", "BACK TO THE START", "Back to the start")):
    """The title of the ending, what happened, and the button back to the start (or RESTART)."""
    action, label, aria = button
    title = ENDINGS[ending]["title"].upper()
    rows = _wrap(ENDINGS[ending]["text"].upper().replace(chr(34), "&quot;"), 92)
    text = "".join(f'<text x="300" y="{394 + 15 * k}" font-family="{FONT}" font-size="11" fill="#f4f4f4" '
                   f'text-anchor="middle" letter-spacing="0.5">{row}</text>' for k, row in enumerate(rows))
    return f'''
  <!-- {title} -->
  <rect x="96" y="12" width="608" height="60" rx="12" fill="#111" opacity="0.8"/>
  {piece(400, 58, title, grad, size=44, rot=-2, anchor="middle", fit=560)}
  <rect x="8" y="378" width="584" height="{20 + 15 * len(rows)}" rx="10" fill="#111" stroke="{edge}" stroke-width="3" opacity="0.92"/>
  {text}
  <g data-action="{action}" role="button" tabindex="0" aria-label="{aria}">
    <title>{aria}</title>
    <rect x="602" y="400" width="190" height="42" rx="9" fill="#111" stroke="#f4f4f4" stroke-width="3"/>
    {piece(697, 430, label, "gWhite", size=22, rot=-2, anchor="middle", fit=168)}
  </g>
'''


def ending_legends():
    """The good ending: Needle cuts in "Think About It", Reekz goes down to the real break, Bible
    and Meyhem tear up the mic, Portals' backdrop pulls the room into another dimension."""
    rings = "".join(
        f'<circle cx="515" cy="170" r="{r}" fill="none" stroke="{c}" stroke-width="10" opacity="0.55">'
        f'<animate attributeName="r" values="{r};{r + 60};{r}" dur="3s" repeatCount="indefinite"/></circle>'
        for r, c in zip((30, 70, 110, 150, 190), CLUB_LIGHTS))
    confetti = "".join(
        f'<rect x="{x}" y="-10" width="6" height="10" fill="{CLUB_LIGHTS[k % 5]}">'
        f'<animate attributeName="y" values="-10;460" dur="{2 + (k % 4) * 0.5}s" begin="{(k % 7) * 0.3:.1f}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="rotate" values="0 {x} 0;360 {x} 0" dur="1.5s" repeatCount="indefinite"/></rect>'
        for k, x in enumerate(range(20, 800, 37)))
    body = defs(DUSK, extra=CLUB_DEFS) + _club("#2a0f3a", neon=False) + f'''
  <!-- Portals' backdrop: the room is pulled into another dimension -->
  <g id="portal-backdrop">
    <g><animateTransform attributeName="transform" type="rotate" values="0 515 170;360 515 170" dur="12s" repeatCount="indefinite"/>{rings}</g>
    {piece(515, 112, "PORTALS", "gPurple", size=30, rot=-6, anchor="middle", fit=170)}
  </g>
  <!-- Needle behind the decks, "Think About It" spinning -->
  {crew.needle(515, idle="nod").replace("translate(515 327)", "translate(515 250)")}
  {BOOTH_FRONT}
  <g id="spinning-record">
    {spinning_record(466, 210, 26, "#ff6fa8", tilt=0.23)}
    <rect x="410" y="276" width="112" height="18" rx="4" fill="#111"/>
    <text x="466" y="289" font-family="{FONT}" font-size="11" fill="#ff6fa8" text-anchor="middle" letter-spacing="1">THINK ABOUT IT</text>
  </g>
  <!-- Bible and Meyhem tear up the mic -->
{crew.bible(120, book=True, idle="nod")}{crew.meyhem(190, idle="nod")}{crew.portals(54, idle="nod")}
  <!-- Reekz goes down to the real break -->
{crew.reekz_breaking(320, 362)}
{_crowd(jump=True)}
  {confetti}
  {_ending_panel("ending_legends", "gGold", "#e0b84a")}
'''
    return _svg(body, "ending-legends")


def ending_static():
    """The bad ending: Needle plays the usual records, Reekz stays standing, the crowd shrugs,
    and the Sopranos Family take the crown."""
    noise = "".join(f'<rect x="0" y="{y}" width="800" height="2" fill="#f4f4f4" opacity="0.06">'
                    f'<animate attributeName="y" values="{y};{y + 40};{y}" dur="{1 + (y % 5) * 0.3:.1f}s" repeatCount="indefinite"/></rect>'
                    for y in range(10, 450, 34))
    body = defs(DUSK, extra=CLUB_DEFS) + _club("#15141a", floor_glow=False, neon=False) + f'''
  <rect width="800" height="450" fill="#3a3a42" opacity="0.45"/>
  <!-- the Sopranos take the crown -->
  {piece(515, 150, "SOPRANOS", "gSteel", size=36, rot=-4, shadow="#c0392b", anchor="middle", fit=220)}
  <text x="515" y="112" font-family="Arial, sans-serif" font-size="40" fill="#e0b84a" text-anchor="middle">♛</text>
  <!-- King Krete on the speaker stack, as on battle night -->
  <rect x="628" y="268" width="62" height="40" fill="#1b1b1b" stroke="#000" stroke-width="2"/>
  <circle cx="659" cy="288" r="13" fill="#2a2a2a" stroke="#000" stroke-width="2"/>
  <g transform="translate(1304 -34) scale(-1 1)">
{crew.king_krete(652, 302)}
  </g>
  <!-- Needle plays the usual records -->
  {crew.needle(515, idle="still").replace("translate(515 327)", "translate(515 250)")}
  {BOOTH_FRONT}
  <ellipse cx="466" cy="210" rx="26" ry="6" fill="#111"/>
  <!-- the crew, flat: Reekz stays standing -->
{crew.bible(120, book=False, idle="still")}{crew.meyhem(190, idle="still")}{crew.portals(54, idle="still")}{crew.reekz(270, idle="still", music=False)}
{_crowd(shrug=True)}
  <text x="640" y="372" font-family="{FONT}" font-size="22" fill="#9a9aa2">. . .</text>
  <!-- static -->
  {noise}
  {_ending_panel("ending_static", "gSteel", "#9a9aa2")}
'''
    return _svg(body, "ending-static")


def ending_lost_battle():
    """Game over after a lost rap battle: King Krete stands on his crate in the station, the record
    held up high, the Sopranos cheering, the crowd booing the GoodFellas. Why it was lost: Bible
    choked without his rhyme book ("lost-choked"), or went first ("lost-order"). RESTART starts
    a new game, from the story intro."""
    boos = "".join(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="#d02b2b" stroke="#111" stroke-width="1" '
                   f'transform="rotate({rot} {x} {y})">BOOO!<animate attributeName="opacity" values="1;0.2;1" dur="{d}s" repeatCount="indefinite"/></text>'
                   for x, y, size, rot, d in ((20, 150, 26, -8, 0.9), (110, 138, 20, 6, 1.1), (660, 140, 22, -5, 0.8), (722, 196, 20, 4, 1.3)))
    record = ('<g transform="translate(492 300) rotate(-10)"><rect x="-22" y="-22" width="44" height="44" fill="#ff6fa8" stroke="#111" stroke-width="2"/>'
              '<path d="M-22 -12H22M-22 8H22" stroke="#ffd23f" stroke-width="4"/>'
              f'<text x="0" y="3" font-family="{FONT}" font-size="10" fill="#111" text-anchor="middle">THINK</text>'
              '<animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="0.8s" repeatCount="indefinite" additive="sum"/></g>')
    reasons = {"lost-choked": CHOKED_MESSAGE, "lost-order": LOST_BATTLE_MESSAGE}
    why = "".join(
        f'<g data-overlay="{name}" style="display:none">'
        + "".join(f'<text x="400" y="{96 + 16 * k}" font-family="{FONT}" font-size="12" fill="#ffd23f" text-anchor="middle" letter-spacing="0.5">{row}</text>'
                  for k, row in enumerate(_wrap(text.upper().replace(chr(34), "&quot;"), 86)))
        + "</g>" for name, text in reasons.items())
    body = defs(DUSK, extra='''    <pattern id="tiles" width="22" height="11" patternUnits="userSpaceOnUse">
      <rect width="22" height="11" fill="#cfc8b8"/><path d="M0 0H22M0 0V11" stroke="#9e9786" stroke-width="1.5"/>
    </pattern>
''') + f'''
  <!-- the abandoned station, dark -->
  <rect width="800" height="304" fill="url(#tiles)"/>
  <rect width="800" height="304" fill="#0b0716" opacity="0.7"/>
  <rect y="304" width="800" height="9" fill="#e8c840"/><rect y="313" width="800" height="137" fill="#3e3c42"/>
  {_mosaic_sign(474, 150, 176, 56, "149 ST")}
  <!-- King Krete on his crate, the record held up high; the Sopranos cheer -->
  <rect x="490" y="334" width="62" height="44" fill="#8b5a2b" stroke="#3a2414" stroke-width="2"/>
  <g transform="translate(1042 0) scale(-1 1)">
{crew.king_krete(521, 334)}
  </g>
  {record}
  {crew.sopranos_member(640)}{crew.sopranos_member(700, bandana="#111")}
  <!-- the GoodFellas, heads down -->
{crew.bible(120, book=False, idle="still")}{crew.meyhem(180, idle="still")}{crew.needle(240, idle="still")}{crew.portals(60, idle="still")}{crew.reekz(300, idle="still", music=False)}
  <g id="crowd-boos">{boos}</g>
  <!-- GAME OVER, and why -->
  <rect x="190" y="160" width="270" height="56" rx="12" fill="#111" stroke="#d02b2b" stroke-width="3" opacity="0.92"/>
  {piece(325, 202, "GAME OVER", "gOrangeRed", size=40, rot=-3, anchor="middle", fit=240)}
  {why}
  {_ending_panel("ending_lost_battle", "gOrangeRed", "#d02b2b", button=("restart", "RESTART ↻", "Restart the game"))}
'''
    return _svg(body, "ending-lost-battle")


def ending_out_of_practice():
    """The plot twist ending: the crew has "Think About It", but Needle never practiced with it.
    He's on the decks with the record, the needle skips (SKRRT), the break stumbles, the crowd
    walks off the floor, and the Sopranos Family take the crown."""
    skip = "".join(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="#ff4f79" stroke="#111" stroke-width="1" '
                   f'transform="rotate({rot} {x} {y})" opacity="0">SKRRT—<animate attributeName="opacity" values="0;1;0" dur="1.1s" '
                   f'begin="{b}s" repeatCount="indefinite"/></text>' for x, y, size, rot, b in ((560, 150, 26, -8, 0), (620, 196, 20, 6, 0.55)))
    body = defs(DUSK, extra=CLUB_DEFS) + _club("#15141a", floor_glow=False, neon=False) + f'''
  <rect width="800" height="450" fill="#3a3a42" opacity="0.4"/>
  <!-- the Sopranos take the crown -->
  {piece(150, 120, "SOPRANOS", "gSteel", size=32, rot=-4, shadow="#c0392b", anchor="middle", fit=200)}
  <text x="150" y="84" font-family="Arial, sans-serif" font-size="34" fill="#e0b84a" text-anchor="middle">♛</text>
  <!-- Needle on the decks with the record: the break skips -->
  {crew.needle(515, idle="still").replace("translate(515 327)", "translate(515 250)")}
  {BOOTH_FRONT}
  <g transform="rotate(-8 466 206)">
    <ellipse cx="466" cy="210" rx="26" ry="6" fill="#111"/>
    <g transform="translate(442 160)"><rect width="38" height="38" fill="#ff6fa8" stroke="#111" stroke-width="2"/>
      <path d="M0 10H38M0 27H38" stroke="#ffd23f" stroke-width="4"/>
      <text x="19" y="22" font-family="{FONT}" font-size="9" fill="#111" text-anchor="middle">THINK</text></g>
  </g>
  {skip}
  <text x="640" y="130" font-family="{FONT}" font-size="26" fill="#9a9aa2" stroke="#111" stroke-width="1">?!</text>
  <!-- the crew can't believe it; Reekz stays standing -->
{crew.bible(120, book=True, idle="still")}{crew.meyhem(190, idle="still")}{crew.portals(54, idle="still")}{crew.reekz(270, idle="still", music=False)}
{_crowd(shrug=True)}
  {_ending_panel("ending_out_of_practice", "gOrangeRed", "#ff4f79")}
'''
    return _svg(body, "ending-out-of-practice")


INK_SIGN = "#1f2e6a"  # his signature, in the same pen


# MC Bible's rhyme book, page by page. Each page is a list of what is written on it:
#   ("title", text)    a heading, underlined twice
#   ("bar", n)         bar n of RHYME_BOOK_VERSE
#   ("crossed", text)  a draft he scribbled out
#   ("note", text, colour, dx, dy, rot)   a note in the margin (dx/dy from the page's top left)
#   ("doodle", kind, dx, dy)              a little drawing: crown, star, arrow
RHYME_PAGES = [
    [("title", "CRACKED CONCRETE"), ("note", "verse 1 – for Krete", "#c0392b", 120, 14, -3),
     ("bar", 0), ("bar", 1), ("crossed", "King Krete is weak, his rhymes are cheap"), ("bar", 2), ("bar", 3),
     ("doodle", "crown", 196, 300)],
    [("bar", 4), ("bar", 5), ("crossed", "You talk a lot but you never write"), ("bar", 6), ("bar", 7),
     ("note", "← save for round 2!!", "#c0392b", 96, 316, -3), ("doodle", "star", 236, 24), ("note", "Bible 1", "#2e8b57", 14, 330, -8)],
    [("bar", 8), ("bar", 9),
     ("crossed", "X marks the spot where you lost your crown"), ("bar", 10), ("bar", 11),
     ("note", "↑ Portals: draw the X here?", "#3d6fb6", 8, 316, -2), ("doodle", "star", 214, 330)],
    [("bar", 12), ("bar", 13), ("crossed", "Your whole crew is a joke"), ("bar", 14), ("bar", 15),
     ("note", "– MC Bible '77", INK_SIGN, 126, 268, -4),
     ("note", "Meyhem goes first, I finish him", "#c0392b", 22, 318, -2), ("note", "GOODFELLAS", "#2e8b57", 170, 24, 6)],
]
INK, PENCIL = "#1f2e6a", "#6a6f80"
PAGE_TEXT_W, ROW_H, HAND = 228, 23, 15


def _hand_rows(text, size=HAND, width=PAGE_TEXT_W):
    """Wrap handwriting into rows that fit the page (measured from the font)."""
    rows, row = [], ""
    for word in text.split():
        trial = f"{row} {word}".strip()
        if row and text_width(trial, size, "tag") > width:
            rows.append(row)
            row = word
        else:
            row = trial
    return rows + [row]


def _esc(text):
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def _page_writing(items, x0, y0):
    """What is written on one page, starting at its top left (x0, y0)."""
    out, y = [], y0 + 44
    for k, item in enumerate(items):
        kind = item[0]
        tilt = (-1.2, 0.8, -0.4, 1.0, -0.8)[k % 5]
        if kind == "title":
            w = text_width(item[1], 22, "tag")
            out.append(f'<g transform="rotate(-2 {x0} {y})"><text x="{x0}" y="{y}" font-family="{TAG_FONT}" font-size="22" fill="{INK}">{item[1]}</text>'
                       f'<path d="M{x0} {y + 5}H{x0 + w}M{x0 + 4} {y + 9}H{x0 + w - 6}" stroke="{INK}" stroke-width="1.6"/></g>')
            y += ROW_H + 14
        elif kind in ("bar", "crossed"):
            text = RHYME_BOOK_VERSE[item[1]] if kind == "bar" else item[1]
            rows = _hand_rows(text)
            colour = INK if kind == "bar" else PENCIL
            lines = "".join(f'<text x="{x0 + (14 if r else 0)}" y="{y + r * ROW_H}" font-family="{TAG_FONT}" font-size="{HAND}" '
                            f'fill="{colour}">{_esc(row)}</text>' for r, row in enumerate(rows))
            if kind == "bar":
                out.append(f'<g class="bar" aria-label="{_esc(text)}" transform="rotate({tilt} {x0} {y})">{lines}</g>')
            else:  # scribbled through
                scribble = "".join(
                    f'<path d="M{x0 + (14 if r else 0) - 2} {y + r * ROW_H - 5}'
                    + "".join(f"l{6} {(-3 if j % 2 else 3)}" for j in range(int(text_width(row, HAND, 'tag') / 6) + 1))
                    + f'" stroke="{INK}" stroke-width="1.6" fill="none"/>' for r, row in enumerate(rows))
                out.append(f'<g class="crossed" transform="rotate({tilt} {x0} {y})">{lines}{scribble}</g>')
            y += ROW_H * len(rows) + 6
        elif kind == "note":
            _, text, colour, dx, dy, rot = item
            out.append(f'<text class="margin-note" x="{x0 + dx}" y="{y0 + dy}" font-family="{TAG_FONT}" font-size="13" '
                       f'fill="{colour}" transform="rotate({rot} {x0 + dx} {y0 + dy})">{_esc(text)}</text>')
        elif kind == "doodle":
            _, what, dx, dy = item
            x, yy = x0 + dx, y0 + dy
            shape = {
                "crown": (f'<path d="M{x} {yy}L{x + 4} {yy - 18}L{x + 12} {yy - 8}L{x + 20} {yy - 22}L{x + 28} {yy - 8}L{x + 36} {yy - 18}L{x + 40} {yy}Z" '
                          f'fill="none" stroke="{INK}" stroke-width="1.8"/>'
                          f'<path d="M{x - 4} {yy - 26}L{x + 44} {yy + 4}M{x + 44} {yy - 26}L{x - 4} {yy + 4}" stroke="#c0392b" stroke-width="2.4"/>'),
                "star": star(x, yy, 9, "none").replace('stroke="#111"', f'stroke="{INK}"'),
                "arrow": f'<path d="M{x} {yy}Q{x + 20} {yy + 30} {x + 34} {yy + 44}M{x + 34} {yy + 44}l-10 -2M{x + 34} {yy + 44}l-2 -10" stroke="#3d6fb6" stroke-width="2" fill="none"/>',
            }[what]
            out.append(f'<g class="margin-note">{shape}</g>')
    return "".join(out)


def rhymebook_spread(n):
    """MC Bible's view of his open rhyme book: his hands hold it, two pages of handwriting
    (spread n of len(RHYME_PAGES) // 2), and a page that flips over when you get there."""
    spreads = len(RHYME_PAGES) // 2
    left, right = RHYME_PAGES[2 * (n - 1)], RHYME_PAGES[2 * (n - 1) + 1]
    ruled = "".join(f'<path d="M{x1} {y}H{x2}" stroke="#9fb7d8" stroke-width="1"/>'
                    for x1, x2 in ((104, 394), (406, 696)) for y in range(98, 400, ROW_H))
    paper_l = "118,42 394,54 394,410 98,402"
    paper_r = "406,54 682,42 702,402 406,410"
    turning = "6,54 282,42 302,402 6,410"  # the right page, seen from the spine
    coffee = ('<g id="coffee-ring" class="margin-note" opacity="0.35"><circle cx="640" cy="356" r="34" fill="none" stroke="#7a4a24" stroke-width="5"/>'
              '<circle cx="640" cy="356" r="30" fill="none" stroke="#7a4a24" stroke-width="1.5"/></g>') if n == 2 else ""
    prev_btn = (f'<g data-action="page_prev" role="button" tabindex="0" aria-label="Previous page"><title>Previous page</title>'
                f'<rect x="8" y="404" width="132" height="40" rx="9" fill="#111" stroke="#7ef0ff" stroke-width="3"/>'
                f'{piece(74, 433, "◀ PAGE", "gBlueGreen", size=22, rot=-2, anchor="middle", fit=110)}</g>') if n > 1 else ""
    next_btn = (f'<g data-action="page_next" role="button" tabindex="0" aria-label="Next page"><title>Next page</title>'
                f'<rect x="660" y="404" width="132" height="40" rx="9" fill="#111" stroke="#7ef0ff" stroke-width="3"/>'
                f'{piece(726, 433, "PAGE ▶", "gBlueGreen", size=22, rot=-2, anchor="middle", fit=110)}</g>') if n < spreads else ""
    sleeve = ("#161616", "#7a4a2e")
    hands = f'''<g id="bible-hands">
    <animateTransform attributeName="transform" type="translate" values="0 0;0 2;0 0" dur="3s" repeatCount="indefinite"/>
    <path d="M18 450L60 382L150 392L160 450Z" fill="{sleeve[0]}" stroke="#000" stroke-width="2"/>
    <path d="M66 388L146 396" stroke="#2e8b57" stroke-width="5"/>
    <ellipse cx="112" cy="398" rx="30" ry="18" fill="{sleeve[1]}" stroke="#111" stroke-width="1.5"/>
    <ellipse cx="136" cy="384" rx="16" ry="8" fill="{sleeve[1]}" stroke="#111" stroke-width="1.5" transform="rotate(-24 136 384)"/>
    <path d="M782 450L740 382L650 392L640 450Z" fill="{sleeve[0]}" stroke="#000" stroke-width="2"/>
    <path d="M734 388L654 396" stroke="#2e8b57" stroke-width="5"/>
    <ellipse cx="688" cy="398" rx="30" ry="18" fill="{sleeve[1]}" stroke="#111" stroke-width="1.5"/>
    <ellipse cx="664" cy="384" rx="16" ry="8" fill="{sleeve[1]}" stroke="#111" stroke-width="1.5" transform="rotate(24 664 384)"/>
  </g>'''
    extra = '''    <linearGradient id="spineShade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="0.5" stop-color="#000" stop-opacity="0.28"/>
      <stop offset="1" stop-color="#000" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="readGlow" cx="0.5" cy="0.1" r="0.8">
      <stop offset="0" stop-color="#ffe9a8" stop-opacity="0.25"/><stop offset="1" stop-color="#ffe9a8" stop-opacity="0"/>
    </radialGradient>
'''
    body = defs(DUSK, extra=extra) + f'''
  <!-- the basement, dark around the book -->
  <rect width="800" height="450" fill="#140f1e"/>
  <rect width="800" height="450" fill="url(#readGlow)"/>
  <!-- the open rhyme book -->
  <polygon points="96,30 400,44 704,30 724,416 400,430 76,416" fill="#5a2216" stroke="#2a0e08" stroke-width="3"/>
  <polygon points="{paper_l}" fill="#f4ecd2" stroke="#c9bd98" stroke-width="1.5"/>
  <polygon points="{paper_r}" fill="#f4ecd2" stroke="#c9bd98" stroke-width="1.5"/>
  {ruled}
  <path d="M146 50V404M432 54V406" stroke="#e8a0a0" stroke-width="1.2"/>
  <rect x="352" y="50" width="96" height="362" fill="url(#spineShade)"/>
  <path d="M400 54V410" stroke="#b8ad88" stroke-width="2"/>
  <text x="120" y="398" font-family="{TAG_FONT}" font-size="12" fill="{PENCIL}">{2 * n - 1}</text>
  <text x="676" y="398" font-family="{TAG_FONT}" font-size="12" fill="{PENCIL}">{2 * n}</text>
  <!-- his writing: it shows once the page has turned -->
  <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.45s" dur="0.3s" fill="freeze"/>
    {_page_writing(left, 152, 54)}
    {_page_writing(right, 440, 54)}
    {coffee}
  </g>
  <!-- the page turning over the spine -->
  <g id="page-turn"><set attributeName="visibility" to="hidden" begin="0.7s"/>
    <g transform="translate(400 0)"><g>
      <animateTransform attributeName="transform" type="scale" values="1 1;0.02 1;-1 1" dur="0.7s" fill="freeze"/>
      <polygon points="{turning}" fill="#efe6c8" stroke="#c9bd98" stroke-width="1.5"/>
      <rect x="6" y="50" width="60" height="360" fill="url(#spineShade)"/>
    </g></g>
  </g>
  {hands}
  <!-- turning the pages, closing the book -->
  <g data-action="close_book" role="button" tabindex="0" aria-label="Close the book"><title>Close the book</title>
    <rect x="8" y="8" width="168" height="40" rx="9" fill="#111" stroke="#ffd23f" stroke-width="3"/>
    {piece(92, 37, "CLOSE BOOK", "gGold", size=22, rot=-2, anchor="middle", fit=146)}
  </g>
  {prev_btn}{next_btn}
  <text x="400" y="446" font-family="{FONT}" font-size="11" fill="#9a9aa2" text-anchor="middle" letter-spacing="2">{n} / {spreads}</text>
'''
    return _svg(body, f"rhymebook-{n}")


# --- the Grandmaster Flash layer: his realm, Portals' portal there and back, the corner store, the crayon ---

FLASH_X = 560  # where Grandmaster Flash stands behind his floating decks
FLASH_SPEAKERS = {
    "flash": ("GRANDMASTER FLASH", "#e0b84a", (FLASH_X, 214)),
    "needle": ("FANTASTIC NEEDLE", "#d02b2b", (300, 238)),
    "portals": ("PORTALS", "#3d6fb6", (120, 236)),
    "reekz": ("REEKZ", "#c0392b", (360, 236)),
}
STORE_SPEAKERS = {"clerk": ("THE CLERK", "#2e8b57", (612, 200))}
FLASH_DEFS = '''    <radialGradient id="nebula" cx="0.6" cy="0.35" r="0.8"><stop offset="0" stop-color="#5b2a9a"/>
      <stop offset="0.5" stop-color="#1f1238"/><stop offset="1" stop-color="#07051a"/></radialGradient>
    <radialGradient id="haloGlow"><stop offset="0" stop-color="#fff4c4" stop-opacity="0.9"/>
      <stop offset="0.45" stop-color="#e0b84a" stop-opacity="0.45"/><stop offset="1" stop-color="#e0b84a" stop-opacity="0"/></radialGradient>
    <radialGradient id="portalGlow"><stop offset="0.55" stop-color="#7ef0ff" stop-opacity="0.8"/><stop offset="1" stop-color="#c58bff" stop-opacity="0"/></radialGradient>
    <radialGradient id="portalDepth"><stop offset="0" stop-color="#f4feff"/><stop offset="0.25" stop-color="#7ef0ff"/>
      <stop offset="0.6" stop-color="#5b2a9a"/><stop offset="1" stop-color="#0b0716"/></radialGradient>
    <linearGradient id="beamUp" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#7ef0ff" stop-opacity="0.55"/><stop offset="1" stop-color="#c58bff" stop-opacity="0"/></linearGradient>
    <linearGradient id="beamDown" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7ef0ff" stop-opacity="0.55"/><stop offset="1" stop-color="#c58bff" stop-opacity="0"/></linearGradient>
'''


def _flash_realm():
    """Somewhere between the stars and the grooves: a starry nebula, a giant record turning
    as the floor, records floating round in orbit, a golden halo where Flash stands."""
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f4f4f4" opacity="0.8">'
                    f'<animate attributeName="opacity" values="0.9;0.2;0.9" dur="{d}s" repeatCount="indefinite"/></circle>'
                    for x, y, r, d in ((40, 40, 1.5, 2.1), (130, 90, 1.2, 3.0), (220, 30, 1.8, 2.6), (330, 70, 1.1, 1.9),
                                       (420, 24, 1.5, 2.8), (690, 40, 1.4, 2.3), (760, 110, 1.6, 3.3), (610, 150, 1.0, 2.4),
                                       (80, 170, 1.2, 2.7), (480, 120, 1.0, 2.2), (300, 160, 1.3, 3.1)))
    grooves = "".join(f'<ellipse cx="400" cy="380" rx="{r}" ry="{r * 0.22:.1f}" fill="none" stroke="#2a2a2a" stroke-width="2"/>'
                      for r in range(80, 380, 26))
    shine = ('<g><animateTransform attributeName="transform" type="translate" values="-500 0;500 0" dur="3.5s" repeatCount="indefinite"/>'
             '<path d="M380 300L420 300L460 460L340 460Z" fill="#f4f4f4" opacity="0.07"/></g>')
    orbits = "".join(
        f'<g><animateMotion dur="{d}s" repeatCount="indefinite" rotate="0" path="M{cx - rx} {cy}a{rx} {ry} 0 1 0 {2 * rx} 0a{rx} {ry} 0 1 0 {-2 * rx} 0" begin="{b}s"/>'
        f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="2s" repeatCount="indefinite"/>'
        f'<circle r="{size}" fill="#111" stroke="#3a3a3a" stroke-width="1.5"/><circle r="{size * 0.35:.1f}" fill="{c}"/></g></g>'
        for cx, cy, rx, ry, d, b, size, c in ((FLASH_X, 220, 150, 44, 9, 0, 16, "#ff4f79"), (FLASH_X, 220, 150, 44, 9, -4.5, 13, "#7ef0ff"),
                                              (FLASH_X, 190, 210, 60, 14, -2, 11, "#ffd23f"), (FLASH_X, 190, 210, 60, 14, -9, 14, "#7ed957")))
    return f'''
  <g id="flash-realm">
    <rect width="800" height="450" fill="url(#nebula)"/>
    {stars}
    <!-- a giant record as the floor, turning -->
    <g id="spinning-floor">
      <ellipse cx="400" cy="380" rx="400" ry="92" fill="#111"/>
      {grooves}
      <ellipse cx="400" cy="380" rx="70" ry="16" fill="#e0b84a"/><ellipse cx="400" cy="380" rx="8" ry="2" fill="#111"/>
      <g clip-path="url(#floorClip)">{shine}</g>
    </g>
    <!-- Flash's halo -->
    <g id="halo">
      <circle cx="{FLASH_X}" cy="230" r="120" fill="url(#haloGlow)">
        <animate attributeName="r" values="110;130;110" dur="3s" repeatCount="indefinite"/></circle>
      <circle cx="{FLASH_X}" cy="230" r="96" fill="none" stroke="#fff4c4" stroke-width="2" stroke-dasharray="4 10" opacity="0.7">
        <animateTransform attributeName="transform" type="rotate" from="0 {FLASH_X} 230" to="360 {FLASH_X} 230" dur="20s" repeatCount="indefinite"/></circle>
    </g>
    <g id="floating-records">{orbits}</g>
  </g>
  <!-- end flash-realm -->'''


def _flash_decks():
    """Flash's decks on a booth floating just above the record: two turntables and a mixer, the
    booth's gold-edged front panel (it hides his legs) with a glowing record on it."""
    return f'''<g id="flash-decks">
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="3s" repeatCount="indefinite"/>
    <path d="M{FLASH_X - 96} 318H{FLASH_X + 96}L{FLASH_X + 84} 382H{FLASH_X - 84}Z" fill="#1b1430" stroke="#e0b84a" stroke-width="2"/>
    <path d="M{FLASH_X - 88} 330H{FLASH_X + 88}" stroke="#e0b84a" stroke-width="1" opacity="0.5"/>
    <circle cx="{FLASH_X}" cy="346" r="14" fill="#111" stroke="#e0b84a" stroke-width="1.5"/><circle cx="{FLASH_X}" cy="346" r="5" fill="#e0b84a">
      <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite"/></circle>
    <text x="{FLASH_X - 50}" y="352" font-family="{FONT}" font-size="12" fill="#e0b84a" text-anchor="middle" letter-spacing="2">GRAND</text>
    <text x="{FLASH_X + 52}" y="352" font-family="{FONT}" font-size="12" fill="#e0b84a" text-anchor="middle" letter-spacing="2">MASTER</text>
    <path d="M{FLASH_X - 110} 300H{FLASH_X + 110}L{FLASH_X + 96} 322H{FLASH_X - 96}Z" fill="#2a2a2a" stroke="#e0b84a" stroke-width="2"/>
    <ellipse cx="{FLASH_X - 58}" cy="300" rx="40" ry="9" fill="#111" stroke="#555" stroke-width="1.5"/>
    <ellipse cx="{FLASH_X + 58}" cy="300" rx="40" ry="9" fill="#111" stroke="#555" stroke-width="1.5"/>
    <rect x="{FLASH_X - 12}" y="292" width="24" height="10" rx="2" fill="#3a3a3a"/>
    <ellipse cx="{FLASH_X}" cy="380" rx="90" ry="8" fill="#7ef0ff" opacity="0.25"><animate attributeName="opacity" values="0.15;0.35;0.15" dur="3s" repeatCount="indefinite"/></ellipse>
  </g>'''


def _flash_crew():
    """The crew, just through the portal, at the edge of the realm."""
    return (f'{crew.portals_front(120, idle="still")}<g data-overlay="lacks-rhyme_book" style="display:none">{crew.bible(190, book=False, idle="still")}</g>'
            f'<g data-overlay="has-rhyme_book" style="display:none">{crew.bible(190, book=True, idle="still")}</g>'
            f'{crew.meyhem(245, idle="still")}{crew.needle(300, idle="still")}{crew.reekz(360, idle="still", music=False)}')


def flash_scene():
    """Grandmaster Flash's realm (flash), through Portals' portal: the guru behind his floating
    decks, in a golden halo, records floating round him on a turning record floor. The crew at the
    edge, the portal still open behind them. His advice: the secret lies in the crayon."""
    body = defs(DUSK, extra=FLASH_DEFS + '    <clipPath id="floorClip"><ellipse cx="400" cy="380" rx="400" ry="92"/></clipPath>\n') + _flash_realm() + f'''
  <!-- the portal they came through, still open -->
  {_portal("back-portal", 40, 250, 34, 78, 0.0, beam=False)}
{crew.grandmaster_flash(FLASH_X)}
  {_flash_decks()}
{_flash_crew()}
  <!-- back through the portal, to the basement -->
  {_way_out("go_hq", "◀ THROUGH THE PORTAL", 8, "gBlueGreen", "#7ef0ff")}
{_dialogue(SCENES["flash"]["dialogue"], FLASH_SPEAKERS)}
'''
    return _svg(body, "scene-flash")


def _camera_dive(cx, cy, start, secs, zoom=7):
    """The camera dives into (cx, cy): it moves to the middle and fills the picture."""
    ease = 'calcMode="spline" keyTimes="0;1" keySplines="0.55 0 0.85 1"'
    return (f'<animateTransform attributeName="transform" type="translate" values="0 0;{400 - zoom * cx} {225 - zoom * cy}" '
            f'begin="{start}s" dur="{secs}s" fill="freeze" {ease}/>'
            f'<animateTransform attributeName="transform" type="scale" values="1;{zoom}" begin="{start}s" dur="{secs}s" '
            f'fill="freeze" additive="sum" {ease}/>')


def walk_hq_to_flash():
    """Portals opens the portal: in the basement he sprays a ring on the wall of his graffiti
    corner, it opens into a swirling portal, and the camera dives through it, to Flash."""
    cx, cy, rx, ry = 736, 196, 42, 92
    ring = 2 * math.pi * math.sqrt((rx * rx + ry * ry) / 2)
    room_defs, room = _basement_room(still=True, later=True)  # after the rap battle: the book and the record are back
    spraying = f'<g visibility="visible"><set attributeName="visibility" to="hidden" begin="2.6s"/>{crew.portals(650, None, spraying=True, idle="still")}</g>'
    body = defs(DUSK, extra=room_defs + FLASH_DEFS) + f'''
  <g id="camera">
    {_camera_dive(cx, cy, 3.0, 1.3)}
    {room}
    <!-- Portals sprays a ring on the wall of his corner ... -->
    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="url(#gPinkYellow)" stroke-width="10"
             stroke-dasharray="{ring:.0f}" stroke-dashoffset="{ring:.0f}">
      <animate attributeName="stroke-dashoffset" from="{ring:.0f}" to="0" begin="0.3s" dur="1.6s" fill="freeze"/></ellipse>
    <!-- ... and it opens: a portal to Grandmaster Flash -->
    {_portal("flash-portal", cx, cy, rx, ry, 1.9, beam=False)}
    {spraying}
    <g visibility="hidden"><set attributeName="visibility" to="visible" begin="2.6s"/>{crew.portals(650, idle="still")}</g>
  </g>
  <!-- end camera -->
  <rect width="800" height="450" fill="#07051a" opacity="0"><animate attributeName="opacity" values="0;1" begin="4.0s" dur="0.4s" fill="freeze"/></rect>
  <g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" dur="3s" fill="freeze"/>
    <rect x="16" y="12" width="360" height="40" rx="8" fill="#111" opacity="0.85"/>
    <text x="196" y="39" font-family="{FONT}" font-size="18" fill="#7ef0ff" text-anchor="middle" letter-spacing="1">PORTALS OPENS THE WAY TO FLASH</text></g>
''' + _skip_walk()
    return _svg(body, "walk-hq-flash", end="4.5", auto=("enter", 4.5))


def walk_flash_to_hq():
    """Back from Flash: the portal swirls at the edge of his realm and the camera dives into it,
    back to the basement. It goes on by itself."""
    cx, cy, rx, ry = 40, 250, 34, 78
    body = defs(DUSK, extra=FLASH_DEFS + '    <clipPath id="floorClip"><ellipse cx="400" cy="380" rx="400" ry="92"/></clipPath>\n') + f'''
  <g id="camera">
    {_camera_dive(cx, cy, 0.6, 1.3)}
    {_flash_realm()}
    {_portal("back-portal", cx, cy, rx, ry, 0.0, beam=False)}
{crew.grandmaster_flash(FLASH_X)}
    {_flash_decks()}
  </g>
  <!-- end camera -->
  <rect width="800" height="450" fill="#07051a" opacity="0"><animate attributeName="opacity" values="0;1" begin="1.6s" dur="0.4s" fill="freeze"/></rect>
''' + _skip_walk()
    return _svg(body, "walk-flash-hq", end="2.1", auto=("enter", 2.1))


STORE_GOODS = [  # what's for sale: (item, what it says on the price tag, price, x of its shelf spot)
    ("crayons", "CRAYONS", "$1.00", 470),
    ("chips", "CHIPS", "50¢", 170),
    ("soda", "SODA", "25¢", 262),
    ("candy", "CANDY", "10¢", 354),
]


def _good(item, x):
    """What an item looks like on the shelf."""
    if item == "crayons":
        sticks = "".join(f'<rect x="{x + 8 + 9 * k}" y="226" width="7" height="22" rx="2" fill="{c}" stroke="#111" stroke-width="1"/>'
                         for k, c in enumerate(("#d02b2b", "#ffd23f", "#3fa9f5", "#7ed957", "#c58bff", "#ff8a3d")))
        return (sticks + f'<rect x="{x}" y="238" width="68" height="40" rx="3" fill="#ffd23f" stroke="#111" stroke-width="2"/>'
                f'<text x="{x + 34}" y="262" font-family="{FONT}" font-size="12" fill="#2e8b57" text-anchor="middle">CRAYONS</text>')
    if item == "chips":
        return (f'<path d="M{x} 278L{x + 6} 228H{x + 62}L{x + 68} 278Z" fill="#e8a33a" stroke="#111" stroke-width="2"/>'
                f'<text x="{x + 34}" y="258" font-family="{FONT}" font-size="13" fill="#c0392b" text-anchor="middle">CHIPS</text>')
    if item == "soda":
        return "".join(f'<rect x="{x + 6 + 22 * k}" y="234" width="18" height="44" rx="5" fill="{c}" stroke="#111" stroke-width="2"/>'
                       f'<rect x="{x + 9 + 22 * k}" y="246" width="12" height="12" fill="#f4f4f4"/>'
                       for k, c in enumerate(("#d02b2b", "#2e8b57", "#3fa9f5")))
    return "".join(f'<rect x="{x + 4 + 20 * k}" y="{252 - 8 * (k % 2)}" width="16" height="26" rx="4" fill="{c}" stroke="#111" stroke-width="1.5"/>'
                   for k, c in enumerate(("#ff4f79", "#ffd23f", "#c58bff")))


def corner_store_scene():
    """Inside the CORNER STORE (corner_store): shelves of cans, boxes and bottles, the counter with
    the clerk behind it, and what the crew can buy: crayons, chips, soda, candy. Without money,
    nothing (the rules say so); what's bought is gone from the shelf."""
    shelf_stuff = "".join(f'<rect x="{x}" y="{y}" width="16" height="22" rx="2" fill="{c}" stroke="#111" stroke-width="1"/>'
                          for y in (70, 132) for x, c in zip(range(30, 762, 22), ("#d02b2b", "#ffd23f", "#3fa9f5", "#7ed957", "#ff8a3d", "#f4f4f4", "#c58bff") * 6))
    goods = "".join(
        f'<g data-overlay="offer-buy_{item}" style="display:none"><g data-action="buy_{item}" role="button" tabindex="0" aria-label="Buy {label.lower()} ({price})">'
        f'<title>{label} {price}</title>{_good(item, x)}'
        f'<rect x="{x + 2}" y="284" width="64" height="26" rx="5" fill="#111" stroke="#ffd23f" stroke-width="2"/>'
        f'<text x="{x + 34}" y="302" font-family="{FONT}" font-size="15" fill="#ffd23f" text-anchor="middle">{price}</text></g></g>'
        for item, label, price, x in STORE_GOODS)
    messages = "".join(_message_sign(f"done-buy_{item}", f"{label}!", next(a["message"] for a in SCENES["corner_store"]["actions"] if a["id"] == f"buy_{item}"),
                                     "#ffd23f", "gPinkYellow") for item, label, _, _ in STORE_GOODS)
    no_money = "".join(_message_sign(f"rejected-buy_{item}", "NO MONEY, NO DEAL", NO_MONEY_MESSAGE, "#d02b2b", "gOrangeRed", end="end rejected")
                       for item, _, _, _ in STORE_GOODS)
    body = defs(DUSK) + f'''
  <!-- the corner store, inside -->
  <rect width="800" height="450" fill="#e8d7ad"/>
  <rect y="200" width="800" height="100" fill="#f2e6c8"/>
  <!-- the linoleum floor, black and white -->
  <rect y="300" width="800" height="150" fill="#d9d2c0"/>
  {"".join(f'<rect x="{x}" y="{y}" width="30" height="30" fill="#3a3a42" opacity="0.55"/>' for y in range(300, 450, 30) for x in range(30 * ((y // 30) % 2), 800, 60))}
  <path d="M0 300H800" stroke="#8b7a5a" stroke-width="3"/>
  <g id="shelves">
    <rect x="20" y="92" width="760" height="8" fill="#8b5a2b"/><rect x="20" y="154" width="760" height="8" fill="#8b5a2b"/>
    {shelf_stuff}
  </g>
  {tag(640, 186, "Needle", "#d02b2b", 14, -4)}
  <!-- the counter, and the clerk behind it -->
<g transform="translate(0 -34)">{crew.store_clerk(620)}</g>
  <rect x="440" y="300" width="360" height="150" fill="#8b5a2b" stroke="#3a2414" stroke-width="3"/>
  <path d="M500 316V450M560 316V450M620 316V450M680 316V450M740 316V450" stroke="#6e4520" stroke-width="3"/>
  <rect x="440" y="300" width="360" height="16" fill="#a0522d"/>
  <!-- stickers on the counter: lotto, and a gum rack on top -->
  <rect x="452" y="326" width="40" height="22" rx="3" fill="#ffd23f" stroke="#111" stroke-width="1.5" transform="rotate(-4 472 337)"/>
  <text x="472" y="342" font-family="{FONT}" font-size="11" fill="#c0392b" text-anchor="middle" transform="rotate(-4 472 337)">LOTTO</text>
  <rect x="764" y="276" width="30" height="26" fill="#c9ccd2" stroke="#111" stroke-width="1.5"/>
  {"".join(f'<rect x="{767 + 9 * k}" y="{280 + 11 * r}" width="6" height="8" fill="{c}"/>' for r in range(2) for k, c in enumerate(("#ff4f79", "#7ed957", "#3fa9f5")))}
  <rect x="700" y="268" width="60" height="34" rx="4" fill="#3a3a42" stroke="#111" stroke-width="2"/>
  <text x="730" y="290" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#7ed957" text-anchor="middle">CASH</text>
  <!-- what's for sale, at the front -->
  <rect x="160" y="280" width="270" height="30" fill="#a0522d"/>
  {goods}
  <!-- the crew: Portals and Reekz in the door, the others up at the counter -->
{crew.portals(40, idle="still")}{crew.reekz_front(100, idle="still", music=False)}
  <g transform="translate(0 62)">{crew.meyhem(520, idle="still")}{crew.needle(590, idle="still")}{crew.bible_either(660)}</g>
  {_way_out("go_block", "◀ BACK TO THE BLOCK", 8, "gBlueGreen", "#7ef0ff")}
{_dialogue(SCENES["corner_store"]["dialogue"], STORE_SPEAKERS)}
  {messages}
  {no_money}
'''
    return _svg(body, "scene-corner-store")


CRAYON_LOOP = SONGS["think_about_it_break"]["loop_secs"]  # one round of the crayon: one loop of the drum break
CRAYON_WINDOW = 0.45  # MARK counts in the last this many seconds, right as the break is over
CRAYON_DECKS = ((200, 212), (600, 212))  # the two turntables, seen from above
MARKING_SECS = 1.5  # his hand stops the record, draws the mark, lets it go
LET_GO = 1.15  # (when the record turns again)


def _crayon_record(cx, cy, state, marked, trigger=None):
    """A copy of "Think About It" on its turntable, from above. state: "spin" (turning with the
    beat), "still" (cued up, not turning) or "marking" (caught by his hand, turning again when he
    lets go); marked: the crayon mark on it, where the break starts (at the top, under the needle)."""
    grooves = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2a2a2a" stroke-width="1.2"/>' for r in range(46, 108, 7))
    spin = f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="1.8s" repeatCount="indefinite"{{begin}}/>'
    if state == "spin":
        turn = spin.format(begin="")
    elif state == "marking":  # it slows to a stop under his hand ... and turns again when he lets go
        turn = (f'<animateTransform attributeName="transform" type="rotate" values="-50 {cx} {cy};0 {cx} {cy}" keyTimes="0;1" '
                f'calcMode="spline" keySplines="0.2 0.8 0.4 1" dur="0.3s" begin="{trigger}.begin" fill="freeze"/>'
                + spin.format(begin=f' begin="{trigger}.begin+{LET_GO}s" additive="replace"'))
    else:
        turn = ""
    mark = ""
    if marked:
        mark = f'<path class="crayon-line" d="M{cx} {cy - 44}V{cy - 100}" stroke="#ffd23f" stroke-width="6" stroke-linecap="round"/>'
    if state == "marking":  # drawn while you watch
        mark = (f'<path class="crayon-line" d="M{cx} {cy - 44}V{cy - 100}" stroke="#ffd23f" stroke-width="6" stroke-linecap="round" '
                f'stroke-dasharray="56" stroke-dashoffset="56"><animate attributeName="stroke-dashoffset" from="56" to="0" '
                f'begin="{trigger}.begin+0.45s" dur="0.45s" fill="freeze"/></path>')
    return f'''<g class="deck">
    <rect x="{cx - 130}" y="{cy - 130}" width="260" height="260" rx="14" fill="#c9ccd2" stroke="#111" stroke-width="3"/>
    <rect x="{cx - 130}" y="{cy - 130}" width="260" height="12" rx="6" fill="#fff" opacity="0.35"/>
    <circle cx="{cx}" cy="{cy}" r="116" fill="#2a2a2a" stroke="#111" stroke-width="2"/>
    <g>{turn}
      <circle cx="{cx}" cy="{cy}" r="108" fill="#111"/>{grooves}
      <path d="M{cx - 76} {cy - 76}A108 108 0 0 1 {cx} {cy - 108}" stroke="#4a4a4a" stroke-width="5" fill="none"/>
      <circle cx="{cx}" cy="{cy}" r="38" fill="{THINK_COLOUR}" stroke="#111" stroke-width="1.5"/>
      <text x="{cx}" y="{cy - 3}" font-family="{FONT}" font-size="13" fill="#111" text-anchor="middle">THINK</text>
      <text x="{cx}" y="{cy + 10}" font-family="Arial, sans-serif" font-size="7" font-weight="bold" fill="#111" text-anchor="middle">LYN COLLINS</text>
      {mark}
    </g>
    <circle cx="{cx}" cy="{cy}" r="4" fill="#e8e8e8" stroke="#111"/>
    <!-- the tone arm, its needle on the record at the top -->
    <circle cx="{cx + 104}" cy="{cy - 104}" r="12" fill="#8d9097" stroke="#111" stroke-width="2"/>
    <path d="M{cx + 104} {cy - 104}L{cx + 96} {cy - 30}L{cx + 22} {cy - 92}" stroke="#e8e8e8" stroke-width="6" fill="none" stroke-linejoin="round"/>
    <rect x="{cx + 10}" y="{cy - 100}" width="16" height="10" rx="2" fill="#555" transform="rotate(-30 {cx + 18} {cy - 95})"/>
  </g>'''


def _needle_hand(cx, cy, trigger):
    """Needle's hand (his yellow sleeve) with a crayon: in from the bottom, onto the record to stop
    it, the crayon along the groove where the break starts, and away again."""
    off, start, end = (cx + 170, cy + 300), (cx + 2, cy - 44), (cx + 2, cy - 100)
    path = ";".join(f"{x} {y}" for x, y in (off, start, start, end, end, off))
    return f'''<g id="needle-hand"><g transform="translate({off[0]} {off[1]})">
    <animateTransform attributeName="transform" type="translate" values="{path}" keyTimes="0;0.22;0.3;0.6;0.7;1" dur="{LET_GO + 0.2:.2f}s" begin="{trigger}.begin" fill="freeze"/>
    <path d="M14 14L150 250" stroke="#4a2e1c" stroke-width="22" stroke-linecap="round"/>
    <path d="M110 180L170 290" stroke="#f2c230" stroke-width="34" stroke-linecap="round"/>
    <path d="M106 172L124 204" stroke="#c99a1c" stroke-width="4"/>
    <circle cx="16" cy="18" r="17" fill="#4a2e1c"/><circle cx="4" cy="8" r="6" fill="#4a2e1c"/>
    <g class="crayon" transform="rotate(-28)"><rect x="-5" y="-2" width="10" height="40" rx="2" fill="#ffd23f" stroke="#111" stroke-width="1.5"/>
      <rect x="-5" y="10" width="10" height="16" fill="#f4f4f4" opacity="0.8"/><path d="M-5 -2L0 -12L5 -2Z" fill="#ffd23f" stroke="#111" stroke-width="1.5"/></g>
    <path d="M28 4Q36 14 30 26" stroke="#000" stroke-width="1.5" opacity="0.3" fill="none"/>
  </g></g>'''


def _crossfader(at_right, slide_at=None, trigger=None):
    x0, x1 = 362, 418
    x = x1 if at_right else x0
    move = ("" if slide_at is None else
            f'<animate attributeName="x" values="{x0};{x1}" begin="{trigger}.begin+{slide_at}s" dur="0.3s" fill="freeze"/>')
    return f'<rect x="{x}" y="292" width="20" height="24" rx="4" fill="#e8e8e8" stroke="#111" stroke-width="2">{move}</rect>'


def _loop_bar(cx):
    """How far the break is, under the deck that plays it; the green: MARK now."""
    w = 220
    return (f'<rect x="{cx - w / 2}" y="352" width="{w}" height="18" rx="6" fill="#111" stroke="#f4f4f4" stroke-width="2"/>'
            f'<rect x="{cx - w / 2 + w * (1 - CRAYON_WINDOW / CRAYON_LOOP):.1f}" y="352" width="{w * CRAYON_WINDOW / CRAYON_LOOP:.1f}" height="18" rx="4" fill="#7ed957" opacity="0.5"/>'
            f'<rect x="{cx - w / 2 + 2}" y="354" width="0" height="14" rx="5" fill="#7ef0ff"><animate attributeName="width" from="0" to="{w - 4}" dur="{CRAYON_LOOP:.3f}s" fill="freeze"/></rect>'
            f'<text x="{cx}" y="386" font-family="{FONT}" font-size="11" fill="#f4f4f4" text-anchor="middle" letter-spacing="1">THE BREAK → MARK AT THE END</text>')


def _deck_label(cx, text, colour):
    return f'<text x="{cx}" y="72" font-family="{FONT}" font-size="14" fill="{colour}" text-anchor="middle" letter-spacing="2">{text}</text>'


def crayon_screen():
    """Grandmaster Flash's secret: both turntables from above, a copy of "Think About It" on each,
    the break playing on one. MARK right when the break is over (the page judges it: mark_hit in
    the last CRAYON_WINDOW seconds, mark_miss before, and mark_miss if he doesn't; it stops the
    beat right then: data-pause-on). Needle's hand comes in, stops the record, draws the crayon
    mark where the break starts and lets it go (mark_done after MARKING_SECS): the beat goes on,
    from the other copy. One mark on each copy and he sees it."""
    (c1, y1), (c2, y2) = CRAYON_DECKS
    playing, cued, marked = ("▶ THE BREAK", "#7ed957"), ("CUED UP", "#ffd23f"), ("✎ MARKED", "#ffd23f")

    def marking(k):
        cx, cy = CRAYON_DECKS[k - 1]
        other = CRAYON_DECKS[2 - k]
        trigger = f"markGo{k}"
        return (f'<g data-overlay="marks-{k} marking" data-auto-action="mark_done" data-auto-delay="{MARKING_SECS:.2f}" style="display:none" id="marking-{k}">'
                f'<animate id="{trigger}" attributeName="opacity" from="1" to="1" dur="0.1s" begin="indefinite"/>'
                + _crayon_record(*other, "spin" if k == 2 else "still", marked=k == 2)
                + _crayon_record(cx, cy, "marking", marked=False, trigger=trigger)
                + _crossfader(k == 2, slide_at=None if k == 2 else LET_GO, trigger=trigger)
                + _deck_label(cx, "✎ MARKING...", "#ffd23f") + _deck_label(other[0], *(marked if k == 2 else cued))
                + _needle_hand(cx, cy, trigger)
                + f'</g>\n  <!-- end marking-{k} -->')
    states = (
        f'<g data-overlay="marks-0 !marking" style="display:none">{_crayon_record(c1, y1, "spin", False)}{_crayon_record(c2, y2, "still", False)}'
        f'{_crossfader(False)}{_deck_label(c1, *playing)}{_deck_label(c2, *cued)}{_loop_bar(c1)}</g>'
        f'<g data-overlay="marks-1 !marking" style="display:none">{_crayon_record(c1, y1, "spin", True)}{_crayon_record(c2, y2, "spin", False)}'
        f'{_crossfader(True)}{_deck_label(c1, *marked)}{_deck_label(c2, *playing)}{_loop_bar(c2)}</g>'
        + marking(1) + marking(2))
    counter = "".join(f'<g data-overlay="marks-{n}" style="display:none">'
                      + "".join(f'<rect x="{716 + 24 * k}" y="16" width="16" height="22" rx="3" fill="{"#ffd23f" if k < n else "#2a2a2a"}" stroke="#f4f4f4" stroke-width="1.5"/>' for k in range(2))
                      + '</g>' for n in range(3))
    button = lambda action, glow: (
        f'<g data-defer="1" data-action="{action}" role="button" tabindex="0" aria-label="Mark the break with the crayon"><title>Mark</title>'
        f'<rect x="300" y="392" width="200" height="50" rx="12" fill="{"#2e8b57" if glow else "#111"}" stroke="{"#7ed957" if glow else "#ffd23f"}" stroke-width="4"/>'
        f'{piece(400, 428, "✎ MARK", "gPinkYellow", size=26, rot=-2, anchor="middle", fit=170)}</g>')
    window = CRAYON_LOOP - CRAYON_WINDOW
    body = defs(DUSK) + f'''
  <!-- the DJ table from above: two turntables, the mixer between them -->
  <rect width="800" height="450" fill="#3a2414"/>
  <path d="M0 60H800M0 150H800M0 240H800M0 330H800M0 420H800" stroke="#2c1a0e" stroke-width="3"/>
  <rect x="340" y="110" width="120" height="216" rx="10" fill="#2a2a2a" stroke="#111" stroke-width="3"/>
  <path d="M364 136V250M388 136V250M412 136V250M436 136V250" stroke="#555" stroke-width="5"/>
  <rect x="352" y="300" width="96" height="8" rx="3" fill="#555"/>
  {states}
  <!-- Flash's words, how it goes, the marks so far -->
  <rect x="190" y="4" width="420" height="34" rx="8" fill="#111" stroke="#e0b84a" stroke-width="2" opacity="0.95"/>
  {piece(400, 29, "THE SECRET LIES IN THE CRAYON", "gGold", size=18, rot=-1, anchor="middle", fit=390)}
  <text x="400" y="54" font-family="Arial, sans-serif" font-size="11" fill="#f4f4f4" text-anchor="middle">MARK right when the break is over: one mark on each copy.</text>
  <text x="704" y="32" font-family="{FONT}" font-size="12" fill="#f4f4f4" text-anchor="end">MARKS</text>
  {counter}
  <g data-overlay="not-there" style="display:none"><text x="400" y="342" font-family="{FONT}" font-size="13" fill="#ff4f79" stroke="#111" stroke-width="0.8" text-anchor="middle">NOT THERE: WAIT FOR THE END</text></g>
  <g class="press-hit" style="display:none"><text x="400" y="342" font-family="{FONT}" font-size="15" fill="#7ed957" text-anchor="middle">✎ ON IT...</text></g>
  <g class="press-miss" style="display:none"><text x="400" y="342" font-family="{FONT}" font-size="15" fill="#ff4f79" text-anchor="middle">TOO EARLY ✗</text></g>
  <!-- MARK: too early until the break is about to end, right then (it counts when it does) -->
  <g data-overlay="!marking">
    <g><set attributeName="visibility" to="hidden" begin="{window:.2f}s"/>{button("mark_miss", False)}</g>
    <g visibility="hidden"><set attributeName="visibility" to="visible" begin="{window:.2f}s"/>{button("mark_hit", True)}</g>
  </g>
  <g data-action="stop_practice" role="button" tabindex="0" aria-label="Stop practicing"><title>Stop</title>
    <rect x="8" y="400" width="110" height="40" rx="9" fill="#111" stroke="#7ef0ff" stroke-width="3"/>
    {piece(63, 429, "◀ STOP", "gBlueGreen", size=20, rot=-2, anchor="middle", fit=90)}
  </g>
'''
    return _svg(body, "crayon-screen", end=f"{CRAYON_LOOP:.3f}", auto=("mark_miss", CRAYON_LOOP),
                attrs=f' data-sync="audio" data-loop="{CRAYON_LOOP:.3f}" data-pause-on="mark_hit"')


ASSETS = {
    "assets/screens/rhymebook_1.svg": lambda: rhymebook_spread(1),
    "assets/screens/rhymebook_2.svg": lambda: rhymebook_spread(2),
    "assets/records/apache.svg": lambda r="apache": turntable_screen(r),
    "assets/records/funky_drummer.svg": lambda r="funky_drummer": turntable_screen(r),
    "assets/records/its_just_begun.svg": lambda r="its_just_begun": turntable_screen(r),
    "assets/records/impeach_the_president.svg": lambda r="impeach_the_president": turntable_screen(r),
    "assets/records/vitamin_c.svg": lambda r="vitamin_c": turntable_screen(r),
    "assets/records/think_about_it.svg": lambda r="think_about_it": turntable_screen(r),
    "assets/records/the_mexican.svg": lambda r="the_mexican": turntable_screen(r),
    "assets/scenes/battle.svg": battle_scene,
    "assets/endings/ending_legends.svg": ending_legends,
    "assets/endings/ending_static.svg": ending_static,
    "assets/endings/ending_lost_battle.svg": ending_lost_battle,
    "assets/endings/ending_out_of_practice.svg": ending_out_of_practice,
    "assets/scenes/station.svg": station_scene,
    "assets/scenes/block.svg": block_scene,
    "assets/scenes/record_shop.svg": record_shop_scene,
    "assets/scenes/hq.svg": hq_scene,
    "assets/screens/home.svg": home_screen,
    "assets/screens/intro.svg": intro_screen,
    "assets/screens/escape.svg": escape_screen,
    "assets/screens/practice.svg": practice_screen,
    "assets/screens/crayon.svg": crayon_screen,
    "assets/scenes/flash.svg": flash_scene,
    "assets/scenes/corner_store.svg": corner_store_scene,
    "assets/walks/hq__flash.svg": walk_hq_to_flash,
    "assets/walks/flash__hq.svg": walk_flash_to_hq,
    "assets/walks/block__record_shop.svg": walk_block_to_record_shop,
    "assets/walks/record_shop__block.svg": walk_record_shop_to_block,
    "assets/walks/hq__block.svg": walk_hq_to_block,
    "assets/walks/block__hq.svg": walk_block_to_hq,
    "assets/scenes/gate.svg": gate_scene,
    "assets/walks/gate__station.svg": walk_gate_to_station,
    "assets/walks/block__gate.svg": walk_block_to_gate,
    "assets/walks/gate__block.svg": walk_gate_to_block,
    "assets/walks/station__block.svg": walk_station_to_block,
}


ASSETS.update(cypher.assets())  # the cypher battle: Reekz's moves and Kid Cyclone's sets


def main():
    for path, make in ASSETS.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(make())
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
