import json
import streamlit as st
import pandas as pd
import Messages as Text
from front_setup import *

def run_init_screen(controller):
    language = controller.get_lang()
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

