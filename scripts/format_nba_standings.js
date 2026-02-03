import fs from "fs";

const ESPN_URL =
  "https://site.web.api.espn.com/apis/v2/sports/basketball/nba/standings";

function pad(str, len) {
  return str.toString().padEnd(len, " ");
}

function formatTeam(team) {
  const rank = pad(team.rank, 2);
  const abbr = pad(team.abbreviation, 3);
  const record = `${team.wins}-${team.losses}`;
  return `${rank} ${abbr} ${record}`;
}

async function main() {
  const res = await fetch(ESPN_URL);
  if (!res.ok) throw new Error("Failed to fetch ESPN standings");

  const data = await res.json();

  const east = [];
  const west = [];

  for (const entry of data.standings.entries) {
    const team = entry.team;
    const stats = Object.fromEntries(
      entry.stats.map(s => [s.name, s.value])
    );

    const formatted = {
      abbreviation: team.abbreviation,
      rank: stats.playoffSeed,
      wins: stats.wins,
      losses: stats.losses
    };

    if (entry.conference.name === "Eastern Conference") {
      east.push(formatted);
    } else if (entry.conference.name === "Western Conference") {
      west.push(formatted);
    }
  }

  east.sort((a, b) => a.rank - b.rank);
  west.sort((a, b) => a.rank - b.rank);

  const output = {
    title: "NBA STANDINGS",
    updated: new Date().toLocaleString("en-PH", {
      timeZone: "Asia/Manila",
      hour12: false
    }),
    east: east.slice(0, 15).map(formatTeam),
    west: west.slice(0, 15).map(formatTeam)
  };

  fs.writeFileSync(
    "nba_standings.json",
    JSON.stringify(output, null, 2)
  );

  console.log("NBA standings formatted successfully");
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
