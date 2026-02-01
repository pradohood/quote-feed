const fs = require("fs");

const data = JSON.parse(fs.readFileSync("quotes.json", "utf8"));
const quote = data.quotes[data.index];

// escape XML
const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Quote of the Day</title>
    <description>Daily mindset and motivation quote</description>
    <link>https://pradohood.github.io/quote-feed/</link>
    <item>
      <title>${esc(quote.text)}</title>
      <description>— ${esc(quote.author)}</description>
    </item>
  </channel>
</rss>`;

fs.writeFileSync("quotes.xml", xml);

// advance index
data.index = (data.index + 1) % data.quotes.length;
fs.writeFileSync("quotes.json", JSON.stringify(data, null, 2));
