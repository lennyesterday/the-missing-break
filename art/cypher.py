"""The cypher battle on the block, in 3D: Reekz against Kid Cyclone.

One 3D skeleton (head, shoulders, elbows, hands, hips, knees, feet) is used for every move. A
move is a list of poses over time (FPS per second), drawn in perspective; limbs pass in front of
and behind the body. Moves connect: every move starts in a "base" pose and ends in one (standing
for toprock, crouched on the floor for footwork and power moves, the freeze to end a set), and
the clip for a move starts from the pose the move before ended in (DROP down, or GET UP first).

    uv run python -m art.build   (writes assets/cypher/*.svg)
"""

import math

from art import crew
from art.crew import _face_points, _face_svg, _headwear_points, _headwear_svg, _project
from art.scenery import FONT, defs, piece, tag
from logic import CYPHER_BASES, CYPHER_MOVES, RIVAL, RIVAL_SETS

FPS = 20
FLOOR = (400, 388)  # the middle of the cardboard, where they dance
HUD_TOP = 404  # below this the strip with the buttons (nothing of the dance goes there)
SCALE = 0.9  # the 3D dancers next to the 2D crowd (big enough to see what they do)
JOINTS = ("hat", "head", "face", "sh_l", "sh_r", "el_l", "el_r", "hand_l", "hand_r",
          "hip_l", "hip_r", "kn_l", "kn_r", "foot_l", "foot_r")
LIMBS = [("sh_l", "el_l", 12, False), ("el_l", "hand_l", 10, False), ("sh_r", "el_r", 12, False), ("el_r", "hand_r", 10, False),
         ("hip_l", "kn_l", 16, False), ("kn_l", "foot_l", 13, True), ("hip_r", "kn_r", 16, False), ("kn_r", "foot_r", 13, True)]
TORSO = ("sh_l", "sh_r", "hip_r", "hip_l")
REEKZ = {"top": "#c0392b", "back": "#93291e", "skin": "#4a2e1c", "stripe": "#f4f4f4",
         "wears": "bucket", "hat": "#f4f4f4"}  # red tracksuit, white bucket hat
CYCLONE = {"top": "#7d3cff", "back": "#5a2bb8", "skin": "#6b4226", "stripe": "#f4f4f4",
           "wears": "headband", "hat": "#d02b2b"}  # purple tracksuit, red headband


# --- the body (x right, y up, z towards us; the floor is y = 0, the cardboard's middle x = z = 0) ---
#
# A pose is a rig: where his pelvis is, how his body is turned (yaw round the vertical, pitch
# leaning forward, roll tipping over sideways; roll = pi is upside down, still facing us), and
# where his hands and feet go. Knees and elbows are worked out from that (two bones, fixed
# lengths), so arms and legs never stretch or shrink, and they bend the right way. Poses are
# blended rig to rig, never joint to joint.

THIGH, SHIN, UPPER_ARM, FOREARM = 42, 42, 24, 23
SPINE, NECK, HIP_W, SHOULDER_W = 40, 22, 10, 16
CAMERA_PITCH, CAMERA_YAW = math.radians(24), math.radians(-28)  # a bit from above, three-quarter


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _mul(a, k):
    return tuple(x * k for x in a)


def _unit(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return tuple(x / n for x in v)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _rotation(yaw, pitch, roll):
    """The body's turn: first leaning forward (pitch), then tipped over (roll), then round (yaw)."""
    cy, sy, cp, sp, cr, sr = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch), math.cos(roll), math.sin(roll)

    def turn(v):
        x, y, z = v
        y, z = y * cp - z * sp, y * sp + z * cp      # pitch: the top goes towards where he faces (z)
        x, y = x * cr - y * sr, x * sr + y * cr      # roll: tipping over sideways
        x, z = x * cy + z * sy, -x * sy + z * cy     # yaw: turning round
        return (x, y, z)
    return turn


def _bend(root, target, a, b, pole):
    """Two bones from root towards target (a, b long): where the joint between them goes (bent
    towards pole) and where the end goes (the target, or as near as the bones reach)."""
    d_vec = _sub(target, root)
    d = math.sqrt(_dot(d_vec, d_vec)) or 1e-6
    n = _mul(d_vec, 1 / d)
    d = min(max(d, abs(a - b) + 0.5), a + b - 0.01)
    along = (a * a - b * b + d * d) / (2 * d)
    up = math.sqrt(max(0.0, a * a - along * along))
    side = _sub(pole, _mul(n, _dot(pole, n)))
    side = _unit(side) if _dot(side, side) > 1e-9 else _unit(_sub((0, 0, 1), _mul(n, n[2])))
    joint = _add(_add(root, _mul(n, along)), _mul(side, up))
    end = _add(joint, _mul(_unit(_sub(_add(root, _mul(n, d)), joint)), b))
    return joint, end


