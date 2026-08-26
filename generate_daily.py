import os
import sys
import time
import random
import datetime
import textwrap
import traceback

from groq import Groq
from PIL import Image, ImageDraw, ImageFont

SCRIPT_VERSION = "v7-diagnostic"
print(f"=== generate_daily.py {SCRIPT_VERSION} ===", flush=True)

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
WHITE = 255
BLACK = 0

FAST_MODEL = "openai/gpt-oss-20b"
SMART_MODEL = "openai/gpt-oss-120b"

# Philippine Time = UTC+8
PHT = datetime.timezone(datetime.timedelta(hours=8))


def now_pht():
    return datetime.datetime.now(tz=PHT)


api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY is not set!", flush=True)
    sys.exit(1)
print(f"API key found: {api_key[:8]}...", flush=True)

client = Groq(api_key=api_key)


def call_model(model_name, system_prompt, user_prompt):
    """One API call. Returns the text, or None with the reason printed."""
    kwargs = {
        "model": model_name,
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    # reasoning_effort is only valid on gpt-oss models; retry without it if rejected
    for attempt_kwargs in (dict(kwargs, reasoning_effort="low"), kwargs):
        try:
            response = client.chat.completions.create(**attempt_kwargs)
        except TypeError as e:
            print(f"  SDK rejected a parameter ({e}); retrying without it.", flush=True)
            continue
        except Exception:
            print(f"  EXCEPTION on {model_name}:", flush=True)
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            return None

        choice = response.choices[0]
        text = (choice.message.content or "").strip()
        if text:
            return text

        print(f"  {model_name} returned EMPTY content "
              f"(finish_reason={choice.finish_reason}).", flush=True)
        return None

    return None


def get_content_safe(system_prompt, user_prompt):
    """Try the fast model, then the smart one."""
    for model_name in (FAST_MODEL, SMART_MODEL):
        print(f"  Trying model: {model_name}...", flush=True)
        text = call_model(model_name, system_prompt, user_prompt)
        if text:
            return text
        time.sleep(1)
    return None


KID_SYSTEM = (
    "You are a helpful assistant for kids aged 11 and below. "
    "Output ONLY the requested text — no intro, no commentary, "
    "no character count, no quotation marks. "
    "Keep responses under 180 characters."
)

HISTORY_SYSTEM = (
    "You pick fun historical facts for kids aged 11 and below. "
    "AVOID: battles, wars, treaties, political elections, or anything violent. "
    "PREFER: space missions, cool inventions, amazing animals, sports records, "
    "fun world firsts, popular movies/games/toys launched, or surprising science "
    "discoveries. Only share events you are highly confident happened on the exact "
    "date. Write like you're excitedly telling a friend — fun and simple. "
    "Under 180 characters. Output ONLY the fact, no intro, no quotation marks."
)


def get_history_fact():
    today_str = now_pht().strftime("%B %d")
    print(f"  Asking {SMART_MODEL} for history fact...", flush=True)
    return call_model(
        SMART_MODEL,
        HISTORY_SYSTEM,
        f"What's a fun, kid-friendly thing that happened on {today_str} in history? "
        "No wars or battles please!",
    )


def create_png(title, text, filename):
    img = Image.new("L", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        body_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        date_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except Exception:
        title_font = body_font = date_font = ImageFont.load_default()

    draw.text((40, 30), title, font=title_font, fill=BLACK)
    draw.line((40, 100, WIDTH - 40, 100), fill=BLACK, width=4)

    y_text = 140
    for line in textwrap.wrap(text, width=35):
        draw.text((40, y_text), line, font=body_font, fill=BLACK)
        y_text += 50

    today = now_pht().strftime("%A, %b %d, %Y")
    bbox = draw.textbbox((0, 0), today, font=date_font)
    x_date = (WIDTH - (bbox[2] - bbox[0])) / 2
    draw.text((x_date, 430), today, font=date_font, fill=BLACK)

    img.save(filename)
    print(f"  Saved {filename}", flush=True)


# --- TOPICS ---
animal_topics = [
    "ocean creature", "jungle animal", "bird", "insect", "reptile",
    "arctic animal", "dinosaur", "desert animal", "rainforest animal",
    "nocturnal animal", "mammal", "amphibian", "Australian animal",
    "African animal", "strange/weird animal", "endangered animal",
]
joke_topics = [
    "pun", "knock-knock joke", "science joke", "animal joke",
    "school joke", "food joke", "space joke", "sports joke",
    "math joke", "music joke", "history joke", "winter/snow joke",
    "summer/beach joke", "pirate joke", "robot joke",
]
affirm_topics = [
    "confidence", "kindness", "learning", "friendship", "bravery",
    "creativity", "gratitude", "patience", "honesty", "resilience",
    "generosity", "curiosity", "health/strength", "family", "nature",
]

tasks = {
    "history.png": {
        "title": "ON THIS DAY",
        "prompt": None,  # handled by get_history_fact
        "backup": "On this day: The world kept spinning!",
    },
    "animal.png": {
        "title": "ANIMAL FACT",
        "prompt": f"Tell me one cool fact about a {random.choice(animal_topics)}.",
        "backup": "Did you know? Cats sleep 70% of their lives!",
    },
    "affirmation.png": {
        "title": "AFFIRMATION",
        "prompt": f"Give me one positive affirmation for kids about {random.choice(affirm_topics)}.",
        "backup": "I am capable of solving any problem!",
    },
    "joke.png": {
        "title": "DAD JOKE",
        "prompt": f"Tell me one funny kid-friendly dad joke about {random.choice(joke_topics)}.",
        "backup": "Why did the computer go to the doctor? It had a virus!",
    },
}

# --- RUN ---
failures = 0
for filename, data in tasks.items():
    print(f"\n--- Generating {filename} ---", flush=True)

    if filename == "history.png":
        content = get_history_fact()
    else:
        content = get_content_safe(KID_SYSTEM, data["prompt"])

    if not content:
        failures += 1
        print("  Falling back to backup text.", flush=True)
        content = data["backup"]

    create_png(data["title"], content, filename)
    time.sleep(2)

print(f"\nDone. {len(tasks) - failures}/{len(tasks)} cards used live content.", flush=True)
