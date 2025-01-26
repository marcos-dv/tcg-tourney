from Player import Player
from Match import Match
from Round import Round
import random
import time

class PairingScheduler:
    
    # Initialize the PairingScheduler with players, rounds, stats, and an optional seed.
    def __init__(self, players, rounds, stats=None, seed=None):
        # Initialize the set of opponents for each player based on the given rounds, in order to not rematch players
        opponents = { p.name : set() for p in players }
        for r in rounds:
            for m in r.roundMatches:
                opponents[m.player1].add(m.player2)
                opponents[m.player2].add(m.player1)
        self.opponents = opponents

        # TODO precompute this...
        if stats is None:
            self.points = { p.name : 0 for p in players }
        else:
            self.points = { name:points for (name, points, wld, vpo, jg, jgo) in stats }

        # Set a random seed if provided, else use the current time
        if seed == None:
            seed = time.time()
        random.seed(seed + len(rounds))

        # Shuffle the list
        random_players = [p.name for p in players]
        random.shuffle(random_players)
        ordered_players = sorted(random_players, key=lambda x: self.points[x], reverse=True)
        self.players = ordered_players
        # players done
        done = { p:False for p in ordered_players }
        self.done = done

        self.found_matches = []

    # Deprecated
    # Find matches by pairing players sequentially. Adds a "Bye" if players are odd.
    # Match in order, player 1 with player 2, and so on
    @classmethod
    def find_matches_v0(self, players):
        found_matches = []

        if len(players) % 2 == 1: # add Bye
            players.append(Player('-'))

        i = 0
        while i < len(players):
            for j in range(i+1,len(players)):
                # is feasible
                if players[i] != players[j]:
                    m = Match(players[i], players[j])
                    found_matches.append(m)
                    break
            i += 2
        return found_matches

    # Deprecated
    @classmethod
    def find_matches_v1(self, players, rounds):
        found_matches = []

        i = 0
        while i < len(players):
            for j in range(i+1,len(players)):
                # is feasible
                if players[i].name != players[j].name:
                    m = Match(players[i].name, players[j].name)
                    found_matches.append(m)
                    break
            i += 2
        return found_matches

    # Recursive backtracking method to find feasible matchings while avoiding repeated opponents
    # TODO version with relax opponents constraint
    def bt(self, i=0):
        n = len(self.players)
        if i >= n:
            return 2*len(self.found_matches) >= n-1 and 2*len(self.found_matches) <= n 

        if self.done[self.players[i]]:
            return self.bt(i+1)

        # Finding pair for player i
        for j in range(i+1, n):
            # Skip players who are already matched or have faced each other before
            if self.done[self.players[j]] \
                or self.players[j] in self.opponents[self.players[i]]:
                continue

            # Pair players i and j
            self.done[self.players[i]] = True
            self.done[self.players[j]] = True
            self.found_matches.append((self.players[i], self.players[j]))
            ret = self.bt(i+1)
            # ret = True, everything succeed
            # no need to try other combinations
            if ret:
            	return True

            # Backtrack: undo the pairing and try another combination
            self.done[self.players[i]] = False
            self.done[self.players[j]] = False
            pop_matches = [m for m in self.found_matches if self.players[i] not in m]
            self.found_matches = pop_matches
            
        # Attempt to proceed to the next player if no valid match is found
        return self.bt(i+1)

    # Find matches using backtracking and print the results
    def find_matches(self):
        found = self.bt()
        if not found:
            print('Critical error: no feasible matchings were found')
        print('There are ', len(self.found_matches), ' matches and ', len(self.players), ' players')
        return [ Match(p1, p2) for p1, p2 in self.found_matches ]

