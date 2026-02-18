import os
import requests
from groq import Groq
from datetime import datetime

# 1. Setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
now = datetime.now()
day_name = now.strftime("%A")
full_date = now.strftime("%B %d, %Y")

# 2. Generate Word of the Day with Date Seed & Difficulty Rotation
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are a Filipino language teacher. Rotate difficulty based on the day: "
                    "Mon/Wed/Fri: Simple words for a 6yo (Finlee). "
                    "Tue/Thu: Practical words for a 9yo (Kenzie). "
                    "Sat/Sun: Poetic/Deep words for an 11yo (Fia). "
                    "STRICT LIMITS: Word < 15 chars, Definition < 40 chars, Phrase < 40 chars. "
                    "Format: Word: [Word] | Definition: [Definition] | Phrase: [Phrase]"
                )
            },
            {
                "role": "user", 
                "content": f"Today is {day_name}, {full_date}. Give me a unique, fresh Filipino word for the kids."
            }
        ],
        temperature=1.2 # Boosted for maximum variety
    )
    raw_output = completion.choices[0].message.content.strip()
except Exception:
    raw_output = "Word: Laro | Definition: To play | Phrase: Tayo ay maglaro!"

# 3. Parsing & Hard Trimming for E-ink layout
try:
    parts = raw_output.split("|")
    word_val = parts[0].replace("Word:", "").strip()[:15]
    def_val = parts[1].replace("Definition:", "").strip()[:40]
    phrase_val = parts[2].replace("Phrase:", "").strip()[:40]
except:
    word_val, def_val, phrase_val = "Salamat", "Thank you", "Salamat po!"

# 4. Push to Dot (Action Slot)
url = f"https://dot.mindreset.tech/api/authV2/open/device/{os.environ['DOT_DEVICE_ID']}/text"

payload = {
    "title": f"Salita ng Araw: {word_val}",
    "message": f"{def_val}\n\n'{phrase_val}'",
    "taskKey": "WWmY1iA8LfjJ", # Your new Action Slot
    "refreshNow": True
}

headers = {
    "Authorization": f"Bearer {os.environ['DOT_API_KEY']}",
    "Content-Type": "application/json"
}

res = requests.post(url, json=payload, headers=headers)
print(f"Sent {word_val} (Difficulty: {day_name}). Status: {res.status_code}")
