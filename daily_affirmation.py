import os
import requests
from groq import Groq

# 1. Setup Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Generate the message with all your custom themes
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system", 
            "content": (
                "You are a supportive parent writing a short note for a child who struggles with school. "
                "Notes must be under 60 characters and fit on a small e-ink screen. "
                "CRITICAL: Never mention grades, studying, success, or 'having a good day at school'. "
                "Focus on internal strength and being in their corner using these themes:\n"
                "- Safety Net: 'No matter what happens, I'm on your team.'\n"
                "- Release Valve: 'It's okay to have a meh day. Just be kind.'\n"
                "- Perspective: 'School is just a small part of your big world.'\n"
                "- Humor: 'Count how many times the teacher says um.'\n"
                "- Internal Strength: 'You are more than a test score.' / 'Your brain is a powerhouse.'\n"
                "- Authenticity: 'Be messy. Be real. Be you.'\n"
                "- Action-Light: 'Focus on the done, not the do.' / 'Deep breaths. You're doing great.'\n"
                "Generate one unique, warm, and low-pressure note."
            )
        },
        {
            "role": "user", 
            "content": "Write today's note."
        }
    ],
    temperature=0.8,
    max_tokens=50
)

# Clean up the response
affirmation = completion.choices[0].message.content.strip().replace('"', '')

# 3. Push to Dot. Quote/0 (296x152)
device_id = os.environ["DOT_DEVICE_ID"]
url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/text"

payload = {
    "title": "A Note for You",
    "message": affirmation,
    "signature": "Love, Dad",
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
