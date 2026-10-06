from logic import LOCKED_STATION_MESSAGE, apply_action, available_actions, new_game


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
    assert "go_record_shop" in action_ids(state)
    assert "go_block" in action_ids(state)


def test_enter_station_without_key_is_rejected():
    # Done when 1 / A1
    state = play(new_game(), "go_block")

    result = apply_action(state, "enter_station")

    assert not result.accepted
    assert result.message == LOCKED_STATION_MESSAGE
    assert result.state.current_scene == "block"
    assert result.state.inventory == []
    assert state.current_scene == "block"
    assert state.inventory == []


def test_take_key_only_once():
    # Done when 2 / A3
    state = play(new_game(), "go_record_shop")
    assert "take_service_key" in action_ids(state)

    state = play(state, "take_service_key")
    assert state.inventory == ["service_key"]
    assert "take_service_key" not in action_ids(state)

    # Leave and come back: the drawer is still empty (PT R3).
    state = play(state, "go_block", "go_hq", "go_record_shop")
    assert "take_service_key" not in action_ids(state)

    result = apply_action(state, "take_service_key")
    assert not result.accepted
    assert result.state.inventory == ["service_key"]
    assert result.state.inventory.count("service_key") == 1


def test_enter_station_with_key():
    # Done when 3 / A2
    state = play(new_game(), "go_record_shop", "take_service_key", "go_block")

    result = apply_action(state, "enter_station")

    assert result.accepted
    assert result.state.current_scene == "station"
    assert result.state.inventory == ["service_key"]


def test_action_not_in_current_scene_is_rejected():
    state = play(new_game(), "go_record_shop", "take_service_key", "go_block", "go_hq")

    result = apply_action(state, "enter_station")

    assert not result.accepted
    assert result.state.current_scene == "hq"
    assert result.state.inventory == ["service_key"]


def test_apply_action_does_not_mutate_input_state():
    state = play(new_game(), "go_record_shop")

    apply_action(state, "take_service_key")

    assert state.inventory == []
