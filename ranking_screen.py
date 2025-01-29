import streamlit as st
import Messages as Text
from PIL import Image
from Controller import Controller
from front_setup import *

def run_ranking_screen(controller):
    language = controller.get_lang()

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

