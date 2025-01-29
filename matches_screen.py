import json
import streamlit as st
import Messages as Text
from Controller import Controller
from Auxiliar import get_current_time_formatted
from front_setup import *

def run_matches_screen(controller):
    language = controller.get_lang()

    st.header(Text.round_space[language] + str(controller.get_current_round_number()) + ' - ' + controller.get_event_name())

    def save_tourney():
        tourney_json = controller.save_tourney()
        event_name = controller.get_event_name().replace(' ', '_')
        file_name = event_name + "_" + get_current_time_formatted() + ".json"
        col1.download_button(label=Text.save_tourney[language],
                           data=tourney_json,
                           file_name=file_name,
                           mime="text/plain",
                           type='primary')

    # Some options: save and manual matches
    col1, col2 = st.columns(2)
    save_tourney()
    manual_matches = col2.checkbox(Text.manual_matches[language], disabled=False)

    # Pairings
    def display_pairings():
        matches = controller.get_current_matches()
        participants = controller.get_participants_names()
        participants_to_index = {player: index for index, player in enumerate(participants)}
        table = 1
        remove_list = []
        # Bye is skipped this way
        for i in range(controller.get_available_participants() // 2):
            if i >= len(matches):
                st.error(Text.no_available_matches[language])
                print(controller.print_tournament())
                return
            player1, player2 = matches[i] # player1 and player2 are just a suggestion. That will be the way when automatic (no-manual) matches
            st.subheader(Text.table_space[language] + str(table))
            table += 1
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
            with col1:
                p1 = st.selectbox("", participants, index=participants_to_index[player1], disabled=not manual_matches, key=f"table_{i}_player1")
            with col2:
                score1 = st.selectbox("", [0, 1, 2], key=f"table_{i}_score1")
            with col3:
                st.write("vs")
            with col4:
                score2 = st.selectbox("", [0, 1, 2], key=f"table_{i}_score2")
            with col5:
                p2 = st.selectbox("", participants, index=participants_to_index[player2], disabled=not manual_matches, key=f"table_{i}_player2")
            remove_list.append(p1)
            remove_list.append(p2)
        
        if manual_matches:
            feasible_players = [name for name in participants if name not in remove_list]
            st.multiselect(Text.available_players[language], participants, placeholder="", disabled=True, default=feasible_players)

    display_pairings()
    
    # Button to set the result for the match
    def next_round():
        results = []
        player1, player2, score1, score2 =  None, None, None, None
        for i in range(controller.get_available_participants() // 2):
            if f"table_{i}_player1" in st.session_state:
                player1 = st.session_state[f"table_{i}_player1"]
            if f"table_{i}_player2" in st.session_state:
                player2 = st.session_state[f"table_{i}_player2"]
            if f"table_{i}_score1" in st.session_state:
                score1 = st.session_state[f"table_{i}_score1"]
            if f"table_{i}_score2" in st.session_state:
                score2 = st.session_state[f"table_{i}_score2"]
            results.append((player1, player2, score1, score2))
        next_round_success = controller.next_round(results=results, manual=manual_matches)
        if next_round_success:
            st.success(Text.new_round_success_space[language] + str(controller.get_current_round_number()))

    # Button to set the result for the match
    def undo_round():
        undo_round_success = controller.undo_last_round()
        if undo_round_success:
            st.success(Text.undo_round_space[language] + str(controller.get_current_round_number()+1))
    
    col1, col2 = st.columns(2)
    col1.button(':green['+Text.finish_round_next[language]+']', on_click=next_round, key="send_results")
    col2.button(Text.undo_round[language], on_click=undo_round, key="undo_results")
    def move_to_ranking():
        st.session_state.current_screen = ranking_screen
        
    st.button(Text.see_ranking[language], on_click=move_to_ranking)

    advanced_options = st.checkbox(Text.advanced_options[language], value=False)

    if advanced_options:
        dplayer = st.selectbox(Text.drop[language], [""]+controller.get_participants_names(), key="drop")
        if dplayer != "":
            st.error(Text.drop_ack[language] + dplayer + "?")
            if st.button(Text.drop_yes[language] + dplayer):
                controller.drop(dplayer)

        hplayer = st.text_input(Text.hot_insertion[language], key='hot_insertion')
        def hot_insertion():
            if hplayer:
                controller.hot_insertion(hplayer)
                st.session_state.hot_insertion = ''
        st.button(Text.add_player[language], on_click=hot_insertion)

