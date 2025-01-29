import json
import streamlit as st
import pandas as pd
import Messages as Text

from front_setup import *

from init_screen import run_init_screen
from matches_screen import run_matches_screen
from ranking_screen import run_ranking_screen

from Controller import Controller
from Tournament import Tournament

# Initialize session state to store participants
if 'controller' not in st.session_state:
    st.session_state.controller = Controller()
    st.session_state.current_screen = init_screen

controller = st.session_state.controller

language = st.radio(
    "",
    Text.available_languages,
    index=1,
    horizontal=True
)

controller.set_lang(language)

if DEBUG:
    st.write(controller.tourney.to_dict())

def display_zero():
    st.title(Text.app_title[language])
        
#############
### ACTION ##
#############
display_zero()
if st.session_state.current_screen == init_screen:
    run_init_screen(controller)
elif st.session_state.current_screen == matches_screen:
    run_matches_screen(controller)
elif st.session_state.current_screen == ranking_screen:
    run_ranking_screen(controller)
    
    
    
    
