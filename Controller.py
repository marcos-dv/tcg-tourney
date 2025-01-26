import pandas as pd
import json
from Tournament import Tournament
import Dominance

DEBUG = False

class Controller:
    def __init__(self):
        self.tourney = Tournament('Default tourney')

    def add_participant(self, name):
        self.tourney.add_participant(name)
        
    def launch_tourney(self, event_name=None):
        if len(self.tourney.participants_names) == 0:
            return False
        self.tourney.start_tourney()
        return True

    def next_round(self, results, manual=False):
        if manual:
            self.tourney.send_manual_results(results)
        else:
            self.tourney.send_results(results)
        return self.tourney.generate_round()
        
    def undo_last_round(self):
        return self.tourney.undo_last_round()
        
    def get_event_name(self):
        return self.tourney.get_name()

    def set_event_name(self, event_name):
        self.tourney.set_name(event_name)
        
    def get_participants_names(self):
        return self.tourney.participants_names

    def remove_participant(self, name):
        self.tourney.remove_participant(name)
        # print(*self.get_participants_names())

    def get_current_matches(self):
        return self.tourney.get_current_matches()

    def get_current_round_number(self):
        return self.tourney.get_current_round_number()
        
    def get_available_participants(self):
        return self.tourney.num_available_participants()

    def drop(self, name):
        return self.tourney.drop_participant(name)

    def hot_insertion(self, name):
        return self.tourney.add_hot_participant(name)

    def get_ranking(self):
        stats = self.tourney.get_stats()
        # Creating a DataFrame from the list of tuples
        stats_df = pd.DataFrame(stats, columns=['Name', 'Points', 'W-L-D', 'OMP', 'GP', 'OGP'])
        return stats_df

    # to a dict
    def save_tourney(self):
        return self.tourney.to_json()

    # from a dict
    # ret false case
    def load_tourney(self, tourney_json):
        td = json.loads(tourney_json)
        self.tourney = Tournament.from_dict(td)
        if DEBUG:
            print(self.tourney)
        return True
            
            
    def get_dominance_graph_image(self):
        names, dominance_arcs, draw_arcs = self.tourney.get_dominance()
        return Dominance.save_dominance_graph(names, dominance_arcs, draw_arcs)
        
    def print_tournament(self):
        return str(self.tourney)
        
