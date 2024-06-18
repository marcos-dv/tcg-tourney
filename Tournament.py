import json
import copy
from Player import Player
from Round import Round, RoundStatus
from RoundScheduler import RoundScheduler
from Match import Match

class TournamentType():
    SWISS = "Swiss"
    SINGLE_ELIMINATION = "Simple elimination"
    DOUBLE_ELIMINATION = "Double elimination"
    ROUND_ROBIN = "Round-Robin"

class Tournament:
    def __init__(self, name):
        self.name = name
        self.rounds = []
        self.participants = []
        self.participants_names = []
        self.type = TournamentType.SWISS
    
    def add_round(self, round):
        self.rounds.append(round)
    
    def add_participant(self, name):
        if name in self.participants_names:
            return False
        self.participants_names.append(name)
        self.participants.append(Player(name))
        return True

    def remove_participant(self, name):
        print('AAAAAAAAAAA', name)
        self.participants_names.remove(name)
        new_part = [p for p in self.participants if p.name != name]
        self.participants = new_part
        #print(*self.participants)
        #print(*self.participants_names)
        
    def set_tournament_type(self, tournamentType):
        self.type = tournamentType
    
    def get_current_matches(self):
        cur_round = self.rounds[-1]
        cur_matches = cur_round.roundMatches
        matches_names = [(m.player1, m.player2) for m in cur_matches]
        return matches_names
    
    def available_participants(self):
        return sum(1 for p in self.participants if p.status == PlayerStatus.PLAYING)

    def start_tourney(self):
        self.generate_round()    

    def generate_round(self):
        self.RoundScheduler = RoundScheduler(self.participants, self.rounds) 
        matches = self.RoundScheduler.find_matches()
        new_round = Round()
        for match in matches:
            new_round.roundMatches.append(match)
        new_round.set_status(RoundStatus.STARTED)
        self.add_round(new_round)
    
    def send_result(self, name1, name2, points1, points2):
        found = False
        for m in self.rounds[-1].roundMatches:
            if m.player1 == name1 and m.player2 == name2:
                m.set_punctuation(points1, points2)
                found = True
                break
            elif m.player1 == name2 and m.player2 == name1:
                m.set_punctuation(points2, points1)
                found = True
                break
        if not found:
            print(f'Error send_result: in round {len(self.rounds)} the following score was not set: {name1} vs {name2}, {points1} - {points2}\n')

    def __str__(self):
        tournament_details = f"Tournament: {self.name}\nParticipants: {[player.name for player in self.participants]}\n"
        for i, round in enumerate(self.rounds, start=1):
            tournament_details += f"\nRound {i} - Status: {round.status}\n{round}\n"
        return tournament_details
        
        
    def to_dict(self):
        tourney_dict = {
        	'name' : self.name, 
        	'rounds' : [r.to_dict() for r in self.rounds],
        	'participants' : [p.to_dict() for p in self.participants],
        	'type' : self.type
        }
        return tourney_dict

    def to_json(self):
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_dict(cls, td):
        t = cls(td['name'])
        t.rounds = [Round.from_dict(r) for r in td['rounds']]
        t.participants = [Player.from_dict(p) for p in td['participants']]
        t.participants_names = [p.name for p in t.participants]
        t.type = td['type']
        return t
