const fs = require("fs");
const path = require("path");

console.log("📂 Current directory:", process.cwd());
console.log("📄 Files:", fs.readdirSync("."));

if (!fs.existsSync("quotes.json")) {
  throw new Error("quotes.json NOT FOUND in repo root");
}

const data = JSON.parse(fs.readFileSync("quotes.json", "utf8"));

if (!data.quotes || data.quotes.length === 0) {
  throw new Error("quotes.json has no quotes");
}

const index = data.index ?? 0;
const quote = data.quotes[index];

// XML escape
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
</rss>
`;

fs.writeFileSync("quotes.xml", xml);
console.log("✅ quotes.xml written");

data.index = (index + 1) % data.quotes.length;
fs.writeFileSync("quotes.json", JSON.stringify(data, null, 2));
console.log("✅ quotes.json index updated");
