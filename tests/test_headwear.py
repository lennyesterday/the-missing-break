"""The breakers' headwear in 3D: Reekz's bucket hat, Kid Cyclone's hair and headband.
(changed: these were in test_six_step.py, which went with the 6-step)"""

from pathlib import Path

from art.crew import reekz_breaking

ROOT = Path(__file__).parent.parent


def test_reekz_wears_a_bucket_hat_in_3d():
    svg = (ROOT / "assets" / "cypher" / "headspin_from_stand.svg").read_text()  # changed: no crouch clips any more
    body = svg[svg.index('id="reekz-3d"'):]
    assert body.count('class="brim"') == 1 and body.count('class="crown"') == 1
    assert 'r="11"' not in body                                # not a ball on his head any more


def test_kid_cyclone_has_hair_and_a_headband():
    svg = (ROOT / "assets" / "cypher" / "rival_1.svg").read_text()
    body = svg[svg.index('id="rival-3d"'):svg.index('id="reekz-3d"')]
    assert 'class="hair"' in body and body.count('class="headband"') >= 8
    assert 'class="brim"' not in body


def test_the_basement_spins_wear_the_bucket_hat_too():
    dance = reekz_breaking(0, 0)
    assert dance.count('class="brim"') == 2 and dance.count('class="crown"') == 2
