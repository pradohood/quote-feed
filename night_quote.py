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
    "KATSEYE", "NewJeans", "aespa", "IVE", "TWICE", "Le Sserafim", "BLACKPINK", "MAMAMOO",
    "Taylor Swift", "Olivia Rodrigo", "Sabrina Carpenter", "Dua Lipa", "Ariana Grande",
    "Bluey", "Hilda", "Kipo", "Anne (Amphibia)", "Luz (The Owl House)",
    "Mabel (Gravity Falls)", "She-Ra",
    "Mirabel (Encanto)", "Moana", "Raya", "Mei (Turning Red)", "Asha (Wish)",
    "Merida (Brave)", "Ember (Elemental)",
    "Joy (Inside Out 2)", "Riley (Inside Out 2)", "Matilda",
    "Nimona", "Chihiro (Spirited Away)", "Kiki (Kiki's Delivery Service)",
    "Anne Shirley (Anne of Green Gables)", "Jo March (Little Women)",
    "Meg Murry (A Wrinkle in Time)", "Mary Lennox (The Secret Garden)",
    "Pippi Longstocking", "Harriet (Harriet the Spy)", "Ramona Quimby",
    "Nancy Drew", "Annabeth Chase (Percy Jackson)", "Hermione Granger",
    "Thea Stilton", "Stella (Front Desk)"
]

seed_words = [
    "sunrise", "ocean", "mountain", "firefly", "thunder", "bloom", "ember",
    "tide", "spark", "horizon", "echo", "frost", "petal", "storm", "lantern",
    "rainbow", "breeze", "meadow", "crystal", "moonlight", "dewdrop", "canyon",
    "starfish", "blossom", "river", "feather", "compass", "cocoon", "anchor"
]

def clean_text(text):
    return text.replace('\\"', '').replace("\\'", '').replace('"', '').replace("'", '').strip()

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


# ── Part 1: Affirmation ────────────────────────────────────────────────────────
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
                    "Never write less than 40 characters. "
                    "Do NOT wrap output in quotation marks of any kind."
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
    affirmation = clean_text(completion.choices[0].message.content.strip())
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


# ── Part 2: Mentor + GenAlpha + Tagalog ───────────────────────────────────────
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
                    "You are a content creator for 3 Filipino-Chinese sisters (ages 6, 9, 11). "
                    "Every day must feel completely different from the last. Be creative and surprising.\n\n"
                    "1. MENTOR WISDOM\n"
                    f"   Pick ONE person from: [{mentors_str}]\n"
                    "   Do NOT pick the same person two days in a row.\n"
                    "   Translate their core idea into a fresh, punchy 1-sentence truth a child would feel.\n"
                    "   Avoid: generic hustle quotes, 'believe in yourself', 'work hard'.\n"
                    "   Aim for: surprising, specific, a little unexpected. Like a secret only that mentor knows.\n\n"
                    "2. GIRL POWER VIBE\n"
                    f"   Pick ONE icon from: [{figures_str}]\n"
                    "   Write a vibe/quote inspired by their world: confidence, sisterhood, being weird and wonderful.\n"
                    "   Avoid: love songs, boys, generic 'you can do it' energy.\n"
                    "   Aim for: something that makes a girl feel seen and cool.\n\n"
                    "3. SALITA NG ARAW\n"
                    "   Pick a Filipino word that fits the day's energy and their Filipino-Chinese roots.\n"
                    "   Mon/Wed/Fri: Simple and fun (6yo level).\n"
                    "   Tue/Thu: Practical and useful (9yo level).\n"
                    "   Sat/Sun: Deep and meaningful (11yo level). Occasionally include words about\n"
                    "   family, roots, identity, or resilience that resonate with Filipino-Chinese culture.\n"
                    "   The example phrase MUST be written in Tagalog/Filipino, not English.\n"
                    "   Format: [Word]|[English definition]|[Example phrase in Tagalog]\n\n"
                    "STRICT LIMITS:\n"
                    "   - All quotes/messages must be 40-80 characters.\n"
                    "   - Never under 40 characters.\n"
                    "   - Do NOT wrap any output in quotation marks of any kind.\n"
                    "   - Output format: Mentor: [Q]|[A] || GenAlpha: [Q]|[A] || Tagalog: [Word]|[Def]|[Phrase]\n"
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
    raw = "Mentor: Your curiosity is your greatest tool.|Aristotle || GenAlpha: Being different is your superpower.|Mirabel (Encanto) || Tagalog: Tapang|Courage|Kailangan natin ng tapang araw-araw."

time.sleep(5)
sections = raw.split("||")

def clean_split(text, prefix):
    return [clean_text(p) for p in text.replace(prefix, "").strip().split("|")]

try:
    m_parts = clean_split(sections[0], "Mentor:")
    m_q, m_a = m_parts[0], m_parts[1]
    g_parts = clean_split(sections[1], "GenAlpha:")
    g_q, g_a = g_parts[0], g_parts[1]
    t_parts = clean_split(sections[2], "Tagalog:")
    t_w, t_d, t_p = t_parts[0], t_parts[1], t_parts[2]
except Exception:
    m_q, m_a = "Your curiosity is your greatest tool.", "Aristotle"
    g_q, g_a = "Being different is your superpower.", "Mirabel (Encanto)"
    t_w, t_d, t_p = "Tapang", "Courage", "Kailangan natin ng tapang araw-araw."

