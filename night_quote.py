import os
import requests
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 1. Generate the quote
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system", 
            "content": "Provide a famous or fictional quote for a 12yo kid. Format: Quote | Author. Keep quote < 80 chars."
        },
        {"role": "user", "content": "Give me tonight's quote."}
    ],
    temperature=0.8
)

# Split the response into Quote and Author
raw_text = completion.choices[0].message.content.strip().replace('"', '')
if "|" in raw_text:
    quote, author = raw_text.split("|")
else:
    quote, author = raw_text, "Inspiration"

# 2. Push to Dot. Quote/0
url = f"https://dot.mindreset.tech/api/authV2/open/device/{os.environ['DOT_DEVICE_ID']}/text"

payload = {
    "title": "Evening Thought",
    "message": quote.strip(),
    "signature": f"— {author.strip()}", # Puts the author in the signature slot
    "taskKey": "night_quote",           # Matches your new task in the Dot App
    "refreshNow": True
}

headers = {
    "Authorization": f"Bearer {os.environ['DOT_API_KEY']}",
    "Content-Type": "application/json"
}

requests.post(url, json=payload, headers=headers)
