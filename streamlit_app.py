import json
import streamlit as st
import pandas as pd
from Controller import Controller
from Tournament import Tournament
from Auxiliar import get_current_time_formatted

init_screen = 1
matches_screen = 2
ranking_screen = 3
DEBUG = False

# Initialize session state to store participants
if 'controller' not in st.session_state:
    st.session_state.controller = Controller()
    st.session_state.current_screen = init_screen

if DEBUG:
    st.write(st.session_state.controller.tourney.to_dict())

st.title("Tournament Manager")
#####################
### INITIAL SCREEN ##
#####################
def run_init_screen():
    # Add participants button
    def add_participant():
        if name_input:  # Check if the name input is not empty
            success = st.session_state.controller.add_participant(name_input)
            #if success:
            #    st.success(f"Participant '{name_input}' added!")
            #else:
            #    st.error(f"Could not add '{name_input}'")
            st.session_state.name = ''  # Reset name input field

    # Start tourney buttonl
    def launch_tournament():
        if st.session_state.controller.launch_tourney():
            st.success("Tournament with participants: " + ", ".join(st.session_state.controller.get_participants_names()))
            st.session_state.current_screen = matches_screen
        else:
            st.error("Not enough participants to start the tournament.")

    name_input = st.text_input("Enter participant's name", key='name')

    col1, col2, col3 = st.columns(3)
    col1.button("Add Participant", on_click=add_participant)
    col2.button("Start Tournament ⚔️", on_click=launch_tournament)
    #col3.button("Load Tournament", on_click=load_tourney)
    uploaded_file = col3.file_uploader("Load Tournament")

    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Show details of the uploaded file
        if DEBUG:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
            st.write(file_details)

        # Additional processing can be done here:
        # For example, read the file as text if it's a text file
        if uploaded_file.type == "application/json":
            # To read file as string (use uploaded_file.read() or .getvalue() based on your Streamlit version)
            json_tourney = str(uploaded_file.read(), "utf-8")
            st.session_state.controller.load_tourney(json_tourney)
            st.write(st.session_state.controller.tourney.participants_names)
            if DEBUG:
                st.write(st.session_state.controller.tourney.to_dict())
            st.success('Loaded!')
            # TODO issue: cannot modify a tournament if it is loaded
            uploaded_file = None
        # st.session_state.current_screen = matches_screen

    def remove_participant(name):
        st.session_state.controller.remove_participant(name)
    
    for name in st.session_state.controller.get_participants_names():
        col1, col2 = st.columns([3, 1])  # Adjust the ratio to suit your layout needs
        col1.write(name)
        col2.button("❌", key=name, on_click=remove_participant, args=(name,))
        
    # Print all participants
    st.header("Players")
    names_df = pd.DataFrame(st.session_state.controller.get_participants_names(), columns=["Name"])
    names_df.index += 1
    st.table(names_df)
        
#####################
### MATCHES SCREEN ##
#####################
def run_matches_screen():
    st.header("Round " + str(st.session_state.controller.get_current_round_number()))
    def save_tourney():
        tourney_json = st.session_state.controller.save_tourney()
        
        file_name = "tourney" + get_current_time_formatted() + ".json"
        st.download_button(label="Download tournament 💾",
                           data=tourney_json,
                           file_name=file_name,
                           mime="text/plain",
                           type='primary')

    # Some options: save and manual matches
    col1, col2 = st.columns(2)
    col1.button("Save tournament", on_click=save_tourney, type='primary')
    manual_matches = col2.checkbox("Manual matches", disabled=True)

    # Show matches
    # Display matches and input for scores
    # matches = [('aaa','bbb'), ('ccc','ddd'), ('eee','fff')]
    # TODO join two manual and not manual. The not manual should have disabled selectboxes...
    if not manual_matches:
        matches = st.session_state.controller.get_current_matches()
        table = 1
        for player1, player2 in matches:
            st.subheader("Table " + str(table))
            table += 1
            match_key = f"{player1} vs {player2}"
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                score1 = st.selectbox(player1, [0, 1, 2], key=f"{match_key} - 1")
            with col2:
                st.write(" **vs** ")
            with col3:
                score2 = st.selectbox(player2, [0, 1, 2], key=f"{match_key} - 2")

    elif manual_matches:
        remove_list = []
        for i in range((len(st.session_state.controller.get_available_participants())+1)//2):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
            with col1:
                p1 = st.selectbox("", st.session_state.controller.get_participants_names(), index=None, key=f"match_{i}_player1")
            with col2:
                score1 = st.selectbox("", [0, 1, 2], key=f"match_{i}_score1")
            with col3:
                st.write("vs")
            with col4:
                score2 = st.selectbox("", [0, 1, 2], key=f"match_{i}_score2")
            with col5:
                p2 = st.selectbox("", st.session_state.controller.get_participants_names(), index=None, key=f"match_{i}_player2")
            remove_list.append(p1)
            remove_list.append(p2)

        feasible_players = [name for name in st.session_state.controller.get_participants_names() if name not in remove_list]
        
        st.multiselect("Available players:", st.session_state.controller.get_participants_names(), disabled=True, default=feasible_players)

    # Button to set the result for the match
    def next_round():
        results = []
        matches = st.session_state.controller.get_current_matches()
        for player1, player2 in matches:
            match_key = f"{player1} vs {player2}"
            if f"{match_key} - 1" in st.session_state:
                score1 = st.session_state[f"{match_key} - 1"]
            if f"{match_key} - 2" in st.session_state:
                score2 = st.session_state[f"{match_key} - 2"]
            results.append((player1, player2, score1, score2))
        st.session_state.controller.next_round(results=results)

    # Button to set the result for the match
    def undo_round():
        st.session_state.controller.undo_last_round()
    
    col1, col2 = st.columns(2)
    col1.button("Finish round and start next 🚀", on_click=next_round, key="send_results")
    col2.button("Undo round ↩️", on_click=undo_round, key="undo_results")
    def move_to_ranking():
        st.session_state.current_screen = ranking_screen
        
    st.button("See Ranking 👑", on_click=move_to_ranking)
            
#####################
### RANKING SCREEN ##
#####################
def run_ranking_screen():
    st.header("Round " + str(st.session_state.controller.get_current_round_number()))
    ranking = st.session_state.controller.get_ranking()
    if len(ranking) <= 3:
        ranking.index += 1 # 1-indexed
    else:
        ranking_index = ['🥇', '🥈', '🥉'] + list(range(4, len(ranking)+1))
        ranking.index = ranking_index
    st.write(ranking)

    def move_to_matches():
        st.session_state.current_screen = matches_screen
        
    st.button("Back to matches 🌚", on_click=move_to_matches)


#############
### ACTION ##
#############
if st.session_state.current_screen == init_screen:
    run_init_screen()
elif st.session_state.current_screen == matches_screen:
    run_matches_screen()
elif st.session_state.current_screen == ranking_screen:
    run_ranking_screen()
    
    
    
    
