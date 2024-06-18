import json
from Tournament import Tournament

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
        
    def get_participants_names(self):
        return self.tourney.participants_names

    def remove_participant(self, name):
        self.tourney.remove_participant(name)
        # print(*self.get_participants_names())

    def get_current_matches(self):
        return self.tourney.get_current_matches()
        
    def get_available_participants(self):
        return self.tourney.available_participants()

	# to a dict
    def save_tourney(self):
        return self.tourney.to_json()

	# from a dict
    def load_tourney(self, tourney_json):
        td = json.loads(tourney_json)
        self.tourney = Tournament.from_dict(td)
        print(self.tourney)
