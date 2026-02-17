import os
import requests
from groq import Groq
from datetime import datetime

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Get today's date to use as a 'Seed' for variety
today = datetime.now().strftime("%A, %B %d, %Y")

# 3. Generate the quote
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are a diverse quote generator for a 12-year-old kid. "
                    "To prevent repetition, randomly choose a focus for today from: "
                    "[Classic Sci-Fi, Modern Animation, Historical Inventors, Video Game Heroes, "
                    "Nature/Space, or Mythological Wisdom]. "
                    "Format: Quote | Author. Keep quote under 120 characters."
                )
            },
            {
                "role": "user", 
                "content": f"Today is {today}. Provide a fresh, unique, and surprising quote."
            }
        ],
        temperature=1.2 # Higher temperature = more randomness
    )
    raw_output = completion.choices[0].message.content.strip()
    print(f"AI Output: {raw_output}")
except Exception as e:
    print(f"Error calling Groq: {e}")
    raw_output = "You are capable of amazing things. | Inspiration"

# 4. Parsing & Cleaning
if "|" in raw_output:
    parts = raw_output.split("|")
    quote = parts[0].strip()
    author = parts[1].strip()
else:
    quote = raw_output
    author = "Inspiration"

# Clean strings to avoid syntax errors
clean_quote = quote.replace('"', '')
clean_author = author.replace('"', '')

final_message = clean_quote
final_signature = f"- {clean_author}"

# 5. Push to Dot. Quote/0 using DOT_API_KEY_2
device_id = os.environ["DOT_DEVICE_ID"]
url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/text"

payload = {
    "title": "Evening Thought",
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
except Exception as e:
    print(f"Connection Error: {e}")
