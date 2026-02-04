import os
import requests
from groq import Groq

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Generate the message
print("Requesting quote from Groq...")
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system", 
            "content": "Provide an inspiring quote for a child under 12. Fictional characters (Yoda, Dumbledore, etc.) are encouraged. Format: Quote | Author. Keep quote under 80 characters."
        },
        {"role": "user", "content": "Generate tonight's quote."}
    ],
    temperature=0.8
)

raw_output = completion.choices[0].message.content.strip()
print(f"AI Raw Output: {raw_output}")

# 3. Robust Parsing
if "|" in raw_output:
    parts = raw_output.split("|")
    quote = parts[0].strip().replace('"', '')
    author = parts[1].strip().replace('"', '')
else:
    # Fallback if AI misses the separator
    quote = raw_output.replace('"', '')
    author = "Inspiration"

print(f"Parsed Quote: {quote}")
print(f"Parsed Author: {author}")

# 4. Push to Dot. Quote/0
device_id = os.environ["DOT_DEVICE_ID"]
url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/text"

payload = {
    "title": "Evening Thought",
    "message": quote,
    "signature": f"— {author}",
    "refreshNow": True
}

# IMPORTANT: If you couldn't find Task Keys in the app, 
# REMOVE the taskKey line entirely. It will default to the primary Text API slot.
# If you DID find it, add it back below:
# payload["taskKey"] = "night_quote"

headers = {
    "Authorization": f"Bearer {os.environ['DOT_API_KEY']}",
    "Content-Type": "application/json"
}

print("Sending to Dot API...")
res = requests.post(url, json=payload, headers=headers)

print(f"Dot API Status Code: {res.status_code}")
print(f"Dot API Response: {res.text}")
