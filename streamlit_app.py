import json
import streamlit as st
import pandas as pd
import Messages as Text
from Controller import Controller
from Tournament import Tournament
from Auxiliar import get_current_time_formatted
from PIL import Image

init_screen = 1
matches_screen = 2
ranking_screen = 3
DEBUG = False

language = st.radio(
    "",
    Text.available_languages,
    index=1,
    horizontal=True
)

# Initialize session state to store participants
if 'controller' not in st.session_state:
    st.session_state.controller = Controller()
    st.session_state.current_screen = init_screen

controller = st.session_state.controller

if DEBUG:
    st.write(controller.tourney.to_dict())

def display_zero():
    st.title(Text.app_title[language])

#####################
### INITIAL SCREEN ##
#####################
def run_init_screen():
    # Display the event name
    event_name = st.text_input(Text.event_name[language], key='event_name')

    # Add participants button
    def add_participant():
        if name_input:  # Check if the name input is not empty
            success = controller.add_participant(name_input)
            #if success:
            #    st.success(f"Participant '{name_input}' added!")
            #else:
            #    st.error(f"Could not add '{name_input}'")
            st.session_state.name = ''  # Reset name input field

    # Start tourney buttonl
    def launch_tournament():
        if event_name:
            controller.set_event_name(event_name)
        if controller.launch_tourney():
            st.success(Text.launch_tourney_participants[language] + ", ".join(controller.get_participants_names()))
            st.session_state.current_screen = matches_screen
        else:
            st.error(Text.not_enough_players[language])

    name_input = st.text_input(Text.enter_player_name[language], key='name')
    if name_input: # allows insertion by "Enter"
        controller.add_participant(name_input)
        
    col1, col2, col3 = st.columns(3)
    col1.button(':blue['+Text.add_player[language]+']', on_click=add_participant)
    col2.button(':orange['+Text.start_tournament[language]+']', on_click=launch_tournament)
    #col3.button("Load Tournament", on_click=load_tourney)
    uploaded_file = col3.file_uploader(Text.load_tournament[language])

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
            load_success = controller.load_tourney(json_tourney)
            if DEBUG:
                st.write(controller.tourney.participants_names)
                st.write(controller.tourney.to_dict())
            st.success(Text.load_success[language])
            uploaded_file = None
            # go to matches if we are already in second round
            if load_success and controller.get_current_round_number() >= 2:
                st.session_state.current_screen = matches_screen
                st.rerun()
        # st.session_state.current_screen = matches_screen

    def remove_participant(name):
        controller.remove_participant(name)
    
    for name in controller.get_participants_names():
        col1, col2 = st.columns([3, 1])  # Adjust the ratio to suit your layout needs
        col1.write(name)
        col2.button("❌", key=name, on_click=remove_participant, args=(name,))
        
    # Print all participants
    st.header(Text.players[language])
    names_df = pd.DataFrame(controller.get_participants_names(), columns=[Text.name[language]])
    names_df.index += 1
    st.table(names_df)
        
#####################
### MATCHES SCREEN ##
#####################
def run_matches_screen():
    st.header(Text.round_space[language] + str(controller.get_current_round_number()) + ' - ' + controller.get_event_name())

    def save_tourney():
        tourney_json = controller.save_tourney()
        event_name = controller.get_event_name().replace(' ', '_')
        file_name = event_name + "_" + get_current_time_formatted() + ".json"
        st.download_button(label=Text.save_tourney[language],
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

    dplayer = st.selectbox("Drop this player?", [""]+controller.get_participants_names(), key="drop")
    if dplayer != "":
        st.error("Do you really, really, wanna drop " + dplayer + "?")
        if st.button("Yes, drop " + dplayer):
            controller.drop(dplayer)

    hot_insertions = st.checkbox("Hot insertions?", disabled=False, value=False)
    if hot_insertions:
        hplayer = st.text_input("Hot insertion? ", key='hot_insertion')
        def hot_insertion():
            if hplayer:
                controller.hot_insertion(hplayer)
                st.session_state.hot_insertion = ''
        st.button("Add player", on_click=hot_insertion)
                
#####################
### RANKING SCREEN ##
#####################
def run_ranking_screen():
    st.header(Text.round_space[language] + str(controller.get_current_round_number()))
    ranking = controller.get_ranking()
    ranking.columns = [Text.name[language], Text.points[language], Text.wld[language], Text.omp[language], Text.gp[language], Text.ogp[language]]
    if len(ranking) <= 3:
        ranking.index += 1 # 1-indexed
    else:
        ranking_index = ['🥇', '🥈', '🥉'] + list(range(4, len(ranking)+1))
        ranking.index = ranking_index
    st.write(ranking)

    st.subheader(Text.dominance_graph[language])
    graph_image = controller.get_dominance_graph_image()
    image = Image.open(graph_image)
    # Display the image
    st.image(image, caption=None, use_column_width=True)

    def move_to_matches():
        st.session_state.current_screen = matches_screen
    st.button(Text.back_to_matches[language], on_click=move_to_matches)    
    

#############
### ACTION ##
#############
display_zero()
if st.session_state.current_screen == init_screen:
    run_init_screen()
elif st.session_state.current_screen == matches_screen:
    run_matches_screen()
elif st.session_state.current_screen == ranking_screen:
    run_ranking_screen()
    
    
    
    
