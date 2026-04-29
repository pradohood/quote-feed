import os
import datetime
import textwrap
import time
import random
import requests
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
WHITE = 255
BLACK = 0

# Set GROQ_API_KEY in your GitHub Actions secrets
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_content_safe(prompt):
    """Call Groq API with model fallback chain."""
    # All free on Groq's free tier
    model_chain = [
        "llama-3.1-8b-instant",   # fastest, very generous limits
        "llama3-8b-8192",          # fallback
        "gemma2-9b-it",            # second fallback
    ]

    for model_name in model_chain:
        try:
            print(f"  Trying model: {model_name}...")
            response = client.chat.completions.create(
                model=model_name,
                max_tokens=120,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant for kids aged 11 and below. "
                            "Output ONLY the requested text — no intro, no commentary, "
                            "no character count, no quotation marks. "
                            "Keep responses under 180 characters."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  {model_name} failed: {e}")
            time.sleep(1)

    return None


def get_history_fact():
    """Fetch a real event from Wikipedia's On This Day API, then rewrite it for kids."""
    now = datetime.datetime.now()
    month, day = now.month, now.day

    try:
        print("  Fetching from Wikipedia On This Day API...")
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        events = resp.json().get("events", [])

        if not events:
            raise ValueError("No events returned")

        # Pick a random event from the top 10 to add variety
        event = random.choice(events[:10])
        raw_fact = f"In {event['year']}, {event['text']}"
        print(f"  Wikipedia fact: {raw_fact[:80]}...")

    except Exception as e:
        print(f"  Wikipedia API failed: {e}")
        return None

    # Now rewrite it for kids using the slower, smarter model
    try:
        print("  Rewriting for kids with llama-3.3-70b-versatile...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=120,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You rewrite historical facts for kids aged 11 and below. "
                        "Keep it fun, simple, and under 180 characters. "
                        "Output ONLY the rewritten fact — no intro, no commentary, no quotation marks."
                    )
                },
                {
                    "role": "user",
                    "content": f"Rewrite this for kids: {raw_fact}"
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  Groq rewrite failed: {e}, using raw fact")
        # Fall back to raw Wikipedia text trimmed to fit
        return raw_fact[:180]


def create_png(title, text, filename):
    img = Image.new('L', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        body_font  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        date_font  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except Exception:
        title_font = body_font = date_font = ImageFont.load_default()

    draw.text((40, 30), title, font=title_font, fill=BLACK)
    draw.line((40, 100, WIDTH - 40, 100), fill=BLACK, width=4)

    lines = textwrap.wrap(text, width=35)
    y_text = 140
    for line in lines:
        draw.text((40, y_text), line, font=body_font, fill=BLACK)
        y_text += 50

    today = datetime.datetime.now().strftime("%A, %b %d, %Y")
    bbox = draw.textbbox((0, 0), today, font=date_font)
    x_date = (WIDTH - (bbox[2] - bbox[0])) / 2
    draw.text((x_date, 430), today, font=date_font, fill=BLACK)

    img.save(filename)
    print(f"  ✓ Saved {filename}")


# --- TOPICS ---
today_str = datetime.datetime.now().strftime("%B %d")

animal_topics = [
    "ocean creature", "jungle animal", "bird", "insect", "reptile",
    "arctic animal", "dinosaur", "desert animal", "rainforest animal",
    "nocturnal animal", "mammal", "amphibian", "Australian animal",
    "African animal", "strange/weird animal", "endangered animal"
]
joke_topics = [
    "pun", "knock-knock joke", "science joke", "animal joke",
    "school joke", "food joke", "space joke", "sports joke",
    "math joke", "music joke", "history joke", "winter/snow joke",
    "summer/beach joke", "pirate joke", "robot joke"
]
affirm_topics = [
    "confidence", "kindness", "learning", "friendship", "bravery",
    "creativity", "gratitude", "patience", "honesty", "resilience",
    "generosity", "curiosity", "health/strength", "family", "nature"
]

tasks = {
    "history.png": {
        "title": "ON THIS DAY",
        "prompt": f"Tell me one interesting historical event that happened on {today_str}.",
        "backup": "On this day: The world kept spinning! (API unavailable)"
    },
    "animal.png": {
        "title": "ANIMAL FACT",
        "prompt": f"Tell me one cool fact about a {random.choice(animal_topics)}.",
        "backup": "Did you know? Cats sleep 70% of their lives!"
    },
    "affirmation.png": {
        "title": "AFFIRMATION",
        "prompt": f"Give me one positive affirmation for kids about {random.choice(affirm_topics)}.",
        "backup": "I am capable of solving any problem!"
    },
    "joke.png": {
        "title": "DAD JOKE",
        "prompt": f"Tell me one funny kid-friendly dad joke about {random.choice(joke_topics)}.",
        "backup": "Why did the computer go to the doctor? It had a virus!"
    }
}

# --- RUN ---
for filename, data in tasks.items():
    print(f"\n--- Generating {filename} ---")

    if filename == "history.png":
        content = get_history_fact()
    else:
        content = get_content_safe(data["prompt"])

    if not content:
        print("  All models failed. Using backup text.")
        content = data["backup"]

    create_png(data["title"], content, filename)
    time.sleep(1)

print("\nAll done!")
