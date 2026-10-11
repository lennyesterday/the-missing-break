"""The 3D breakers' faces: two eyes and a mouth on the front of the head, placed the way the
head is turned; hidden when he faces away, upside down when he is upside down."""

from pathlib import Path

from art import cypher
from art.crew import _face_points, _project, reekz_breaking

ROOT = Path(__file__).parent.parent


def on_screen(pose):
    feats = {**pose, **_face_points(pose)}
    return {n: _project(p, 0, 0) for n, p in feats.items()}


def test_two_eyes_and_a_mouth_on_the_front_of_the_head():
    p = on_screen(cypher.STAND)
    head = p["head"]
    for n in ("eye_l", "eye_r", "mouth_l", "mouth_c", "mouth_r"):
        assert p[n][2] > head[2], n                          # on the side facing us
        assert abs(p[n][0] - head[0]) < 14 and abs(p[n][1] - head[1]) < 14, n  # on the head
    assert p["eye_l"][0] < head[0] < p["eye_r"][0]           # one eye each side
    assert p["eye_l"][1] < p["mouth_c"][1]                   # eyes above the mouth


def test_upside_down_the_face_is_upside_down():
    for pose in (cypher.INVERTED, cypher.NINETY):
        p = on_screen(pose)
        assert p["eye_l"][1] > p["mouth_c"][1] and p["eye_r"][1] > p["mouth_c"][1]  # eyes below the mouth on screen


def test_facing_away_no_face():
    back = cypher._turn(cypher.STAND, 3.14159)
    p = on_screen(back)
    assert all(p[n][2] < p["head"][2] for n in ("eye_l", "eye_r", "mouth_c"))


def test_the_clips_draw_the_face():
    svg = (ROOT / "assets" / "cypher" / "headspin_from_stand.svg").read_text()  # changed: no crouch clips any more
    body = svg[svg.index('id="reekz-3d"'):]
    assert body.count('class="eye"') == 2 and body.count('class="mouth"') == 1
    assert 'class="eye"' in (ROOT / "assets" / "cypher" / "rival_1.svg").read_text()


def test_the_basement_spins_draw_the_face_too():
    dance = reekz_breaking(0, 0)
    for move in ("headspin", "nineteen-ninety"):
        face = dance[dance.index(f'id="{move}-face"'):]
        face = face[:face.index("</g>", face.index('class="mouth"'))]
        assert face.count('class="eye"') == 2 and 'class="mouth"' in face
