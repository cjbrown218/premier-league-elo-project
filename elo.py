import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("epl-2025-26-results.csv")

combined = pd.concat([df["Home Team"], df["Away Team"]])
team_names = pd.unique(combined)
ratings = {}
rating_history = {team: [] for team in team_names}

for team in team_names:
    ratings[team]= 1500

def expected_score(rA, rB):
    return 1 / (1 + 10 ** ((rB - rA) / 400))

def parse_result(result_str):
    home_goals, away_goals = result_str.split('-')
    return int(home_goals), int(away_goals)

def update_elo(home_team, away_team, home_goals, away_goals):
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


for index, row_data in df.iterrows():
    home_team = row_data["Home Team"]
    away_team = row_data["Away Team"]
    result_string = row_data["Result"]
    home_goals, away_goals = parse_result(result_string)
    update_elo(home_team, away_team, home_goals, away_goals)
    for team in team_names:
        rating_history[team].append(ratings[team])
    
ratings_table = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
for team, rating in ratings_table:
    print(f"{team}: {rating:.2f}")

round_numbers = [(i // 10) + 1 for i in range(len(df))]
sorted_teams = sorted(team_names)
plt.figure(figsize=(12, 8))
for team in sorted_teams:
    plt.plot(round_numbers, rating_history[team], label=team)
plt.title("Premier League Elo Rating (2025–26 Season)")
plt.xlabel("Round Number")
plt.ylabel("Elo Rating")
plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.show()