import os
import requests
from groq import Groq
from datetime import datetime

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Get today's date to force variety
today = datetime.now().strftime("%A, %B %d, %Y")

# 3. Generate the message with variety logic
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are a supportive parent writing a short note for a child who struggles with school. "
                    "Notes must be under 120 characters for a small e-ink screen. "
                    "CRITICAL: Never mention grades, success, or 'having a good day'. "
                    "Focus on internal strength using themes: Safety Net, Release Valve, "
                    "Perspective, Humor, Internal Strength, Authenticity, or Action-Light. "
                    "Pick a DIFFERENT theme every time. Be warm and low-pressure."
                )
            },
            {
                "role": "user", 
                "content": f"Today is {today}. Write a unique note for today."
            }
        ],
        temperature=1.1, # Increased for more variety
        max_tokens=50
    )
    affirmation = completion.choices[0].message.content.strip().replace('"', '')
except Exception as e:
    print(f"Error: {e}")
    affirmation = "You're more than enough, exactly as you are."

# 4. Push to Dot. Quote/0
device_id = os.environ["DOT_DEVICE_ID"]
url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/text"

payload = {
    "title": "A Note for You",
    "message": affirmation,
    "signature": "Love, Mom and Dad",
    "taskKey": "HlzQCJSj_Goo",  # Morning Slot
    "refreshNow": True
}

headers = {
    "Authorization": f"Bearer {os.environ['DOT_API_KEY']}",
    "Content-Type": "application/json"
}

res = requests.post(url, json=payload, headers=headers)

if res.status_code == 200:
    print(f"Success! Sent: {affirmation}")
else:
    print(f"Error {res.status_code}: {res.text}")
