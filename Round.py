from Match import Match

class RoundStatus():
    NOT_STARTED = "Not started"
    STARTED = "Started"
    FINISHED = "Finished"

class Round:
    def __init__(self):
        self.roundMatches = []
        self.status = RoundStatus.STARTED  # Default status
    
    def print_matches(self):
        for match in self.roundMatches:
            print(match)
    
    def set_status(self, status):
        self.status = status

    def __str__(self):
        round_details = ""
        for match in self.roundMatches:
                round_details += f"  {match}\n"
        return round_details
        
    def to_dict(self):
        round_dict = {
            'status' : self.status,
            'matches' : [m.to_dict() for m in self.roundMatches]
        }
        return round_dict
        
    @classmethod
    def from_dict(cls, rd):
        r = Round()
        r.status = rd['status']
        r.roundMatches = [Match.from_dict(m) for m in rd['matches']]
        return r
