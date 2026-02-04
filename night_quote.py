import os
import requests
from groq import Groq

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Generate the quote
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system", 
            "content": "Provide an inspiring quote for a child < 12. Fictional characters (Yoda, Dumbledore, etc.) are great. Format: Quote | Author. Keep quote < 80 chars."
        },
        {"role": "user", "content": "Generate tonight's quote."}
    ]
)

raw_output = completion.choices[0].message.content.strip()

# Parsing logic
if "|" in raw_output:
    parts = raw_output.split("|")
    quote, author = parts[0].strip(), parts[1].strip()
else:
    quote, author = raw_output, "Inspiration"

# 3. Push to Dot. Quote/0 using KEY 2
url = f"https://dot.mindreset.tech/api/authV2/open/device/{os.environ['DOT_DEVICE_ID']}/text"

payload = {
    "title": "Quote of the Day",
    "message": quote.replace('"', ''),
    "signature": f"— {author.replace('"', '')}",
    "refreshNow": True
}

headers = {
    "Authorization": f"Bearer {os.environ['DOT_API_KEY_2']}", # Using the 2nd key
    "Content-Type": "application/json"
}

requests.post(url, json=payload, headers=headers)