def solve(rig):
    """The rig as joints (the JOINTS the drawing uses)."""
    turn = _rotation(rig["yaw"], rig["pitch"], rig["roll"])
    pelvis = rig["pelvis"]
    chest = _add(pelvis, turn((0, SPINE, 0)))
    head = _add(chest, turn((0, NECK, 3)))
    j = {"head": head, "face": _add(head, turn((0, 0, 14))), "hat": _add(head, turn((0, 14, 0)))}
    for side, sign in (("l", -1), ("r", 1)):
        hip = _add(pelvis, turn((sign * HIP_W, 0, 0)))
        shoulder = _add(chest, turn((sign * SHOULDER_W, 0, 0)))
        knee_pole = rig.get(f"knee_{side}") or turn((sign * 0.25, 0.2, 1))         # knees forward, a bit out
        elbow_pole = rig.get(f"elbow_{side}") or turn((sign * 0.7, -0.2, -0.7))   # elbows back and out
        foot = rig[f"foot_{side}"]
        hand = rig[f"hand_{side}"]
        j[f"hip_{side}"], j[f"sh_{side}"] = hip, shoulder
        j[f"kn_{side}"], j[f"foot_{side}"] = _bend(hip, foot, THIGH, SHIN, knee_pole)
        j[f"el_{side}"], j[f"hand_{side}"] = _bend(shoulder, hand, UPPER_ARM, FOREARM, elbow_pole)
    lowest = min(y for _, y, _ in j.values())
    if lowest < 0:  # never through the floor: the whole body a little higher
        j = {n: (x, y - lowest, z) for n, (x, y, z) in j.items()}
    return {n: tuple(round(c, 3) for c in j[n]) for n in JOINTS}


def _rig(pelvis, hands, feet, yaw=0.0, pitch=0.0, roll=0.0, **poles):
    r = {"pelvis": pelvis, "yaw": yaw, "pitch": pitch, "roll": roll,
         "hand_l": hands[0], "hand_r": hands[1], "foot_l": feet[0], "foot_r": feet[1]}
    r.update(poles)
    return r


def _angle_lerp(a, b, u):
    d = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + d * u


def _mix(a, b, u):
    """A rig between a and b (the turns the short way round)."""
    out = {}
    for k in set(a) | set(b):
        va, vb = a.get(k), b.get(k)
        if va is None or vb is None:
            out[k] = None
        elif k in ("yaw", "pitch", "roll"):
            out[k] = _angle_lerp(va, vb, u)
        else:
            out[k] = tuple(x + (y - x) * u for x, y in zip(va, vb))
    return out


def _spun(rig, angle, about=(0.0, 0.0)):
    """The whole rig turned round the vertical line through about (x, z)."""
    c, s = math.cos(angle), math.sin(angle)
    ax, az = about

    def p(v):
        x, y, z = v
        return (ax + (x - ax) * c + (z - az) * s, y, az - (x - ax) * s + (z - az) * c)
    out = dict(rig)
    for k in ("pelvis", "hand_l", "hand_r", "foot_l", "foot_r"):
        out[k] = p(rig[k])
    for k in ("knee_l", "knee_r", "elbow_l", "elbow_r"):
        if rig.get(k):
            x, y, z = rig[k]
            out[k] = (x * c + z * s, y, -x * s + z * c)
    out["yaw"] = rig["yaw"] + angle
    return out


def _ease(u):
    return u * u * (3 - 2 * u)


def _over(secs, fn):
    """The rigs of one part of a move, FPS per second, fn(u) for u from 0 to 1."""
    n = max(2, round(secs * FPS) + 1)
    return [fn(i / (n - 1)) for i in range(n)]


def _flow(a, b, secs, lift=0.0):
    """Straight from one pose into the next (eased); lift: the pelvis goes up a little on the way
    (when he swings from one move into another)."""
    def at(u):
        r = _mix(a, b, _ease(u))
        if lift:
            x, y, z = r["pelvis"]
            r["pelvis"] = (x, y + lift * math.sin(math.pi * u), z)
        return r
    return _over(secs, at)


def _join(*parts):
    rigs = list(parts[0])
    for part in parts[1:]:
        rigs += part[1:]  # its first pose is the last one already there
    return rigs


# --- the poses ---

STAND_RIG = _rig((0, 82, 0), ((-24, 84, 8), (24, 84, 8)), ((-15, 3, 0), (15, 3, 0)), pitch=-0.05)


def _toprock_rig(u):
    """Two Indian steps: a foot crosses in front and taps, back out, the other one; the arm on
    the other side swings out wide, the body dips on every step, turns with it, leans back."""
    s = math.sin(2 * math.pi * 2 * u)
    r, l = max(0.0, s), max(0.0, -s)
    lift_r, lift_l = math.sin(math.pi * min(1, 2 * r)) if r else 0.0, math.sin(math.pi * min(1, 2 * l)) if l else 0.0
    feet = ((-15 + 30 * l, 3 + 14 * lift_l * (1 - l), 24 * l), (15 - 30 * r, 3 + 14 * lift_r * (1 - r), 24 * r))
    if 0.5 <= u < 0.75:  # the second step on the right is a kick, straight out in front
        feet = (feet[0], (12, 3 + 34 * r, 48 * r))
    # the arm on the other side of the stepping foot swings out wide and up; this side's comes in front
    hands = ((-24 - 34 * r + 14 * l, 84 + 34 * r + 22 * l, 8 + 6 * r + 22 * l),
             (24 + 34 * l - 14 * r, 84 + 34 * l + 22 * r, 8 + 6 * l + 22 * r))
    dip = 7 * (r + l)
    return _rig((0, 82 - dip, 3 * (r + l)), hands, feet, yaw=0.4 * s, pitch=-0.05 - 0.08 * (r + l))


# The helicopter (coffee grinder): down low on his right leg, leaning far forward, hands on the
# floor in front; his left leg straight out sweeps round him. Angle 0: the leg out to his left,
# then behind him, to his right (under his support foot: it hops), in front (his hands lift).
SWEEP_RADIUS, SWEEPS, SWEEP_SECS = 76, 2, 1.0
GRINDER_CENTRE = (4, -6)


