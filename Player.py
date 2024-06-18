class PlayerStatus():
    PLAYING = "Playing"
    DROPPED = "Dropped"
    ELIMINATED = "Eliminated"

class PlayerPunctuation:
    def __init__(self):
        self.points = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0

        self.games_won = 0
        self.total_games = 0
        self.total_matches = 0
        
        self.rate_opponents_points = 0
        self.rate_games_won = 0
        self.rate_opponents_games_won = 0
        
    def print_stats(self):
        stats_msg = ''
        stats_msg += f'Total points: {self.points}\n'
        stats_msg += f'Total rate opponents points: {self.rate_opponents_points}\n'
        stats_msg += f'Total rate games won: {self.rate_games_won}\n'
        stats_msg += f'Total rate opponents games won: {self.rate_opponents_games_won}\n'
        print(stats_msg)

    
class Player:
    def __init__(self, name):
        self.name = name
        self.status = PlayerStatus.PLAYING
    
    def isBye(self):
        return self.name == '-'

    def update_stats(self):
        stats = self.punctuation
        self.punctuation.points = 3*stats.wins + 1*stats.ties + 0*stats.losses
        # todo update everything

    def update_rates(self):
        stats = self.punctuation
        # todo update everything

    def get_stats(self):
        self.update_stats()
        stats = self.punctuation
        return stats.points, stats.rate_opponents_points, stats.rate_games_won, stats.rate_opponents_games_won
    
    def __str__(self):
        return f"Player: {self.name}"
        
    def to_dict(self):
        player_dict = {
            'name' : self.name,
            'status' : self.status
        }
        return player_dict
        
    @classmethod    
    def from_dict(cls, pd):
        p = cls(pd['name'])
        p.status = pd['status']
        return p
