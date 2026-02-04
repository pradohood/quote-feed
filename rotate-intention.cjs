const fs = require("fs");

const data = JSON.parse(fs.readFileSync("intentions.json", "utf8"));
const index = data.index ?? 0;
const intention = data.intentions[index];

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Daily Intention</title>
    <item>
      <title>TODAY&#10;${intention}</title>
    </item>
  </channel>
</rss>`;

fs.writeFileSync("intentions.xml", xml);

data.index = (index + 1) % data.intentions.length;
fs.writeFileSync("intentions.json", JSON.stringify(data, null, 2));
