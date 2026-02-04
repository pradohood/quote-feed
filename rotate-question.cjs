const fs = require("fs");

const data = JSON.parse(fs.readFileSync("questions.json", "utf8"));
const index = data.index ?? 0;
const question = data.questions[index];

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Daily Question</title>
    <item>
      <title>${question}</title>
    </item>
  </channel>
</rss>`;

fs.writeFileSync("questions.xml", xml);

data.index = (index + 1) % data.questions.length;
fs.writeFileSync("questions.json", JSON.stringify(data, null, 2));