def _grinder_rig(angle):
    def near(target):  # 1 when the leg is right at that side, 0 more than 55 degrees away
        gap = abs((angle - target + math.pi) % (2 * math.pi) - math.pi)
        return max(0.0, 1 - gap / math.radians(55))
    hop, lift = near(math.pi), near(3 * math.pi / 2)
    cx, cz = GRINDER_CENTRE
    sweep = (cx - SWEEP_RADIUS * math.cos(angle), 3, cz - SWEEP_RADIUS * math.sin(angle))
    support = (14, 3 + 26 * hop, -6)
    hands = ((-22, 2 + 26 * lift, 42 - 8 * lift), (24, 2 + 26 * lift, 42 - 8 * lift))
    return _rig((4, 28 + 4 * hop, -6), hands, (sweep, support), yaw=0.22 * math.sin(angle), pitch=1.12,
                knee_r=(0.3, 0.8, 0.6))


GRINDER_RIG = _grinder_rig(0.0)

# The headspin: first the tripod (head and hands on the floor, knees tucked, face up to us), the
# legs go up, upside down; the hands push him round, then go out, the legs open into a V.
TRIPOD_RIG = _rig((0, 50, -28), ((-24, 2, 24), (24, 2, 24)), ((-14, 76, -48), (14, 76, -48)), roll=math.pi, pitch=0.9,
                  knee_l=(0, -0.3, 1), knee_r=(0, -0.3, 1))
HEADSPIN_RIG = _rig((0, 76, 0), ((-58, 46, 10), (58, 46, -10)), ((-40, 152, 0), (40, 152, 0)), roll=math.pi)
HEADSPIN_TURNS, SPIN_SECS = 3, 2.4

# The 1990: a handstand on his right hand, his left arm out, legs straight up, turning round
# the hand on the floor.
NINETY_HAND = (-18.0, 2.0, 0.0)
NINETY_RIG = _rig((-2, 86, 0), ((56, 74, 14), NINETY_HAND), ((-12, 172, 6), (14, 170, -6)), roll=math.pi - 0.08)
NINETY_TURNS, NINETY_SECS = 2, 2.2

# The freeze: a chair freeze, tipped over sideways onto his right hand and his head, his elbow
# in his side, legs bent up in the air.
FREEZE_RIG = _rig((16, 52, -4), ((-48, 64, 14), (2, 2, 6)), ((48, 96, -34), (54, 104, 24)), roll=2.3, pitch=0.15,
                  knee_l=(0.5, 1, -0.3), knee_r=(0.6, 1, 0.4))
FREEZE_HOLD = 1.3

# Where he is when each move is over (and the next one starts from).
EXIT = {"stand": STAND_RIG, "helicopter": GRINDER_RIG, "headspin": HEADSPIN_RIG, "nineteen_ninety": NINETY_RIG,
        "freeze": FREEZE_RIG}
ENTRY = {"toprock": STAND_RIG, "helicopter": GRINDER_RIG, "headspin": TRIPOD_RIG, "nineteen_ninety": NINETY_RIG,
         "freeze": FREEZE_RIG}


def next_base_of(move):
    return "stand" if move == "toprock" else move


def _move_rigs(name):
    """The move itself, from its first pose to its last."""
    if name == "toprock":
        rigs = _over(2.4, _toprock_rig)
    elif name == "helicopter":
        rigs = _over(SWEEPS * SWEEP_SECS, lambda u: _grinder_rig(2 * math.pi * SWEEPS * u))
    elif name == "headspin":
        def spin(u):
            push = max(0.0, 1 - u / 0.22)  # the hands push him round, then go out
            r = _mix(HEADSPIN_RIG, _rig(HEADSPIN_RIG["pelvis"], ((-26, 2, 18), (26, 2, 18)),
                                        ((-16, 156, 0), (16, 156, 0)), roll=math.pi), push)
            r["yaw"] = 0.0
            if u > 0.2:  # once he's spinning, the legs scissor: wide open, together, open again
                open_ = 0.5 + 0.5 * math.cos(2 * math.pi * 2.5 * (u - 0.2))
                spread, swing = 10 + 38 * open_, 22 * math.sin(2 * math.pi * 2.5 * (u - 0.2))
                r["foot_l"] = (-spread, 150 - 6 * open_, swing)
                r["foot_r"] = (spread, 150 - 6 * open_, -swing)
            turn = 2 * math.pi * HEADSPIN_TURNS * (0.35 * u + 0.65 * _ease(u))  # starts fast, slows into the end
            return _spun(r, turn)
        up = _flow(TRIPOD_RIG, _mix(HEADSPIN_RIG, _rig(HEADSPIN_RIG["pelvis"], ((-26, 2, 18), (26, 2, 18)),
                                                       ((-16, 156, 0), (16, 156, 0)), roll=math.pi), 1.0), 0.45)
        rigs = _join(up, _over(SPIN_SECS, spin))
    elif name == "nineteen_ninety":
        about = (NINETY_HAND[0], NINETY_HAND[2])
        rigs = _over(NINETY_SECS, lambda u: _spun(NINETY_RIG, 2 * math.pi * NINETY_TURNS * _ease(u), about))
    elif name == "freeze":
        def hold(u):  # held, only breathing
            r = dict(FREEZE_RIG)
            x, y, z = r["pelvis"]
            r["pelvis"] = (x, y + 0.8 * math.sin(2 * math.pi * u), z)
            return r
        rigs = _over(FREEZE_HOLD, hold)
    else:
        raise ValueError(name)
    rigs[-1] = dict(EXIT[next_base_of(name)])
    return rigs