push_slot("Daily Wisdom",    m_a[:80], m_q[:80],     "HlzQCJSj_Goo", refresh_now=False, label="Mentor")
push_slot("Today's Vibe",    g_a[:80], g_q[:80],     "WWmY1iA8LfjJ", refresh_now=False, label="GenAlpha")
push_slot(f"Salita: {t_w}", f"{t_d}\n\n{t_p}", "",  "bF84UsCAfkac", refresh_now=False, label="Tagalog")


# ── Part 3: Mandarin Word of the Day ──────────────────────────────────────────
print("Generating Mandarin word...")
random_seed = random.choice(seed_words)
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Mandarin teacher for Filipino-Chinese kids ages 6-11.\n"
                    "Each day pick a DIFFERENT Chinese word or character.\n"
                    "Mon/Wed/Fri: HSK 1 - simple, everyday words (6yo level).\n"
                    "Tue/Thu: HSK 2 - practical words (9yo level).\n"
                    "Sat/Sun: HSK 3 - deeper, meaningful words (11yo level). Occasionally pick words\n"
                    "   related to family, identity, or values that resonate with Filipino-Chinese culture.\n"
                    "The example sentence MUST be written in Chinese characters, not pinyin or English.\n"
                    "Do NOT wrap output in quotation marks of any kind.\n\n"
                    "Output format: [Character]|[Pinyin]|[English]|[Example sentence in Chinese]|[HSK level]"
                )
            },
            {
                "role": "user",
                "content": f"Today is {day_name}, {full_date}. Seed: {random_seed}. Pick today's Mandarin word."
            }
        ],
        temperature=1.2,
        max_tokens=60
    )
    ch_raw = clean_text(completion.choices[0].message.content.strip())
    ch_parts = [p.strip() for p in ch_raw.split("|")]
    ch_char, ch_pinyin, ch_english, ch_sentence, ch_level = (
        ch_parts[0], ch_parts[1], ch_parts[2], ch_parts[3], ch_parts[4]
    )
except Exception as e:
    print(f"Mandarin error: {e}")
    ch_char, ch_pinyin, ch_english, ch_sentence, ch_level = "家", "jiā", "Family", "我爱我的家。", "HSK 1"

push_slot(
    title=f"Mandarin: {ch_char} ({ch_pinyin})",
    message=f"{ch_english}\n\n{ch_sentence}",
    signature=ch_level,
    task_key="QFpKgsLeQ0DB",
    refresh_now=False,
    label="Mandarin"
)


# ── Part 4: Capital of the Day ────────────────────────────────────────────────
print("Generating capital of the day...")
random_seed = random.choice(seed_words)
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a fun geography teacher for kids ages 6-11. "
                    "Each day pick a DIFFERENT country and its capital city. "
                    "Vary the continent every day - do not repeat the same region two days in a row. "
                    "Do NOT wrap output in quotation marks of any kind.\n\n"
                    "Output format: [Country]|[Capital]|[Continent]"
                )
            },
            {
                "role": "user",
                "content": f"Today is {day_name}, {full_date}. Seed: {random_seed}. Pick today's country."
            }
        ],
        temperature=1.2,
        max_tokens=30
    )
    cap_raw = clean_text(completion.choices[0].message.content.strip())
    cap_parts = [p.strip() for p in cap_raw.split("|")]
    cap_country, cap_city, cap_continent = cap_parts[0], cap_parts[1], cap_parts[2]
except Exception as e:
    print(f"Capital error: {e}")
    cap_country, cap_city, cap_continent = "Japan", "Tokyo", "Asia"

push_slot(
    title=f"Capital: {cap_country}",
    message=cap_city,
    signature=cap_continent,
    task_key="iYkoqYsMh49D",
    refresh_now=False,
    label="Capital"
)


# ── Part 5: Would You Rather ──────────────────────────────────────────────────
print("Generating Would You Rather...")
random_seed = random.choice(seed_words)
try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You create fun Would You Rather questions for 3 Filipino-Chinese sisters (ages 6, 9, 11). "
                    "Questions must be silly, imaginative, and spark dinner table debate. "
                    "Keep both options fun - no dark, scary, or violent choices. "
                    "Occasionally include Filipino or Chinese cultural references like food, places, or traditions. "
                    "Output must be a single question under 80 characters. "
                    "Format: [Option A] or [Option B]? "
                    "Do NOT wrap output in quotation marks of any kind."
                )
            },
            {
                "role": "user",
                "content": f"Today is {day_name}, {full_date}. Seed: {random_seed}. Write today's Would You Rather."
            }
        ],
        temperature=1.3,
        max_tokens=40
    )
    wyr = clean_text(completion.choices[0].message.content.strip())
except Exception as e:
    print(f"Would You Rather error: {e}")
    wyr = "Eat halo-halo every day or eat dimsum every day?"

push_slot(
    title="Would You Rather?",
    message=wyr,
    signature="Talk at dinner!",
    task_key="IVSWf5TIWugX",
    refresh_now=True,
    label="Would You Rather"
)


# ── Final Log ─────────────────────────────────────────────────────────────────
print("-" * 40)
print(f"DATE       : {full_date}")
print(f"AFFIRMATION: {affirmation}")
print(f"MENTOR     : {m_a} says: {m_q}")
print(f"VIBE       : {g_a} says: {g_q}")
print(f"TAGALOG    : {t_w} ({t_d}) -> {t_p}")
print(f"MANDARIN   : {ch_char} ({ch_pinyin}) = {ch_english} | {ch_sentence} [{ch_level}]")
print(f"CAPITAL    : {cap_city} is the capital of {cap_country} ({cap_continent})")
print(f"WYR        : {wyr}")
print("-" * 40)
