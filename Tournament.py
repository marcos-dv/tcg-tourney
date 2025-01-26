import json
import copy
import time
from Player import Player, PlayerStatus
from Round import Round, RoundStatus
from PairingScheduler import PairingScheduler
from Match import Match
from collections import Counter
from Stats import compute_stats, compute_dominance

class TournamentType():
    SWISS = "Swiss"
    SINGLE_ELIMINATION = "Simple elimination"
    DOUBLE_ELIMINATION = "Double elimination"
    ROUND_ROBIN = "Round-Robin"

class Tournament:
    def __init__(self, name):
        self.name = name
        self.rounds = []
        self.participants = {} # name : Player object
        self.participants_names = []
        self.type = TournamentType.SWISS
        self.hot_insertions = {} # name : round when it was introduced
        self.drops = {} # name : last played round
        self.seed = time.time() # name : last played round
    
    def add_round(self, round):
        self.rounds.append(round)
    
    def add_participant(self, name):
        if name in self.participants_names:
            return False
        self.participants_names.append(name)
        self.participants[name] = Player(name)
        return True

    def add_hot_participant(self, name):
        if name in self.participants_names:
            return False
        self.participants_names.append(name)
        self.participants[name] = Player(name)
        self.hot_insertions[name] = self.get_current_round_number()
        return True

    def drop_participant(self, name):
        self.drops[name] = self.get_current_round_number()

    def remove_participant(self, name):
        self.participants_names.remove(name)
        new_part = { p.name : p for p in self.participants.values() if p.name != name }
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
    
    def set_name(self, event_name):
        self.name = event_name

    def get_name(self):
        return self.name
    
    def num_available_participants(self):
        return sum(1 for p in self.participants.values() if p.status == PlayerStatus.PLAYING)

    def get_active_players(self):
        # dropped players in this round are considered active in the current round
        return [p for p in self.participants.values() if p.status == PlayerStatus.PLAYING or self.drops[p] < self.get_current_round_number()]

    def start_tourney(self):
        if len(self.rounds) == 0:
            self.generate_round()

    def get_current_round_number(self):
        return len(self.rounds)

    def drop_players(self):
        for name,round_number in self.drops.items():
            if round_number == self.get_current_round_number():
                self.participants[name].update_status(PlayerStatus.DROPPED)
        
    def generate_round(self):
        # 1. Finish round
        if len(self.rounds) > 0:
            self.rounds[-1].status = RoundStatus.FINISHED
        # 2. Drop players
        self.drop_players()

        # TODO check type of tourney, swiss, etc
        # 3. Generate new pairings
        stats = self.get_stats() if len(self.rounds) > 0 else None
        scheduler = PairingScheduler(self.get_active_players(), self.rounds, stats, self.seed)
        matches = scheduler.find_matches()
        new_round = Round()
        new_round.roundMatches = [m for m in matches]
        new_round.set_status(RoundStatus.STARTED)
        # 4. New round available
        self.add_round(new_round)
        return True
        
    def undo_hot_insertions(self):
        current_round = self.get_current_round_number()
        to_delete_players = [name for name, round_number in self.hot_insertions.items() if round_number == current_round]
        for name in to_delete_players:
            self.participants_names.remove(name)
            self.participants.pop(name)
            self.hot_insertions.pop(name)
        
    def undo_drops(self):
        current_round = self.get_current_round_number()
        to_restore_players = [name for name, round_number in self.drops.items() if round_number == current_round]
        for name in to_restore_players:
            self.participants[name].update_status(PlayerStatus.PLAYING)
            self.drops.pop(name)

    def undo_last_round(self):
        # undoing round "len(self.rounds)"
        if len(self.rounds) > 1:
            # hot insertions are for incumbent round
            self.undo_hot_insertions()
            del self.rounds[-1]
            self.rounds[-1].status = RoundStatus.STARTED
            # drops are from previous round
            self.undo_drops()
            return True
        return False
        
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

    def send_results(self, results):
        for p1,p2,s1,s2 in results:
            self.send_result(p1,p2,s1,s2)

    def check_manual_results(self, results):
        # Flatten the list of tuples into a single list of strings
        all_players_playing = [player for tpl in results for player in tpl[:2]]

        # Count occurrences of each string
        counter = Counter(all_players_playing)
        duplicates = [string for string, count in counter.items() if count > 1]
        
        # No dupps
        if len(duplicates) == 0:
            return True

        # Print the number of duplicates and the actual strings
        print(f"Number of duplicate strings: {len(duplicates)}")
        print(f"Duplicate strings: {', '.join(duplicates)}")
        return False

    def send_manual_results(self, results):
        last_round = self.rounds[-1]
        self.check_manual_results(results)
        last_round.roundMatches = [ Match(p1,p2,s1,s2) for p1,p2,s1,s2 in results ]

    def get_stats(self):
        return compute_stats(self.participants_names, self.rounds)
        
    def get_dominance(self):
        return compute_dominance(self.participants_names, self.rounds)        

    def __str__(self):
        tournament_details = f"Tournament: {self.name}\nParticipants: {[player.name for player in self.participants.values()]}\n"
        for i, round in enumerate(self.rounds, start=1):
            tournament_details += f"\nRound {i} - Status: {round.status}\n{round}\n"
        return tournament_details
        
    def to_dict(self):
        tourney_dict = {
            'name' : self.name, 
            'rounds' : [r.to_dict() for r in self.rounds],
            'participants' : [p.to_dict() for p in self.participants.values()],
            'type' : self.type
        }
        return tourney_dict

    def to_json(self):
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_dict(cls, td):
        t = cls(td['name'])
        t.rounds = [Round.from_dict(r) for r in td['rounds']]
        participants_list = [Player.from_dict(p) for p in td['participants']]
        t.participants = { p.name : p for p in participants_list }
        t.participants_names = [p.name for p in participants_list]
        t.type = td['type']
        return t
