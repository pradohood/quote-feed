import json
import requests
from datetime import datetime

URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

resp = requests.get(URL, timeout=15)
resp.raise_for_status()
raw = resp.json()

games = []

for e in raw.get("events", []):
    status = e["status"]["type"]
    if not status["completed"]:
        continue

    comp = e["competitions"][0]
    teams = comp["competitors"]

    home = next(t for t in teams if t["homeAway"] == "home")
    away = next(t for t in teams if t["homeAway"] == "away")

    winner = home if home["winner"] else away
    loser  = away if home["winner"] else home

    game = {
        "winner": winner["team"]["abbreviation"],
        "winner_score": int(winner["score"]),
        "loser": loser["team"]["abbreviation"],
        "loser_score": int(loser["score"]),
        "season_type": e["season"]["type"],
        "series": comp.get("series", {}).get("summary"),
        "leaders": comp.get("leaders", [])
    }

    games.append(game)

out = {
    "generated_at_utc": datetime.utcnow().isoformat(),
    "games": games
}

with open("nba.json", "w") as f:
    json.dump(out, f, indent=2)