def _lead_in(base, move):
    """From where he is straight into the move: quick, with a little swing up when he goes from
    one floor move into another, a drop when he goes down from standing."""
    a, b = EXIT[base], ENTRY[move]
    if a == b:
        return [dict(a)]
    if move == "freeze":  # it snaps in: a little past (tipped further, legs kicked higher), then it settles
        past = dict(FREEZE_RIG)
        past["roll"] = past["roll"] + 0.12
        past["foot_l"], past["foot_r"] = (_add(past["foot_l"], (8, 14, 0)), _add(past["foot_r"], (8, 14, 0)))
        return _join(_flow(a, past, 0.28), _flow(past, b, 0.16))
    far = math.dist(a["pelvis"], b["pelvis"]) + 40 * abs(_angle_lerp(0, b["roll"] - a["roll"], 1))
    secs = 0.3 if move == "freeze" else min(0.75, 0.35 + far / 260)  # the freeze snaps in
    lift = 0 if base == "stand" or move == "toprock" else 14
    return _flow(a, b, secs, lift=lift)


def _move(name):
    """A move, as joints, from its first pose to its last."""
    return [solve(r) for r in _move_rigs(name)]


def _from(base, move):
    """The clip for a move from where he is: straight from the pose the last move ended in."""
    rigs = _join(_lead_in(base, move), _move_rigs(move))
    rigs[0] = dict(EXIT[base])
    return [solve(r) for r in rigs]


def _set(moves):
    """A whole set, move after move, from standing."""
    base, frames = "stand", [solve(STAND_RIG)]
    for move in moves:
        frames = frames + _from(base, move)[1:]
        base = next_base_of(move)
    return frames


def _turn(pose, angle, about=(0, 0)):
    """The whole body (joints) turned round the vertical line through about (x, z)."""
    c, s = math.cos(angle), math.sin(angle)
    ax, az = about
    return {n: (ax + (x - ax) * c + (z - az) * s, y, az - (x - ax) * s + (z - az) * c) for n, (x, y, z) in pose.items()}


STAND, INVERTED, NINETY, FREEZE, TRIPOD = (solve(r) for r in (STAND_RIG, HEADSPIN_RIG, NINETY_RIG, FREEZE_RIG, TRIPOD_RIG))


# --- drawing it ---

def render3d(gid, frames, look, begin=0.0):
    """The body through all its poses: limbs (each drawn behind and in front of the torso, only
    the copy on the right side showing), torso, head, face, and the bucket hat or the headband."""
    proj = [{n: _project(p, CAMERA_YAW, 0, pitch=CAMERA_PITCH) for n, p in {**f, **_face_points(f), **_headwear_points(f, look["wears"])}.items()}
            for f in frames]
    secs = (len(proj) - 1) / FPS
    timing = f'dur="{secs:.2f}s" begin="{begin:.2f}s" fill="freeze"'

    def values(fn):
        return ";".join(fn(f) for f in proj)

    def discrete(fn):
        return f'values="{";".join(fn(i) for i in range(len(proj)))}" calcMode="discrete"'

    def depth(i, names):
        return sum(proj[i][n][2] for n in names) / len(names)

    def limb(a, b, width, shoe, layer):
        in_front = (lambda i: (proj[i][a][2] + proj[i][b][2]) / 2 >= depth(i, TORSO))
        show = discrete(lambda i: "1" if in_front(i) == (layer == "front") else "0")
        d = values(lambda f: f"M{f[a][0]:.1f} {f[a][1]:.1f}L{f[b][0]:.1f} {f[b][1]:.1f}")
        out = (f'<g class="{layer}"><animate attributeName="opacity" {show} {timing}/>'
               f'<path stroke="#111" stroke-width="{width + 3}" stroke-linecap="round" fill="none"><animate attributeName="d" values="{d}" {timing}/></path>'
               f'<path stroke="{look["top"]}" stroke-width="{width}" stroke-linecap="round" fill="none"><animate attributeName="d" values="{d}" {timing}/></path>'
               f'<path stroke="{look["stripe"]}" stroke-width="2" fill="none"><animate attributeName="d" values="{d}" {timing}/></path>')
        if not shoe and b.startswith("hand"):
            out += (f'<circle r="6.5" fill="{look["skin"]}" stroke="#111" stroke-width="1.5">'
                    f'<animate attributeName="cx" values="{values(lambda f: f"{f[b][0]:.1f}")}" {timing}/>'
                    f'<animate attributeName="cy" values="{values(lambda f: f"{f[b][1]:.1f}")}" {timing}/></circle>')
        if shoe:
            out += (f'<circle r="8" fill="#f4f4f4" stroke="#111" stroke-width="1.5">'
                    f'<animate attributeName="cx" values="{values(lambda f: f"{f[b][0]:.1f}")}" {timing}/>'
                    f'<animate attributeName="cy" values="{values(lambda f: f"{f[b][1]:.1f}")}" {timing}/></circle>')
        return out + "</g>"

    def dot(name, r, fill):
        return (f'<circle r="{r}" fill="{fill}" stroke="#111" stroke-width="1.5">'
                f'<animate attributeName="cx" values="{values(lambda f: f"{f[name][0]:.1f}")}" {timing}/>'
                f'<animate attributeName="cy" values="{values(lambda f: f"{f[name][1]:.1f}")}" {timing}/></circle>')

    corners = values(lambda f: " ".join(f"{f[n][0]:.1f},{f[n][1]:.1f}" for n in TORSO))
    facing = [proj[i]["face"][2] > proj[i]["head"][2] for i in range(len(proj))]
    colour = discrete(lambda i: look["top"] if facing[i] else look["back"])
    torso = (f'<polygon fill="#111" stroke="#111" stroke-width="22" stroke-linejoin="round"><animate attributeName="points" values="{corners}" {timing}/></polygon>'
             f'<polygon stroke-width="19" stroke-linejoin="round"><animate attributeName="points" values="{corners}" {timing}/>'
             f'<animate attributeName="fill" {colour} {timing}/><animate attributeName="stroke" {colour} {timing}/></polygon>')
    neck_d = values(lambda f: f"M{(f['sh_l'][0] + f['sh_r'][0]) / 2:.1f} {(f['sh_l'][1] + f['sh_r'][1]) / 2:.1f}L{f['head'][0]:.1f} {f['head'][1]:.1f}")
    neck = (f'<path class="neck" stroke="{look["skin"]}" stroke-width="10" stroke-linecap="round" fill="none">'
            f'<animate attributeName="d" values="{neck_d}" {timing}/></path>')
    eye = _face_svg(proj, "head", timing, loop=False)  # two eyes and a mouth, turned with his head
    behind, on_top = _headwear_svg(proj, look["wears"], look["hat"], timing, loop=False)
    back = "".join(limb(a, b, w, shoe, "back") for a, b, w, shoe in LIMBS)
    front = "".join(limb(a, b, w, shoe, "front") for a, b, w, shoe in LIMBS)
    return (f'<g id="{gid}" transform="translate({FLOOR[0]} {FLOOR[1]}) scale({SCALE})">'
            f'<ellipse cx="0" cy="4" rx="80" ry="14" fill="#000" opacity="0.25"/>'
            f'{back}{torso}{neck}{behind}{dot("head", 14, look["skin"])}{eye}{on_top}{front}</g>')


