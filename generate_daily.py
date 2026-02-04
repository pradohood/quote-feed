import os
import datetime
import textwrap
import time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
# 7.3" E-Ink Resolution (800x480 is standard)
WIDTH, HEIGHT = 800, 480 
WHITE = 255
BLACK = 0

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_content(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{prompt}. Keep it under 180 characters. Kid-friendly for ages 11 and below."
        )
        return response.text.strip()
    except Exception as e:
        print(f"API Error (using backup): {e}")
        return None

def create_png(title, text, filename):
    img = Image.new('L', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Font Logic - Fallback to default if custom fonts aren't found
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
    except:
        title_font = body_font = ImageFont.load_default()

    # Header & Date
    today = datetime.datetime.now().strftime("%A, %b %d")
    draw.text((40, 30), title, font=title_font, fill=BLACK)
    draw.text((WIDTH - 250, 45), today, font=ImageFont.load_default(), fill=BLACK)
    draw.line((40, 100, WIDTH-40, 100), fill=BLACK, width=4)

    # Wrap Text
    lines = textwrap.wrap(text, width=35) 
    y_text = 140
    for line in lines:
        draw.text((40, y_text), line, font=body_font, fill=BLACK)
        y_text += 55

    img.save(filename)
    print(f"SUCCESS: Created {filename}")

# --- TASKS & BACKUPS ---
# This dictionary contains the definitions for your 4 images
tasks = {
    "history.png": {
        "title": "ON THIS DAY",
        "prompt": "Tell me an interesting historical event for today.",
        "backup": "On this day: The world kept spinning! (API connection failed, check back tomorrow!)"
    },
    "animal.png": {
        "title": "ANIMAL FACT",
        "prompt": "Tell me a cool animal fact.",
        "backup": "Did you know? Cats sleep 70% of their lives! (Backup fact - API unavailable)"
    },
    "affirmation.png": {
        "title": "AFFIRMATION",
        "prompt": "Give me a positive kid-friendly affirmation.",
        "backup": "I am capable of solving any problem! (Even technical ones!)"
    },
    "joke.png": {
        "title": "DAD JOKE",
        "prompt": "Tell me a funny dad joke.",
        "backup": "Why did the computer go to the doctor? It had a virus! (Backup joke)"
    }
}

# --- EXECUTION ---
for filename, data in tasks.items():
    print(f"Generating {filename}...")
    
    # Try to get content
    content = get_content(data["prompt"])
    
    # If API fails, use backup
    if not content:
        content = data["backup"]
        
    create_png(data["title"], content, filename)
    
    # Sleep 5s to avoid hitting API rate limits
    time.sleep(5)
