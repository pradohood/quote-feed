import os
import requests
from groq import Groq

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Generate the quote
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": "Provide an inspiring quote for a child under 12. Fictional characters are great. Format: Quote | Author. Keep quote under 80 chars."
            },
            {"role": "user", "content": "Generate tonight's quote."}
        ],
        temperature=0.8
    )
    raw_output = completion.choices[0].message.content.strip()
    print(f"AI Output: {raw_output}")
except Exception as e:
    print(f"Error calling Groq: {e}")
    raw_output = "You are capable of amazing things. | Inspiration"

# 3. Robust Parsing & Cleaning
# We split the quote and author first
if "|" in raw_output:
    parts = raw_output.split("|")
    quote = parts[0].strip()
    author = parts[1].strip()
else:
    quote = raw_output
    author = "Inspiration"

# We clean the text on separate lines to avoid f-string SyntaxErrors
clean_quote = quote.replace('"', '')
clean_author = author.replace('"', '')

# Build final strings for the payload
final_message = clean_quote
final_signature = f"- {clean_author}"

# 4. Push to Dot. Quote/0 using DOT_API_KEY_2
device_id = os.environ["DOT_DEVICE_ID"]
url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/text"

payload = {
    "title": "Quote of the Day",
    "message": final_message,
    "signature": final_signature,
    "refreshNow": True
}

headers = {
    "Authorization": f"Bearer {os.environ['DOT_API_KEY_2']}",
    "Content-Type": "application/json"
}

try:
    res = requests.post(url, json=payload, headers=headers)
    print(f"Dot API Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Connection Error: {e}")
