import os
import requests
from groq import Groq
from datetime import datetime

# 1. Setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
now = datetime.now()
day_name = now.strftime("%A")
full_date = now.strftime("%B %d, %Y")

# Your Curated Council
mentor_list = [
    "Albert Einstein", "Abraham Lincoln", "Aristotle", "Benjamin Franklin", "Bill Gates",
    "Brené Brown", "Bruce Lee", "Buddha", "Cal Newport", "Charlie Munger", "Confucius",
    "Dale Carnegie", "Eleanor Roosevelt", "Elon Musk", "Epictetus", "Friedrich Nietzsche",
    "George Washington", "Henry David Thoreau", "James Clear", "Jeff Bezos", "Jim Rohn",
    "Jocko Willink", "John Wooden", "Jordan Peterson", "Lao Tzu", "Leonardo da Vinci",
    "Malcolm X", "Marcus Aurelius", "Mark Twain", "Martin Luther King Jr.", "Maya Angelou",
    "Napoleon Hill", "Naval Ravikant", "Oprah Winfrey", "Oscar Wilde", "Paulo Coelho",
    "Peter Drucker", "Plato", "Ralph Waldo Emerson", "Ray Dalio", "Robin Sharma",
    "Ryan Holiday", "Seneca", "Seth Godin", "Simon Sinek", "Socrates", "Steve Jobs",
    "Sun Tzu", "Theodore Roosevelt", "Tim Ferriss", "Tony Robbins", "Vince Lombardi",
    "Warren Buffett", "William James", "Winston Churchill", "Zig Ziglar"
]

def get_ai_content():
    mentors_str = ", ".join(mentor_list)
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a content creator for kids (ages 6-11). Provide 3 items:\n\n"
                        f"1. Mentor: A kid-translated quote from ONE person on this list: [{mentors_str}].\n"
                        "2. GenAlpha: A quote or vibe from a character or icon kids love (Bluey, Minecraft, Taylor Swift, Spider-Man, etc.).\n"
                        "3. Tagalog: A fun Filipino word (Mon/Wed/Fri: 6yo level, Tue/Thu: 9yo level, Sat/Sun: 11yo level).\n\n"
                        "Format: Mentor: [Q]|[A] || GenAlpha: [Q]|[A] || Tagalog: [Word]|[Def]|[Phrase]"
                    )
                },
                {"role": "user", "content": f"Today is {day_name}, {full_date}. Make it fresh!"}
            ],
            temperature=1.2
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return "Mentor: Be kind.|Plato || GenAlpha: For real life?|Bluey || Tagalog: Masaya|Happy|Masaya ako!"

# 2. Parse & Push
raw = get_ai_content()
sections = raw.split("||")

def clean_split(text, prefix):
    return [item.strip() for item in text.replace(prefix, "").strip().split("|")]

m_q, m_a = clean_split(sections[0], "Mentor:")
g_q, g_a = clean_split(sections[1], "GenAlpha:")
t_w, t_d, t_p = clean_split(sections[2], "Tagalog:")

url = f"https://dot.mindreset.tech/api/authV2/open/device/{os.environ['DOT_DEVICE_ID']}/text"
headers = {"Authorization": f"Bearer {os.environ['DOT_API_KEY']}", "Content-Type": "application/json"}

# SLOT 1: The Mentor Mix
requests.post(url, headers=headers, json={
    "title": "Daily Wisdom",
    "message": m_q[:80], "signature": f"- {m_a}",
    "taskKey": "HlzQCJSj_Goo", "refreshNow": False
})

# SLOT 2: The Gen Alpha Slot
requests.post(url, headers=headers, json={
    "title": "Today's Vibe",
    "message": g_q[:80], "signature": f"- {g_a}",
    "taskKey": "WWmY1iA8LfjJ", "refreshNow": False
})

# SLOT 4: Filipino Word
requests.post(url, headers=headers, json={
    "title": f"Salita ng Araw: {t_w}",
    "message": f"{t_d}\n\n'{t_p}'",
    "taskKey": "bF84UsCAfkac", "refreshNow": True
})
