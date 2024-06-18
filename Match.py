from Player import Player, PlayerPunctuation

class Match:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.punctuation1 = None
        self.punctuation2 = None
    
    def set_punctuation(self, score1, score2):
        self.punctuation1 = score1
        self.punctuation2 = score2
        
        # TODO this logic should go out of here...
        
        # update players stats
        # update games
        """
        self.player1.punctuation.total_games += score1 + score2
        self.player2.punctuation.total_games += score1 + score2

        self.player1.punctuation.games_won += score1
        self.player2.punctuation.games_won += score2

        # update matches
        self.player1.punctuation.total_matches += 1
        self.player2.punctuation.total_matches += 1        
        if score1 > score2:
            self.player1.punctuation.wins += 1
            self.player2.punctuation.losses += 1
        elif score2 > score1:
            self.player2.punctuation.wins += 1
            self.player1.punctuation.losses += 1
        else: # score1 == score2
            self.player1.punctuation.ties += 1
            self.player2.punctuation.ties += 1
        """
        
    def __str__(self):
        return f"{self.player1} vs {self.player2} - Scores: {self.punctuation1}, {self.punctuation2}"

    def to_dict(self):
        match_dict = {
            'player1' : self.player1,
            'player2' : self.player2,
            'punctuation1' : self.punctuation1,
            'punctuation2' : self.punctuation2
        }
        return match_dict
        
    @classmethod
    def from_dict(cls, md):
        m = cls(md['player1'], md['player2'])
        m.punctuation1 = md['punctuation1']
        m.punctuation2 = md['punctuation2']
        return m
