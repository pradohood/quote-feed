const fs = require("fs");

const data = JSON.parse(fs.readFileSync("dadjokes.json", "utf8"));
const index = data.index ?? 0;
const joke = data.jokes[index];

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Dad Joke of the Day</title>
    <item>
      <title>${joke.setup}&#10;&#10;${joke.punchline}</title>
    </item>
  </channel>
</rss>`;

fs.writeFileSync("dadjokes.xml", xml);

data.index = (index + 1) % data.jokes.length;
fs.writeFileSync("dadjokes.json", JSON.stringify(data, null, 2));