def _seconds(frames):
    return (len(frames) - 1) / FPS


# --- the scene round the dancers, and the battle's signs ---


# Round the cardboard in a half circle, like a cypher: (who, x, feet, scale). Further back is
# higher up and smaller, at the sides nearer and bigger. The GoodFellas on the left, Kid
# Cyclone's crew on the right; whoever waits for his turn stands nearest the cardboard.
CIRCLE_LEFT = [("meyhem", 250, 340, 0.86), ("bible", 192, 352, 0.9), ("needle", 132, 366, 0.95), ("portals", 66, 382, 1.0)]
CIRCLE_RIGHT = [("cap", 550, 340, 0.86), ("headband", 608, 352, 0.9), ("bucket hat", 668, 366, 0.95), ("kangol", 734, 382, 1.0)]
WAITING_LEFT, WAITING_RIGHT = (305, 332, 0.82), (495, 332, 0.82)


def _waiting(who):
    """Reekz or Kid Cyclone, waiting for his turn at the edge of the cardboard."""
    if who == "reekz":
        x, feet, scale = WAITING_LEFT
        return crew.placed(crew.reekz(x, idle="nod"), "reekz", x, feet, scale)
    x, feet, scale = WAITING_RIGHT
    return crew.placed(f'<g transform="translate({2 * x} 0) scale(-1 1)">{crew.bboy(x, "toprock")}</g>', "bboy-cyclone", x, feet, scale)


def _circle():
    """The GoodFellas and Kid Cyclone's crew round the cardboard."""
    goodfellas = {"meyhem": lambda x: crew.meyhem_front(x), "bible": lambda x: crew.bible_front(x),  # (these two face us)
                  "needle": lambda x: crew.needle(x, idle="nod"), "portals": lambda x: crew.portals(x, idle="nod")}
    left = "".join(crew.placed(goodfellas[who](x), who, x, feet, s) for who, x, feet, s in CIRCLE_LEFT)
    # Kid Cyclone's crew turned round (mirrored), to face the dancer in the middle
    right = "".join(crew.placed(f'<g transform="translate({2 * x} 0) scale(-1 1)">{crew.bboy(x, who)}</g>', f"bboy-{who.split()[0]}", x, feet, s)
                    for who, x, feet, s in CIRCLE_RIGHT)
    return f'\n  <!-- round the cardboard: the GoodFellas, and Kid Cyclone\'s crew -->\n  <g id="circle">{left}{right}</g>'


def _crowd():
    """People from the block watching: a row of them along the store front, some throwing their
    arms up; three more looking out of the store window, two in the door."""
    looks = crew.LOOKS
    row = "".join(crew.onlooker(x, 336, looks[k % len(looks)], k, cheer=k % 3 == 1, scale=0.72)
                  for k, x in enumerate(range(30, 780, 46)))
    window = "".join(crew.onlooker(x, 300, looks[(k + 3) % len(looks)], k + 20, scale=0.78) for k, x in enumerate((84, 140, 196)))
    door = "".join(crew.onlooker(x, 326, looks[(k + 6) % len(looks)], k + 30, scale=0.82) for k, x in enumerate((644, 696)))
    return f'''
  <!-- the crowd from the block -->
  <clipPath id="storeWindow"><rect x="47" y="131" width="184" height="144"/></clipPath>
  <g id="store-window-crowd" clip-path="url(#storeWindow)">{window}</g>
  <clipPath id="storeDoor"><rect x="613" y="127" width="114" height="203"/></clipPath>
  <g id="store-door-crowd" clip-path="url(#storeDoor)">{door}</g>
  <g id="crowd-row">{row}</g>'''


