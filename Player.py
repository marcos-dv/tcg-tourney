class PlayerStatus():
    PLAYING = "Playing"
    DROPPED = "Dropped"
    ELIMINATED = "Eliminated"
    
class Player:
    def __init__(self, name):
        self.name = name
        self.status = PlayerStatus.PLAYING
    
    def isBye(self):
        return self.name == '-'

    def update_status(self, new_status):
        self.status = new_status

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
