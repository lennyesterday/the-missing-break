import pytest

from logic import LOCKED_STATION_MESSAGE, apply_action, available_actions, home_choice, new_game


def play(state, *action_ids):
    """Apply accepted actions one after another and return the final state."""
    for action_id in action_ids:
        result = apply_action(state, action_id)
        assert result.accepted, f"{action_id} was rejected: {result.message}"
        state = result.state
    return state


def action_ids(state):
    return [action["id"] for action in available_actions(state)]


def test_new_game_starts_in_hq_with_empty_inventory():
    state = new_game()
    assert state.current_scene == "hq"
    assert state.inventory == []
    # changed: the basement only leads to the block; Rico's is reached from the block
    assert "go_record_shop" not in action_ids(state)
    assert "go_block" in action_ids(state)


def test_the_block_leads_everywhere():
    # the block is the hub: back to the basement, Rico's, the station, Disco Fever
    state = play(new_game(), "go_block")
    assert {"go_hq", "go_record_shop", "go_gate", "go_battle"} <= set(action_ids(state))  # changed: the crew walks to the station gate first (the gate is its own place now)


def test_enter_station_without_key_is_rejected():
    # Done when 1 / A1
    state = play(new_game(), "go_block", "go_gate")  # changed: the crew walks to the station gate first (the gate is its own place now)

    result = apply_action(state, "enter_station")

    assert not result.accepted
    assert result.message == LOCKED_STATION_MESSAGE
    assert result.state.current_scene == "gate"
    assert result.state.inventory == []
    assert state.current_scene == "gate"
    assert state.inventory == []


def test_from_the_gate_back_to_the_block():
    # without the key: back to the block, and on to Rico's for it
    state = play(new_game(), "go_block", "go_gate", "go_block", "go_record_shop")
    assert state.current_scene == "record_shop"


def test_take_key_only_once():
    # Done when 2 / A3
    # changed: the basement only leads to the block; Rico's is reached from the block
    state = play(new_game(), "go_block", "go_record_shop")
    assert "take_service_key" in action_ids(state)

    state = play(state, "take_service_key")
    assert state.inventory == ["service_key"]
    assert "take_service_key" not in action_ids(state)

    # Leave and come back: the drawer is still empty (PT R3).
    state = play(state, "go_block", "go_hq", "go_block", "go_record_shop")
    assert "take_service_key" not in action_ids(state)

    result = apply_action(state, "take_service_key")
    assert not result.accepted
    assert result.state.inventory == ["service_key"]
    assert result.state.inventory.count("service_key") == 1


def test_enter_station_with_key():
    # Done when 3 / A2
    # changed: the basement only leads to the block; Rico's is reached from the block
    state = play(new_game(), "go_block", "go_record_shop", "take_service_key", "go_block", "go_gate")  # changed: the crew walks to the station gate first (the gate is its own place now)

    result = apply_action(state, "enter_station")

    assert result.accepted
    assert result.state.current_scene == "station"
    assert result.state.inventory == ["service_key"]


def test_action_not_in_current_scene_is_rejected():
    # changed: the basement only leads to the block; Rico's is reached from the block
    state = play(new_game(), "go_block", "go_record_shop", "take_service_key", "go_block", "go_hq")

    result = apply_action(state, "enter_station")

    assert not result.accepted
    assert result.state.current_scene == "hq"
    assert result.state.inventory == ["service_key"]


def test_apply_action_does_not_mutate_input_state():
    # changed: the basement only leads to the block; Rico's is reached from the block
    state = play(new_game(), "go_block", "go_record_shop")

    apply_action(state, "take_service_key")

    assert state.inventory == []


@pytest.mark.parametrize("choice, has_save, outcome", [
    ("start", False, "new_game"),
    ("start", True, "confirm_restart"),  # PT01: never replace progress without asking
    ("resume", True, "resume"),
    ("resume", False, "ignore"),
    ("menu", True, "ignore"),  # the menu comes in a later feature
    ("menu", False, "ignore"),
    ("nonsense", True, "ignore"),
])
def test_home_choice(choice, has_save, outcome):
    assert home_choice(choice, has_save) == outcome


@pytest.mark.parametrize("choice, outcome", [
    ("restart_yes", "new_game"),
    ("restart_no", "cancel"),
    ("start", "ignore"),  # while the sign asks, the train's buttons wait
    ("resume", "ignore"),
    ("menu", "ignore"),
])
def test_home_choice_while_asking_to_start_over(choice, outcome):
    assert home_choice(choice, has_save=True, confirming=True) == outcome


def test_confirm_answers_mean_nothing_when_not_asking():
    assert home_choice("restart_yes", has_save=True) == "ignore"
    assert home_choice("restart_no", has_save=True) == "ignore"