def _backdrop():
    """Close up in front of the corner store: the awning, the window full of goods, the door, the
    sidewalk with its cracks, the cardboard, the crowd from the block along the store front, and
    the two crews round the cardboard in a half circle."""
    goods = "".join(f'<rect x="{x}" y="{y}" width="24" height="32" rx="3" fill="{c}" stroke="#111" stroke-width="1.5"/>'
                    f'<rect x="{x + 4}" y="{y + 8}" width="16" height="10" fill="#f4f4f4" opacity="0.7"/>'
                    for x, y, c in ((60, 150, "#d02b2b"), (90, 150, "#ffd23f"), (120, 150, "#3fa9f5"), (150, 150, "#7ed957"),
                                    (180, 150, "#ff8a3d"), (60, 192, "#f4f4f4"), (90, 192, "#c58bff"), (120, 192, "#d02b2b"),
                                    (150, 192, "#ffd23f"), (180, 192, "#3fa9f5")))
    cracks = ('<path d="M40 360L90 372L120 366M600 344L640 356L690 352L700 362M180 430L230 420M560 436L620 428L640 440" '
              'stroke="#7d7d85" stroke-width="2" fill="none"/>'
              '<g stroke="#86868e" stroke-width="2"><path d="M0 390H800"/><path d="M160 330L120 450M400 330V382M640 330L680 450"/></g>')
    return f'''
  <rect width="800" height="330" fill="url(#bricks)"/>
  <rect width="800" height="330" fill="#2a1a20" opacity="0.3"/>
  <rect x="40" y="14" width="420" height="52" fill="#f4e7c3" stroke="#111" stroke-width="4"/>
  <rect x="40" y="14" width="420" height="10" fill="#fff" opacity="0.3"/>
  <text x="250" y="52" font-family="{FONT}" font-size="34" fill="#c0392b" text-anchor="middle" letter-spacing="2">CORNER STORE</text>
  <path d="M20 70H800V112H20Z" fill="#2e8b57"/>
  <path d="M60 70L52 112M120 70L116 112M180 70L180 112M240 70L244 112M300 70L308 112M360 70L372 112M420 70L436 112M480 70L500 112M540 70L564 112M600 70L628 112M660 70L692 112M720 70L756 112" stroke="#f4f4f4" stroke-width="18" opacity="0.9"/>
  <path d="M20 112Q50 122 80 112Q110 122 140 112Q170 122 200 112Q230 122 260 112Q290 122 320 112Q350 122 380 112Q410 122 440 112Q470 122 500 112Q530 122 560 112Q590 122 620 112Q650 122 680 112Q710 122 740 112Q770 122 800 112" fill="#2e8b57" stroke="#1f6b42" stroke-width="2"/>
  <rect x="44" y="128" width="190" height="150" fill="#f9e2a2" stroke="#111" stroke-width="6"/>
  {goods}
  <path d="M60 140L110 270M150 140L200 270" stroke="#fff" stroke-width="6" opacity="0.18"/>
  <rect x="610" y="124" width="120" height="206" fill="#3a2a1c" stroke="#111" stroke-width="6"/>
  <rect x="300" y="130" width="250" height="40" fill="#000" opacity="0"/>
  {tag(300, 180, "Rock Steady", "#f4f4f4", 26, -6)}{tag(500, 160, "SF", "#d02b2b", 22, -10)}{tag(256, 300, "Cyclone", "#c58bff", 18, 4)}
  <rect y="330" width="800" height="120" fill="#9a9aa2"/>
  <path d="M0 330H800" stroke="#6e6e76" stroke-width="3"/>
  {cracks}
  {_crowd()}
  <g id="cardboard"><path d="M250 402L284 362H516L550 402Z" fill="#b08a5a" stroke="#6b4e2a" stroke-width="3"/>
    <path d="M284 362H516L513 366H287Z" fill="#c9a26a"/>
    <path d="M350 364L330 400M450 364L440 400" stroke="#8b6b3a" stroke-width="3"/>
    <path d="M270 390L300 384M500 384L530 392" stroke="#8b6b3a" stroke-width="2" opacity="0.6"/>
    <rect x="452" y="372" width="30" height="12" fill="#c0392b" opacity="0.45" transform="rotate(-6 467 378)"/></g>
  <ellipse cx="400" cy="400" rx="170" ry="8" fill="#000" opacity="0.12"/>
{_circle()}'''


def _shouts(begin, words):
    return "".join(
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="28" fill="{c}" stroke="#111" stroke-width="1.2" '
        f'text-anchor="middle" transform="rotate({rot} {x} {y})" opacity="0">{word}'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" dur="1.4s" begin="{begin + k * 0.7:.1f}s" fill="freeze"/></text>'
        for k, (x, y, c, rot, word) in enumerate(words))


def _button(action, label, x, w, edge, grad, y=406, h=40):
    return (f'<g data-action="{action}" role="button" tabindex="0" aria-label="{label.title()}"><title>{label.title()}</title>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#111" stroke="{edge}" stroke-width="3" opacity="0.94"/>'
            f'{piece(x + w / 2, y + h * 0.72, label, grad, size=min(20, h * 0.52), rot=-2, anchor="middle", fit=w - 16)}</g>')


