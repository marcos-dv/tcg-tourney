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
        if len(self.rounds) == 0:
            self.generate_round()

    def get_current_round_number(self):
        return len(self.rounds)

    def generate_round(self):
        if len(self.rounds) > 0:
            self.rounds[-1].status = RoundStatus.FINISHED
        # TODO check type of tourney, swiss, etc
        stats = self.get_stats() if len(self.rounds) > 0 else None
        matches = RoundScheduler(self.participants, self.rounds, stats).find_matches()
        new_round = Round()
        new_round.roundMatches = [m for m in matches]
        new_round.set_status(RoundStatus.STARTED)
        self.add_round(new_round)
        
    def undo_last_round(self):
        if len(self.rounds) > 1:
            del self.rounds[-1]
            self.rounds[-1].status = RoundStatus.STARTED
    
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
            
    # see https://blogs.magicjudges.org/rules/mtr/
    def get_stats(self):
        # opponents
        opponents = { p : set() for p in self.participants_names }
        # by match
        match_points = {p:0 for p in self.participants_names}
        win_matches = {p:0 for p in self.participants_names}
        loss_matches = {p:0 for p in self.participants_names}
        draw_matches = {p:0 for p in self.participants_names}
        total_matches = {p:0 for p in self.participants_names}
        # by games
        win_games = {p:0 for p in self.participants_names}
        draw_games = {p:0 for p in self.participants_names}
        total_games = {p:0 for p in self.participants_names}
        game_points = {p:0 for p in self.participants_names}
        
        min_rate = 0.3333
        
        finished_rounds = 0
        # Update personal stats
        for r in self.rounds:
            if r.status != RoundStatus.FINISHED:
                continue
            finished_rounds += 1
            for m in r.roundMatches:
                # add opponent
                opponents[m.player1].add(m.player2)
                opponents[m.player2].add(m.player1)

                # update points
                if m.punctuation1 > m.punctuation2:
                    win_matches[m.player1] += 1
                    loss_matches[m.player2] += 1
                elif m.punctuation2 > m.punctuation1:
                    win_matches[m.player2] += 1
                    loss_matches[m.player1] += 1
                else: # draw
                    draw_matches[m.player1] += 1
                    draw_matches[m.player2] += 1
                # update total matches
                total_matches[m.player1] += 1
                total_matches[m.player2] += 1

                # update games
                win_games[m.player1] += m.punctuation1
                win_games[m.player2] += m.punctuation2
                total_games[m.player1] += m.punctuation1 + m.punctuation2
                total_games[m.player2] += m.punctuation1 + m.punctuation2

                # detect unfinished games...
                # TODO is companion doing this!!??
                if m.punctuation1 <= 1 and m.punctuation2 <= 1:
                    draw_games[m.player1] += 1
                    draw_games[m.player2] += 1
                    total_games[m.player1] += 1
                    total_games[m.player2] += 1
                
        # adjust byes!
        byes = {p:0 for p in self.participants_names}
        for p in self.participants_names:
            byes[p] = finished_rounds - total_matches[p]
            if byes[p] >= 1:
                win_matches[p] += byes[p]
                total_matches[p] += byes[p]

                win_games[p] += 2*byes[p] # win 2-0
                total_games[p] += 2*byes[p] # win 2-0

        # compute match points
        for p in self.participants_names:
            match_points[p] = 3*win_matches[p] + draw_matches[p]

        # compute game points
        for p in self.participants_names:
            game_points[p] = 3*win_games[p] + draw_games[p]

        # TODO when drop is allowed, divide between the number of played rounds by that player!
        match_win_perc = {}
        for p in self.participants_names:
            match_win_perc[p] = max(min_rate, match_points[p] / (3*total_matches[p])) if total_matches[p] != 0 else 0

        game_win_perc = {}
        for p in self.participants_names:
            game_win_perc[p] = max(min_rate, game_points[p] / (3*total_games[p])) if total_games[p] != 0 else 0
            
        # opponent match win perc
        vpo = {p:0 for p in self.participants_names}
        for p in self.participants_names:
            v = 0
            for oppo in opponents[p]:
                v += match_win_perc[oppo]
            vpo[p] = (v/len(opponents[p])) if len(opponents[p]) > 0 else 0

        # opponent match win perc
        jgo = {p:0 for p in self.participants_names}
        for p in self.participants_names:
            v = 0
            for oppo in opponents[p]:
                v += game_win_perc[oppo]
            jgo[p] = (v/len(opponents[p])) if len(opponents[p]) > 0 else 0

        from operator import itemgetter
        def sort_tuples_descending(data):
            sorted_data = sorted(data, key=itemgetter(1, 2, 3, 4), reverse=True)
            return sorted_data
        
        def to_perc(val):
            return str(format(100*val,".2f")) + '%'

        wld = {p:str(win_matches[p]) + '-' + str(loss_matches[p]) + '-' + str(draw_matches[p]) for p in self.participants_names}
        stats_tuples = [(p, match_points[p], wld[p], to_perc(vpo[p]), to_perc(game_win_perc[p]), to_perc(jgo[p])) for p in self.participants_names]
        return sort_tuples_descending(stats_tuples)

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
