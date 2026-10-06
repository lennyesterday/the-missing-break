"""Streamlit screens only, no game rules."""

import streamlit as st

import db
import logic

st.set_page_config(page_title="The Missing Break")


def start_new_game():
    st.session_state.game = logic.new_game()
    db.save_game(db.db_path(), st.session_state.game)
    st.session_state.feedback = None


def resume_game():
    st.session_state.game = db.load_game(db.db_path())
    st.session_state.feedback = None


def do_action(action_id):
    result = logic.apply_action(st.session_state.game, action_id)
    if result.accepted:
        st.session_state.game = result.state
        db.save_game(db.db_path(), result.state)
    st.session_state.feedback = (result.accepted, result.message)


def show_menu():
    st.title("The Missing Break")
    st.write(
        "South Bronx, summer 1977. Two days before the borough DJ battle, the Concrete Kings "
        'stole your crew\'s secret weapon: Tom Zé – "Dor e Dor". Get it back.'
    )
    if db.has_save(db.db_path()):
        st.button("Resume", key="resume", on_click=resume_game)
    else:
        st.button("New game", key="new_game", on_click=start_new_game)


def show_game():
    game = st.session_state.game
    scene = logic.SCENES[game.current_scene]

    with st.sidebar:
        st.subheader("Inventory")
        if game.inventory:
            for item in game.inventory:
                st.write(f"- {logic.ITEMS[item]}")
        else:
            st.write("Empty")

    st.header(scene["title"])
    st.write(scene["text"])

    feedback = st.session_state.get("feedback")
    if feedback and feedback[1]:
        accepted, message = feedback
        (st.success if accepted else st.warning)(message)

    for action in logic.available_actions(game):
        st.button(action["label"], key=action["id"], on_click=do_action, args=(action["id"],))


if "game" in st.session_state:
    show_game()
else:
    show_menu()