NOTES = {
    "flow": ("FLOW! +1 A STEP UP", "#7ed957"), "finish": ("HIT THE FREEZE!", "#ffd23f"),
    "repeat": ("SAME MOVE AGAIN -2", "#d02b2b"), "seen": ("SEEN IT BEFORE -1", "#ff8a3d"),
    "no_freeze": ("NO FREEZE -2", "#d02b2b"),
}


def _hud():
    """The battle's signs, shown by the page: Reekz's next move (choose), his set so far
    (did-<n>-<move>), the crowd's verdict and points (judge), and who runs the cypher."""
    labels = list(CYPHER_MOVES.items())
    w, gap, left, y, h = 116, 6, 186, HUD_TOP + 6, 34
    spots = {m: left + k * (w + gap) for k, (m, _) in enumerate(labels)}
    buttons = "".join(_button(f"move:{m}", info["label"], spots[m], w, "#ff8a3d", "gOrangeRed", y=y, h=h) for m, info in labels)
    chips = "".join(f'<g data-overlay="did-{i}-{m}" style="display:none"><rect x="{12 + i * 104}" y="78" width="98" height="24" rx="6" fill="#111" opacity="0.85"/>'
                    f'<text x="{61 + i * 104}" y="95" font-family="{FONT}" font-size="13" fill="#ffd23f" text-anchor="middle">{i + 1}. {info["label"]}</text></g>'
                    for i in range(4) for m, info in CYPHER_MOVES.items())
    scores = "".join(f'<text data-overlay="reekz-score-{n}" style="display:none" x="300" y="246" font-family="{FONT}" font-size="40" fill="#ff4f79" text-anchor="middle">{n}</text>'
                     f'<text data-overlay="rival-score-{n}" style="display:none" x="500" y="246" font-family="{FONT}" font-size="40" fill="#c58bff" text-anchor="middle">{n}</text>'
                     for n in range(16))
    notes = "".join(f'<g data-overlay="note-{key}" style="display:none"><text x="400" y="{276 + 18 * k}" font-family="{FONT}" font-size="14" fill="{c}" text-anchor="middle" letter-spacing="1">{text}</text></g>'
                    for k, (key, (text, c)) in enumerate(NOTES.items()))
    # up next: its button lights up, with a tag on top (nothing over the dance)
    queued = "".join(f'<g data-overlay="queued-{m}" style="display:none"><title>UP NEXT: {CYPHER_MOVES[m]["label"]}</title><rect x="{spots[m] - 3}" y="{y - 3}" width="{w + 6}" height="{h + 6}" rx="11" fill="none" stroke="#ffd23f" stroke-width="3">'
                     f'<animate attributeName="opacity" values="1;0.4;1" dur="0.8s" repeatCount="indefinite"/></rect>'
                     f'<rect x="{spots[m] + w / 2 - 34}" y="{HUD_TOP - 12}" width="68" height="15" rx="5" fill="#ffd23f" stroke="#111" stroke-width="1.5"/>'
                     f'<text x="{spots[m] + w / 2}" y="{HUD_TOP - 1}" font-family="{FONT}" font-size="10" fill="#111" text-anchor="middle" letter-spacing="1">UP NEXT</text></g>'
                     for m in CYPHER_MOVES)
    rounds = "".join(f'<text data-overlay="round-{r}" style="display:none" x="792" y="70" font-family="{FONT}" font-size="20" fill="#f4f4f4" stroke="#111" stroke-width="1" text-anchor="end">ROUND {r} OF 3</text>'
                     for r in (1, 2, 3))
    return f'''
  <!-- the battle's signs -->
  {rounds}
  <g id="set-so-far">{chips}</g>
  <!-- the strip along the bottom, under the cardboard: the buttons, nothing over the dance -->
  <rect x="0" y="{HUD_TOP}" width="800" height="{450 - HUD_TOP}" fill="#0b0716" opacity="0.88"/>
  <path d="M0 {HUD_TOP}H800" stroke="#ff8a3d" stroke-width="2" opacity="0.7"/>
  <g data-overlay="choose" style="display:none">
    <text x="150" y="{HUD_TOP + 21}" font-family="{FONT}" font-size="11" fill="#ffd23f" text-anchor="middle" letter-spacing="1">REEKZ&#39;S</text>
    <text x="150" y="{HUD_TOP + 36}" font-family="{FONT}" font-size="11" fill="#ffd23f" text-anchor="middle" letter-spacing="1">NEXT MOVE ▶</text>
    {buttons}
    {queued}
  </g>
  <!-- end choose -->
  <g data-overlay="judge" style="display:none">
    <rect x="150" y="120" width="500" height="258" rx="14" fill="#111" stroke="#ffd23f" stroke-width="3" opacity="0.95"/>
    <text x="400" y="150" font-family="{FONT}" font-size="16" fill="#f4f4f4" text-anchor="middle" letter-spacing="2">THE CROWD SAYS...</text>
    <g data-overlay="round-won" style="display:none">{piece(400, 182, "REEKZ TAKES THE ROUND!", "gPinkYellow", size=28, rot=-2, anchor="middle", fit=440)}</g>
    <g data-overlay="round-lost" style="display:none">{piece(400, 182, f"{RIVAL} TAKES IT", "gPurple", size=28, rot=-2, anchor="middle", fit=440)}</g>
    <text x="300" y="208" font-family="{FONT}" font-size="12" fill="#ff4f79" text-anchor="middle">REEKZ</text>
    <text x="500" y="208" font-family="{FONT}" font-size="12" fill="#c58bff" text-anchor="middle">{RIVAL}</text>
    <text x="400" y="240" font-family="{FONT}" font-size="22" fill="#f4f4f4" text-anchor="middle">–</text>
    {scores}
    {notes}
    <g data-overlay="can-next" style="display:none">{_button("next_round", "NEXT ROUND ▶", 520, 140, "#7ed957", "gBlueGreen", y=330)}</g>
    <g data-overlay="cypher-won" style="display:none">{piece(400, 362, "REEKZ RUNS THE CYPHER! +$10", "gGold", size=26, rot=-2, anchor="middle", fit=460)}</g>
    <g data-overlay="cypher-lost" style="display:none">{piece(400, 362, f"{RIVAL} KEEPS THE CYPHER", "gSteel", size=24, rot=-2, anchor="middle", fit=460)}</g>
  </g>
  <!-- end judge -->
  <g data-action="leave_cypher" role="button" tabindex="0" aria-label="Back to the block"><title>Back to the block</title>
    <rect x="8" y="{HUD_TOP + 6}" width="104" height="34" rx="9" fill="#111" stroke="#7ef0ff" stroke-width="3" opacity="0.94"/>
    {piece(60, HUD_TOP + 30, "◀ BLOCK", "gBlueGreen", size=17, rot=-2, anchor="middle", fit=88)}
  </g>'''


