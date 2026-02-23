import os
import requests
import time
import random
from groq import Groq
from datetime import datetime

# ── Setup ──────────────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
now = datetime.now()
day_name = now.strftime("%A")
full_date = now.strftime("%B %d, %Y")
today = now.strftime("%A, %B %d, %Y")

device_id = os.environ["DOT_DEVICE_ID"]
api_key = os.environ["DOT_API_KEY"]
url = f"https://dot.mindreset.tech/api/authV2/open/device/{device_id}/text"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

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

gen_alpha_figures = [
    # K-pop / Music
    "KATSEYE", "NewJeans", "aespa", "IVE", "TWICE", "Le Sserafim", "BLACKPINK", "MAMAMOO",
    # Western Pop
    "Taylor Swift", "Olivia Rodrigo", "Sabrina Carpenter", "Dua Lipa", "Ariana Grande",
    # Cartoons / Animated Series
    "Bluey", "Hilda", "Kipo", "Anne (Amphibia)", "Luz (The Owl House)",
    "Mabel (Gravity Falls)", "She-Ra",
    # Disney / Pixar
    "Mirabel (Encanto)", "Moana", "Raya", "Mei (Turning Red)", "Asha (Wish)",
    "Merida (Brave)", "Ember (Elemental)",
    # Movies / Studio Ghibli
    "Joy (Inside Out 2)", "Riley (Inside Out 2)", "Matilda",
    "Nimona", "Chihiro (Spirited Away)", "Kiki (Kiki's Delivery Service)",
    # Book Heroines — Classic
    "Anne Shirley (Anne of Green Gables)", "Jo March (Little Women)",
    "Meg Murry (A Wrinkle in Time)", "Mary Lennox (The Secret Garden)",
    "Pippi Longstocking", "Harriet (Harriet the Spy)", "Ramona Quimby",
    # Book Heroines — Middle Grade / YA
    "Nancy Drew", "Annabeth Chase (Percy Jackson)", "Hermione Granger",
    "Thea Stilton", "Stella (Front Desk)"
]

seed_words = [
    "sunrise", "ocean", "mountain", "firefly", "thunder", "bloom", "ember",
    "tide", "spark", "horizon", "echo", "frost", "petal", "storm", "lantern",
    "rainbow", "breeze", "meadow", "crystal", "moonlight", "dewdrop", "canyon",
    "starfish", "blossom", "river", "feather", "compass", "cocoon", "anchor"
]

def push_slot(title, message, signature, task_key, refresh_now=False, label=""):
    print(f"Pushing {label}...")
    res = requests.post(url, headers=headers, json={
        "title": title,
        "message": message,
        "signature": signature,
        "taskKey": task_key,
        "refreshNow": refresh_now
    })
    if res.status_code == 200:
        print(f"  ✓ {label} sent.")
    else:
        print(f"  ✗ {label} failed ({res.status_code}): {res.text}")
    time.sleep(5)


# ── Part 1: Affirmation — Personal Note from Mom & Dad ────────────────────────
print("Generating affirmation...")
random_seed = random.choice(seed_words)
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a supportive parent writing a short note for a child who struggles with school. "
                    "Notes must be between 40-120 characters for a small e-ink screen. "
                    "CRITICAL: Never mention grades, success, or 'having a good day'. "
                    "Focus on internal strength using themes: Safety Net, Release Valve, "
                    "Perspective, Humor, Internal Strength, Authenticity, or Action-Light. "
                    "Pick a DIFFERENT theme every time. Be warm and low-pressure. "
                    "Never write less than 40 characters."
                )
            },
            {
                "role": "user",
                "content": f"Today is {today}. Seed: {random_seed}. Write a unique note for today."
            }
        ],
        temperature=1.1,
        max_tokens=80
    )
    affirmation = completion.choices[0].message.content.strip().replace('"', '')
except Exception as e:
    print(f"Affirmation error: {e}")
    affirmation = "You're more than enough, exactly as you are."

push_slot(
    title="A Note for You",
    message=affirmation,
    signature="Love, Mom and Dad",
    task_key="XOfUEqYdSjTr",
    refresh_now=False,
    label="Affirmation"
)


# ── Part 2: Council + GenAlpha + Tagalog — Night Quote ────────────────────────
print("Generating council content...")
mentors_str = ", ".join(mentor_list)
figures_str = ", ".join(gen_alpha_figures)
random_seed = random.choice(seed_words)
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
                    f"2. GenAlpha: A vibe/quote from ONE of these icons the girls love: [{figures_str}]. "
                    "Focus on confidence, friendship, and sisterhood. No boys, no superheroes.\n"
                    "3. Tagalog: A Filipino word. Mon/Wed/Fri: Simple (6yo level). Tue/Thu: Practical (9yo level). Sat/Sun: Deep (11yo level).\n\n"
                    "STRICT LIMIT: All messages/quotes must be between 40-80 characters. Never under 40 characters.\n"
                    "Format: Mentor: [Q]|[A] || GenAlpha: [Q]|[A] || Tagalog: [Word]|[Def]|[Phrase]"
                )
            },
            {
                "role": "user",
                "content": f"Today is {day_name}, {full_date}. Seed: {random_seed}. Make it fresh and inspiring."
            }
        ],
        temperature=1.2
    )
    raw = completion.choices[0].message.content.strip()
except Exception as e:
    print(f"Council error: {e}")
    raw = "Mentor: Doing your best is a superpower.|Aristotle || GenAlpha: Be your own kind of girl group.|KATSEYE || Tagalog: Masaya|Happy|Masaya ako!"

time.sleep(5)

sections = raw.split("||")

def clean_split(text, prefix):
    return [p.strip() for p in text.replace(prefix, "").strip().split("|")]

try:
    m_parts = clean_split(sections[0], "Mentor:")
    m_q, m_a = m_parts[0], m_parts[1]
    g_parts = clean_split(sections[1], "GenAlpha:")
    g_q, g_a = g_parts[0], g_parts[1]
    t_parts = clean_split(sections[2], "Tagalog:")
    t_w, t_d, t_p = t_parts[0], t_parts[1], t_parts[2]
except Exception:
    m_q, m_a = "You are capable of great things.", "Aristotle"
    g_q, g_a = "Keep shining bright, you've got this!", "KATSEYE"
    t_w, t_d, t_p = "Salamat", "Thank you", "Salamat po!"

push_slot("Daily Wisdom",           m_q[:80], m_a[:80],          "HlzQCJSj_Goo", refresh_now=False, label="Mentor")
push_slot("Today's Vibe",           g_q[:80], g_a[:80],          "WWmY1iA8LfjJ", refresh_now=False, label="GenAlpha")
push_slot(f"Salita ng Araw: {t_w}", f"{t_d}\n\n'{t_p}'", "",    "bF84UsCAfkac", refresh_now=True,  label="Tagalog")


# ── Final Log ──────────────────────────────────────────────────────────────────
print("-" * 40)
print(f"DATE       : {full_date}")
print(f"AFFIRMATION: {affirmation}")
print(f"MENTOR     : {m_a} says: {m_q}")
print(f"VIBE       : {g_a} says: {g_q}")
print(f"TAGALOG    : {t_w} ({t_d}) -> {t_p}")
print("-" * 40)
