from Player import Player

class Match:
    def __init__(self, player1, player2, score1 = None, score2 = None):
        self.player1 = player1
        self.player2 = player2
        self.punctuation1 = score1
        self.punctuation2 = score2
    
    def set_punctuation(self, score1, score2):
        self.punctuation1 = score1
        self.punctuation2 = score2
        
        
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
