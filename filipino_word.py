import os
import requests
from groq import Groq
from datetime import datetime

# 1. Setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# Get the day of the week and full date
now = datetime.now()
day_name = now.strftime("%A")
full_date = now.strftime("%B %d, %Y")

# 2. Generate Word of the Day with Date Seed
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are a Filipino language teacher. Rotate difficulty: "
                    "Mon/Wed/Fri: Simple words for a 6yo. "
                    "Tue/Thu: Practical words for a 9yo. "
                    "Sat/Sun: Poetic/Deep words for an 11yo. "
                    "STRICT LIMITS: Word < 15 chars, Definition < 40 chars, Phrase < 40 chars. "
                    "Format: Word: [Word] | Definition: [Definition] | Phrase: [Phrase]"
                )
            },
            {
                "role": "user", 
                "content": f"Today is {day_name}, {full_date}. Give me a unique word."
            }
        ],
        temperature=1.1 # High variety
    )
    raw_output = completion.choices[0].message.content.strip()
except Exception:
    raw_output = "Word: Laro | Definition: To play | Phrase: Tayo ay maglaro!"

# 3. Parsing & Hard Trimming
try:
    parts = raw_output.split("|")
    # We strip and slice to ensure it NEVER breaks the e-ink layout
    word_val = parts[0].replace("Word:", "").strip()[:15]
    def_val = parts[1].replace("Definition:", "").strip()[:40]
    phrase_val = parts[2].replace("Phrase:", "").strip()[:40]
except:
    word_val, def_val, phrase_val = "Kaibigan", "Friend", "Mabuting kaibigan."

# 4. Push to Dot (Morning Slot)
url = f"https://dot.mindreset.tech/api/authV2/open/device/{os.environ['DOT_DEVICE_ID']}/text"

payload = {
    "title": f"Salita ng Araw: {word_val}",
    "message": f"{def_val}\n\n'{phrase_val}'",
    "taskKey": "HlzQCJSj_Goo", 
    "refreshNow": True
}

headers = {
    "Authorization": f"Bearer {os.environ['DOT_API_KEY']}",
    "Content-Type": "application/json"
}

res = requests.post(url, json=payload, headers=headers)
print(f"Sent {word_val} for {day_name}. Status: {res.status_code}")
