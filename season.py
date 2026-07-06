import pandas as pd
import matplotlib.pyplot as plt
import random
df = pd.read_csv("epl-2026-27-fixtures.csv")

ratings = {
    "Arsenal": 1629.00,
    "Man City": 1606.68,
    "Man Utd": 1592.84,
    "Bournemouth": 1552.03,
    "Aston Villa": 1540.82,
    "Liverpool": 1520.38,
    "Sunderland": 1507.48,
    "Brentford": 1506.87,
    "Brighton": 1502.65,
    "Leeds": 1500.19,
    "Fulham": 1493.31,
    "Chelsea": 1483.54,
    "Nott'm Forest": 1482.25,
    "Everton": 1478.29,
    "Newcastle": 1478.12,
    "Crystal Palace": 1463.80,
    "Spurs": 1447.69,
    "Coventry": 1420.00,
    "Ipswich": 1400.00,
    "Hull": 1380.00
}

def expected_score(rA, rB):
    return 1 / (1 + 10 ** ((rB - rA) / 400))

def pred_match(home_team, away_team, ratings):
    home_rating = ratings[home_team] + 50
    away_rating = ratings[away_team]
    E_home = expected_score(home_rating, away_rating)
    E_away = 1 - E_home
    p_draw = 0.20
    p_home_win = E_home * (1 - p_draw)
    p_away_win = E_away * (1 - p_draw)
    p_sum = p_draw + p_home_win + p_away_win
    if p_sum != 1:
        p_draw = p_draw/p_sum
        p_home_win = p_home_win/p_sum
        p_away_win = p_away_win/p_sum
        return p_home_win, p_draw, p_away_win
    else:
        return p_home_win, p_draw, p_away_win

def update_elo(home_team, away_team, home_goals, away_goals, ratings):
    home_rating = ratings[home_team] + 50
    away_rating = ratings[away_team]
    exp_home = expected_score(home_rating, away_rating)
    exp_away = 1 - exp_home

    if home_goals > away_goals:
        actual_home = 1
    elif home_goals < away_goals:
        actual_home = 0
    else:
        actual_home = 0.5

    actual_away = 1 - actual_home
    new_home_rating = home_rating + 20 * (actual_home - exp_home)
    new_away_rating = away_rating + 20 * (actual_away - exp_away)
    ratings[home_team] = new_home_rating - 50
    ratings[away_team] = new_away_rating

def simulate_season(ratings, df):
    expected_points = {team: 0 for team in ratings}

    for index, row in df.iterrows():
        home = row["Home Team"]
        away = row["Away Team"]

        p_home, p_draw, p_away = pred_match(home, away, ratings)

        EP_home = 3 * p_home + p_draw
        EP_away = 3 * p_away + p_draw
        expected_points[home] += EP_home
        expected_points[away] += EP_away

        r = random.random()
        if r < p_home:
            update_elo(home, away, 1, 0, ratings)
        elif r < p_home + p_draw:
            update_elo(home, away, 0, 0, ratings)
        else:
            update_elo(home, away, 0, 1, ratings)

    sorted_table = sorted(expected_points.items(), key=lambda x: x[1], reverse=True)
    return sorted_table

num_sims = 10000
title_counts = {team: 0 for team in ratings}
top4_counts = {team: 0 for team in ratings}
relegation_counts = {team: 0 for team in ratings}
title_prob = {}
top4_prob = {}
releg_prob = {}

finish_counts = {
    team: {pos: 0 for pos in range(1, 21)}
    for team in ratings
}

for sim in range(num_sims):
    sim_ratings = ratings.copy()
    final_table = simulate_season(sim_ratings, df)

    champ = final_table[0][0]
    top4_list = [team for team, pts in final_table[0:4]]
    relegated_list = [team for team, pts in final_table[-3:]]

    title_counts[champ] += 1
    for team in top4_list:
        top4_counts[team] += 1
    for team in relegated_list:
        relegation_counts[team] += 1

    for position, (team, pts) in enumerate(final_table, start=1):
        finish_counts[team][position] += 1

finish_prob = {
    team: {pos: finish_counts[team][pos] / num_sims for pos in range(1, 21)}
    for team in ratings
}


team_order = list(ratings.keys())
heatmap_matrix = [
    [finish_prob[team][pos] for pos in range(1, 21)]
    for team in team_order
]

plt.imshow(heatmap_matrix, cmap="Blues")
plt.colorbar()
plt.xticks(range(20), range(1, 21))
plt.yticks(range(len(team_order)), team_order)
plt.title("Finishing Position Probability Heatmap")
plt.xlabel("Position")
plt.ylabel("Team")
plt.show()

for team in ratings:
    title_prob[team] = title_counts[team] / num_sims
    top4_prob[team] = top4_counts[team] / num_sims
    releg_prob[team] = relegation_counts[team] / num_sims

print("Team                Title %    Top 4 %    Relegation %")
for team in ratings:
    print(f"{team:15}  {title_prob[team]*100:6.2f}%   {top4_prob[team]*100:6.2f}%   {releg_prob[team]*100:6.2f}%")
