from Match import Match
from Round import Round, RoundStatus
from Player import Player, PlayerStatus

# see https://blogs.magicjudges.org/rules/mtr/
def compute_stats(participants_names, rounds):
    # opponents
    opponents = { p : set() for p in participants_names }
    # by match
    match_points = {p:0 for p in participants_names}
    win_matches = {p:0 for p in participants_names}
    loss_matches = {p:0 for p in participants_names}
    draw_matches = {p:0 for p in participants_names}
    total_matches = {p:0 for p in participants_names}
    # by games
    win_games = {p:0 for p in participants_names}
    draw_games = {p:0 for p in participants_names}
    total_games = {p:0 for p in participants_names}
    game_points = {p:0 for p in participants_names}
    
    min_rate = 0.333333333
    
    finished_rounds = 0
    # Update personal stats
    for r in rounds:
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
            total_games[m.player1] += (m.punctuation1 + m.punctuation2)
            total_games[m.player2] += (m.punctuation1 + m.punctuation2)

            # detect unfinished games...
            if m.punctuation1 <= 1 and m.punctuation2 <= 1:
                draw_games[m.player1] += 1
                draw_games[m.player2] += 1
                total_games[m.player1] += 1
                total_games[m.player2] += 1
            
    # adjust byes!
    byes = {p:0 for p in participants_names}
    for p in participants_names:
        # TODO update for dropped and hot insertions (maybe just give byes to hot insertions...)
        byes[p] = finished_rounds - total_matches[p]
        if byes[p] >= 1:
            win_matches[p] += byes[p]
            total_matches[p] += byes[p]

            win_games[p] += 2*byes[p] # win 2-0
            total_games[p] += 2*byes[p] # win 2-0

    # compute match points
    for p in participants_names:
        match_points[p] = 3*win_matches[p] + 1*draw_matches[p]

    # compute game points
    for p in participants_names:
        game_points[p] = 3*win_games[p] + 1*draw_games[p]

    # TODO when drop is allowed, divide between the number of played rounds by that player!
    match_win_perc = {}
    for p in participants_names:
        match_win_perc[p] = max(min_rate, match_points[p] / (3*total_matches[p])) if total_matches[p] != 0 else 0

    game_win_perc = {}
    for p in participants_names:
        game_win_perc[p] = max(min_rate, game_points[p] / (3*total_games[p])) if total_games[p] != 0 else 0
        
    # opponent match win perc
    vpo = {p:0 for p in participants_names}
    for p in participants_names:
        v = 0
        for oppo in opponents[p]:
            v += match_win_perc[oppo]
        vpo[p] = (v/len(opponents[p])) if len(opponents[p]) > 0 else 0

    # opponent match win perc
    jgo = {p:0 for p in participants_names}
    for p in participants_names:
        v = 0
        for oppo in opponents[p]:
            v += game_win_perc[oppo]
        jgo[p] = (v/len(opponents[p])) if len(opponents[p]) > 0 else 0

    from operator import itemgetter
    def sort_tuples_descending(data):
        sorted_data = sorted(data, key=lambda x: (x[1], x[3], x[4], x[5]), reverse=True)
        return sorted_data
    
    def to_perc(val):
        return str(format(100*val,".2f")) + '%'

    wld = {p:str(win_matches[p]) + '-' + str(loss_matches[p]) + '-' + str(draw_matches[p]) for p in participants_names}
    # round to 5 decimals is useful because of comparisons with min_rate
    decimals = 5
    stats_tuples = [(p, match_points[p], wld[p], round(vpo[p],decimals), round(game_win_perc[p],decimals), round(jgo[p],decimals)) for p in participants_names]

    stats_tuples = sort_tuples_descending(stats_tuples) # sort without strings but numbers

    stats_tuples_perc = [ (p,mp,wld,to_perc(vpo),to_perc(gwp),to_perc(jpo)) for (p, mp, wld, vpo, gwp, jpo) in stats_tuples ]
    return stats_tuples_perc


def compute_dominance(names, rounds):
    dominant_arcs = []
    draw_arcs = []
    # Update personal stats
    for r in rounds:
        if r.status != RoundStatus.FINISHED:
           continue
        for m in r.roundMatches:
            # update points
            if m.punctuation1 > m.punctuation2:
                dominant_arcs.append((m.player1, m.player2))
            elif m.punctuation2 > m.punctuation1:
                dominant_arcs.append((m.player2, m.player1))
            else:
                draw_arcs.append((m.player1, m.player2))
    return names, dominant_arcs, draw_arcs

