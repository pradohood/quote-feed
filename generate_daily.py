import os
import datetime
import textwrap
import time
import random 
from google import genai
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480 
WHITE = 255
BLACK = 0

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_content_safe(prompt):
    # Try Lite first (Cheap), then Flash Latest (Reliable)
    model_chain = ["gemini-2.0-flash-lite-001", "gemini-flash-latest"]
    
    for model_name in model_chain:
        try:
            print(f"Attempting with model: {model_name}...")
            
            # UPDATED PROMPT: "Strictly output only the content" removes side comments
            final_prompt = (
                f"{prompt} "
                "Keep it under 180 characters. "
                "Strictly output ONLY the requested text. "
                "No introductory phrases, no conversational filler, no character count. "
                "Kid-friendly for ages 11 and below."
            )
            
            response = client.models.generate_content(
                model=model_name,
                contents=final_prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            time.sleep(1)
            
    return None 

def create_png(title, text, filename):
    img = Image.new('L', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        date_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        title_font = body_font = date_font = ImageFont.load_default()

    draw.text((40, 30), title, font=title_font, fill=BLACK)
    draw.line((40, 100, WIDTH-40, 100), fill=BLACK, width=4)

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
    print(f"SUCCESS: Created {filename}")

# --- EXPANDED TOPICS LIST ---
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
        "prompt": f"Tell me an interesting historical event that happened on {today_str}.",
        "backup": "On this day: The world kept spinning! (API Quota Hit)"
    },
    "animal.png": {
        "title": "ANIMAL FACT",
        "prompt": f"Tell me a cool animal fact about a {random.choice(animal_topics)}.",
        "backup": "Did you know? Cats sleep 70% of their lives!"
    },
    "affirmation.png": {
        "title": "AFFIRMATION",
        "prompt": f"Give me a positive kid-friendly affirmation about {random.choice(affirm_topics)}.",
        "backup": "I am capable of solving any problem!"
    },
    "joke.png": {
        "title": "DAD JOKE",
        "prompt": f"Tell me a funny dad joke about {random.choice(joke_topics)}.",
        "backup": "Why did the computer go to the doctor? It had a virus!"
    }
}

# --- RUN ---
for filename, data in tasks.items():
    print(f"--- Generating {filename} ---")
    
    content = get_content_safe(data["prompt"])
    
    if not content:
        print("All models failed. Using BACKUP text.")
        content = data["backup"]
        
    create_png(data["title"], content, filename)
    
    print("Waiting 20 seconds...")
    time.sleep(20)
