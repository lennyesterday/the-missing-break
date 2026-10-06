"""Game rules: scenes, items, conditions, actions. Pure functions, no Streamlit, no DB."""

from dataclasses import dataclass, field

START_SCENE = "hq"
LOCKED_STATION_MESSAGE = "The gate is chained shut. You need a key."

ITEMS = {
    "service_key": "Old MTA service key",
}

# Story content (docs/story.md). Only the parts of specs/first-feature.md for now.
SCENES = {
    "hq": {
        "title": "The Basement",
        "text": (
            "The crate is empty, and there's a Concrete Kings sticker on the turntable. "
            "Needle is furious."
        ),
        "actions": [
            {"id": "go_record_shop", "label": "Go to Rico's Record Shop", "target": "record_shop"},
            {"id": "go_block", "label": "Hit the block", "target": "block"},
        ],
    },
    "record_shop": {
        "title": "Rico's Record Shop",
        "text": (
            "Rico says the Kings were asking about the abandoned 149th St station. "
            "His cousin used to work for the MTA, and there's an old key in the drawer."
        ),
        "actions": [
            {
                "id": "take_service_key",
                "label": "Take the service key",
                "collects": "service_key",
                "message": "You take the old MTA service key from Rico's drawer.",
            },
            {"id": "go_block", "label": "Back to the block", "target": "block"},
        ],
    },
    "block": {
        "title": "The Basketball Court",
        "text": "A wall full of fresh Concrete Kings tags. Portals studies them.",
        "actions": [
            {
                "id": "enter_station",
                "label": "Enter the abandoned station",
                "target": "station",
                "requires": "service_key",
                "locked_message": LOCKED_STATION_MESSAGE,
            },
            {"id": "go_hq", "label": "Back to the Basement", "target": "hq"},
        ],
    },
    "station": {
        "title": "Abandoned 149th St Station",
        "text": 'King Krete is sitting on a crate with "Dor e Dor" under his arm.',
        "actions": [
            {"id": "go_block", "label": "Back to the block", "target": "block"},
        ],
    },
}


@dataclass
class GameState:
    current_scene: str = START_SCENE
    inventory: list[str] = field(default_factory=list)


@dataclass
class ActionResult:
    accepted: bool
    state: GameState
    message: str = ""


def new_game() -> GameState:
    return GameState(current_scene=START_SCENE, inventory=[])


def _copy(state: GameState) -> GameState:
    return GameState(current_scene=state.current_scene, inventory=list(state.inventory))


def available_actions(state: GameState) -> list[dict]:
    """Actions offered in the current scene. Items already collected are no longer offered."""
    return [
        action
        for action in SCENES[state.current_scene]["actions"]
        if action.get("collects") not in state.inventory
    ]


def apply_action(state: GameState, action_id: str) -> ActionResult:
    """Return a new state. A rejected action returns an unchanged copy of the state."""
    action = next((a for a in available_actions(state) if a["id"] == action_id), None)
    if action is None:
        return ActionResult(False, _copy(state), "You can't do that here.")

    required = action.get("requires")
    if required and required not in state.inventory:
        return ActionResult(False, _copy(state), action["locked_message"])

    new_state = _copy(state)
    if "collects" in action:
        new_state.inventory.append(action["collects"])
    if "target" in action:
        new_state.current_scene = action["target"]
    return ActionResult(True, new_state, action.get("message", ""))
