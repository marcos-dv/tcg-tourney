import pandas as pd
import json
from Tournament import Tournament

DEBUG = False

class Controller:
    def __init__(self):
        self.tourney = Tournament('Default tourney')

    def add_participant(self, name):
        self.tourney.add_participant(name)
        
    def launch_tourney(self):
        if len(self.tourney.participants_names) == 0:
            return False
        self.tourney.start_tourney()
        return True

    def next_round(self, results):
        for p1,p2,s1,s2 in results:
            self.tourney.send_result(p1,p2,s1,s2)
            
        return self.tourney.generate_round()
        
    def undo_last_round(self):
        return self.tourney.undo_last_round()
        
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
        return self.tourney.available_participants()

    def get_ranking(self):
        stats = self.tourney.get_stats()
        # Creating a DataFrame from the list of tuples
        stats_df = pd.DataFrame(stats, columns=['Name', 'Points', 'W-L-D', 'VPO', 'JG', 'JGO'])
        return stats_df

    # to a dict
    def save_tourney(self):
        return self.tourney.to_json()

    # from a dict
    def load_tourney(self, tourney_json):
        td = json.loads(tourney_json)
        self.tourney = Tournament.from_dict(td)
        if DEBUG:
            print(self.tourney)
