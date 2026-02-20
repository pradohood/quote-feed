import os
import requests
import time
from groq import Groq
from datetime import datetime

# 1. Initial "Breath" - Wait for previous script (daily_affirmation) to clear
print("Waiting 5 seconds for previous tasks to settle...")
time.sleep(5)

# 2. Setup
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
    print("Requesting content from Groq...")
    mentors_str = ", ".join(mentor_list)
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a content creator for 3 sisters (ages 6, 9, 11). Provide 3 items:\n\n"
                        f"1. Mentor: A kid-translated wisdom nugget from ONE person on this list: [{mentors_str}]. "
                        "Translate the big idea into a simple 1-sentence 'Note from a Friend'. Avoid jargon.\n"
                        "2. GenAlpha: A vibe/quote from icons girls love (KATSEYE, NewJeans, Taylor Swift, Bluey, or Inside Out 2). "
                        "Focus on confidence, friendship, and sisterhood. NO MARVEL/BOYS.\n"
                        "3. Tagalog: A Filipino word. Mon/Wed/Fri: Simple (6yo level). Tue/Thu: Practical (9yo level). Sat/Sun: Deep (11yo level).\n\n"
                        "STRICT LIMIT: All messages/quotes must be under 80 characters.\n"
                        "Format: Mentor: [Q]|[A] || GenAlpha: [Q]|[A] || Tagalog: [Word]|[Def]|[Phrase]"
                    )
                },
                {"role": "user", "content": f"Today is {day_name}, {full_date}. Make it fresh and inspiring."}
            ],
            temperature=1.2
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Mentor: Doing your best is a superpower.|Aristotle || GenAlpha: Be your own kind of girl group.|KATSEYE || Tagalog: Masaya|Happy|Masaya ako!"

# 3. Execution with 5-second gaps
raw = get_ai_content()
time.sleep(5) # Delay after Groq call

sections = raw.split("||")
def clean_split(text, prefix):
    parts = text.replace(prefix, "").strip().split("|")
    return [p.strip() for p in parts]

try:
    m_parts = clean_split(sections[0], "Mentor:")
    m_q, m_a = m_parts[0], m_parts[1]
    g_parts = clean_split(sections[1], "GenAlpha:")
    g_q, g_a = g_parts[0], g_parts[1]
    t_parts = clean_split(sections[2], "Tagalog:")
    t_w, t_d, t_p = t_parts[0], t_parts[1], t_parts[2]
except:
    m_q, m_a = "You are capable of great things.", "Aristotle"
    g_q, g_a = "Keep shining bright!", "KATSEYE"
    t_w, t_d, t_p = "Salamat", "Thank you", "Salamat po!"

# API Pushing
device_id = os.environ["DOT_DEVICE_ID"]
api_key = os.environ["DOT_API_KEY"]
url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/text"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# SLOT 1
print("Pushing Slot 1...")
requests.post(url, headers=headers, json={
    "title": "Daily Wisdom", "message": m_a[:80], "signature": m_q[:80],
    "taskKey": "HlzQCJSj_Goo", "refreshNow": False
})
time.sleep(5)

# SLOT 2
print("Pushing Slot 2...")
requests.post(url, headers=headers, json={
    "title": "Today's Vibe", "message": g_a[:80], "signature": g_q[:80],
    "taskKey": "WWmY1iA8LfjJ", "refreshNow": False
})
time.sleep(5)

# SLOT 4
print("Pushing Slot 4...")
requests.post(url, headers=headers, json={
    "title": f"Salita ng Araw: {t_w}", "message": f"{t_d}\n\n'{t_p}'",
    "taskKey": "bF84UsCAfkac", "refreshNow": True
})

# FINAL LOGS
print("-" * 30)
print(f"DATE: {full_date}")
print(f"SLOT 1 (Mentor): {m_a} says: {m_q}")
print(f"SLOT 2 (Vibe)  : {g_a} says: {g_q}")
print(f"SLOT 4 (Tagalog): {t_w} ({t_d}) -> {t_p}")
print("-" * 30)