def test_basement_conversation():
    from logic import SCENES
    dialogue = SCENES["hq"]["dialogue"]
    speakers = {speaker for speaker, _ in dialogue}
    assert speakers <= {"needle", "bible", "meyhem", "portals", "reekz"}
    assert speakers == {"needle", "bible", "meyhem", "portals", "reekz"}  # the whole crew talks
    lines = " ".join(line for _, line in dialogue)
    assert "WHAT HAPPENED, NEEDLE?" in lines
    assert "THAT SHIT IS CRAZY, DAWG" in lines  # changed: edited by the product owner
    # changed: the Sopranos crossed out the GoodFellas piece instead of leaving a sticker
    assert "CROSSED OUT OUR NAME" in lines
    assert "STICKER" not in lines
    # hints for the player: the rhyme book on the couch, and Rico
    assert "RHYME BOOK" in lines and "COUCH" in lines
    assert "RICO" in lines


# --- rhyme book, rap battle, DJ battle, endings (docs/story.md) ---

from logic import CHOKED_MESSAGE, ENDINGS, GameState as _State  # noqa: E402


def test_take_rhyme_book_only_once():
    state = play(new_game(), "take_rhyme_book")
    assert state.inventory == ["rhyme_book"]
    assert "take_rhyme_book" not in action_ids(state)
    assert not apply_action(state, "take_rhyme_book").accepted


def test_meyhem_going_first_is_remembered():
    # changed: the order now matters (Meyhem has to go first), so it is remembered; it used to
    # be "only words, nothing changes" (more in test_rap_order.py)
    state = _State(current_scene="station", inventory=["service_key"])
    result = apply_action(state, "meyhem_first")
    assert result.accepted
    assert "KRETE" in result.message.upper()
    assert result.state.rap_battle == "meyhem_went_first"
    assert result.state.inventory == ["service_key"]


def test_rap_round_2_without_the_rhyme_book_is_lost():
    # changed: Bible finishes Krete after Meyhem went first ("bible_finishes", was "rap_round_2");
    # without his rhyme book he is no longer turned down: he chokes and the battle is lost
    state = _State(current_scene="station", inventory=["service_key"], rap_battle="meyhem_went_first")
    result = apply_action(state, "bible_finishes")
    assert result.accepted
    assert result.message == CHOKED_MESSAGE
    assert result.state.rap_battle == "lost" and "vinyl" not in result.state.inventory
    assert result.state.ending == "ending_lost_battle"  # and the game is over: start again


def test_rap_round_2_with_the_rhyme_book_wins_the_record():
    # changed: only after Meyhem went first ("bible_finishes", was "rap_round_2")
    state = _State(current_scene="station", inventory=["rhyme_book", "service_key"], rap_battle="meyhem_went_first")
    result = apply_action(state, "bible_finishes")
    assert result.accepted
    assert result.state.inventory == ["rhyme_book", "service_key", "vinyl"]
    assert "bible_finishes" not in action_ids(result.state)  # the record can be won only once


def test_disco_fever_from_the_block():
    state = play(new_game(), "go_block", "go_battle")
    assert state.current_scene == "battle"
    assert action_ids(state) == ["start_battle"]


def test_with_the_record_the_battle_ends_with_the_legends():
    # changed: the plot twist: the record is only enough once Needle has practiced (test_practice.py)
    state = _State(current_scene="battle", inventory=["rhyme_book", "service_key", "vinyl"], practiced=True)
    result = apply_action(state, "start_battle")
    assert result.accepted
    assert result.state.ending == "ending_legends"


def test_without_the_record_the_battle_ends_in_the_static():
    state = _State(current_scene="battle", inventory=[])
    result = apply_action(state, "start_battle")
    assert result.state.ending == "ending_static"


def test_after_an_ending_story_actions_stop():
    # PT05 / A5: at an ending, further story actions cannot change the completed game
    state = _State(current_scene="battle", inventory=[], ending="ending_static")
    assert available_actions(state) == []
    result = apply_action(state, "start_battle")
    assert not result.accepted
    assert result.state == state


def test_both_endings_are_reachable_from_a_new_game():
    # PT R4 / A5: the win path and the lose path from docs/story.md
    # changed: the basement only leads to the block; Rico's is reached from the block
    win = play(new_game(), "take_rhyme_book", "go_block", "go_record_shop", "take_service_key", "go_block",
               "go_gate", "enter_station", "meyhem_first", "bible_finishes", "go_block", "go_hq",
               "try_practice", "go_flash", "go_hq", "go_block", "win_cypher", "go_store", "buy_crayons", "go_block",
               "go_hq", "practice", "go_block", "go_battle", "start_battle")
    # changed: Meyhem first, then Bible; via the gate; practice in the basement, which takes Flash's
    # advice and crayons from the corner store, paid for with the cypher's prize
    lose = play(new_game(), "go_block", "go_battle", "start_battle")
    assert win.ending == "ending_legends"
    assert lose.ending == "ending_static"


def test_endings_are_clearly_identified():
    assert ENDINGS["ending_legends"]["title"] == "Legends of the Bronx"
    assert ENDINGS["ending_static"]["title"] == "Lost in the Static"
    assert "Think About It" in ENDINGS["ending_legends"]["text"]