def _screen(body, auto, secs):
    extra = f'id="cypher-screen" data-end="{secs:.1f}" data-auto-action="{auto}" data-auto-delay="{secs:.1f}"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" {extra} viewBox="0 0 800 450" width="800" height="450">\n'
            f'{defs()}{body}{_hud()}\n</svg>\n')


def reekz_clip(base, move):
    """Reekz's move, from the pose he is in; Kid Cyclone stands by in the circle."""
    frames = _from(base, move)
    secs = _seconds(frames)
    shouts = {"headspin": [(170, 170, "#ffd23f", -8, "OHHH!"), (640, 160, "#7ed957", 6, "SPIN IT!")],
              "nineteen_ninety": [(170, 170, "#ffd23f", -8, "1990!!"), (640, 160, "#7ed957", 6, "OHHH!")],
              "freeze": [(400, 140, "#ff4f79", -4, "FREEZE!")],
              "helicopter": [(640, 160, "#7ed957", 6, "GO REEKZ!"), (170, 170, "#ffd23f", -6, "HELICOPTER!")],
              "toprock": [(170, 170, "#ffd23f", -6, "AYYY!")]}[move]
    body = (_backdrop() + _waiting("cyclone")
            + f'\n  <!-- Reekz: {CYPHER_MOVES[move]["label"]} (from {base}) -->\n  '
            + render3d("reekz-3d", frames, REEKZ) + _shouts(secs * 0.4, shouts))
    return _screen(body, "move_done", secs)  # the next move follows right away (he holds the last pose meanwhile)


def rival_clip(r):
    """Kid Cyclone's set in round r; then Reekz steps onto the cardboard, standing, ready."""
    frames = _set(RIVAL_SETS[r - 1])
    secs = _seconds(frames)
    ready = [dict(STAND), dict(STAND)]
    title = (f'<g opacity="1"><animate attributeName="opacity" values="1;1;0" keyTimes="0;0.8;1" dur="2s" fill="freeze"/>'
             f'<rect x="200" y="120" width="400" height="70" rx="12" fill="#111" opacity="0.88"/>'
             f'{piece(400, 168, f"ROUND {r}: {RIVAL}", "gPurple", size=30, rot=-2, anchor="middle", fit=360)}</g>')
    body = (_backdrop()
            + f'<g><set attributeName="visibility" to="hidden" begin="{secs + 0.4:.1f}s"/>{_waiting("reekz")}</g>'
            + f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="{secs + 0.4:.1f}s"/>{_waiting("cyclone")}</g>'
            + f'\n  <!-- {RIVAL}: {", ".join(CYPHER_MOVES[m]["label"] for m in RIVAL_SETS[r - 1])} -->\n  '
            + f'<g><set attributeName="visibility" to="hidden" begin="{secs + 0.4:.1f}s"/>{render3d("rival-3d", frames, CYCLONE)}</g>'
            + _shouts(1.5, [(170, 170, "#c58bff", -6, "CYCLONE!"), (640, 160, "#7ed957", 6, "OHHH!")])
            + f'\n  <!-- then Reekz steps in -->\n  <g visibility="hidden"><set attributeName="visibility" to="visible" begin="{secs + 0.4:.1f}s"/>'
            + render3d("reekz-3d", ready, REEKZ, begin=secs + 0.4) + "</g>" + title)
    return _screen(body, "reekz_turn", secs + 1.0)


def assets():
    """Every clip of the battle: Reekz's moves from standing and from the floor, Kid Cyclone's sets."""
    out = {f"assets/cypher/{m}_from_{b}.svg": (lambda b=b, m=m: reekz_clip(b, m)) for b in CYPHER_BASES for m in CYPHER_MOVES}
    out.update({f"assets/cypher/rival_{r}.svg": (lambda r=r: rival_clip(r)) for r in (1, 2, 3)})
    return out
