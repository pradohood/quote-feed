import os
import datetime
import textwrap
import time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# 7.3" E-Ink Resolution (800x480 is standard)
WIDTH, HEIGHT = 800, 480 
WHITE = 255
BLACK = 0

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_content(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{prompt}. Keep it under 180 characters. Kid-friendly for ages 11 and under."
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_png(title, text, filename):
    img = Image.new('L', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Load basic fonts available on Ubuntu runners
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
    except:
        title_font = body_font = ImageFont.load_default()

    # Header
    today = datetime.datetime.now().strftime("%A, %b %d")
    draw.text((40, 30), title, font=title_font, fill=BLACK)
    draw.text((WIDTH - 250, 40), today, font=ImageFont.load_default(), fill=BLACK)
    draw.line((40, 100, WIDTH-40, 100), fill=BLACK, width=4)

    # Content - Wrapped for 7.3" width
    lines = textwrap.wrap(text, width=35) 
    y_text = 140
    for line in lines:
        draw.text((40, y_text), line, font=body_font, fill=BLACK)
        y_text += 55

    img.save(filename)

# Tasks
categories = {
    "history.png": ("ON THIS DAY", "Tell me an interesting historical event for today."),
    "animal.png": ("ANIMAL FACT", "Tell me a cool animal fact."),
    "affirmation.png": ("AFFIRMATION", "Give me a positive kid-friendly affirmation."),
    "joke.png": ("DAD JOKE", "Tell me a funny dad joke.")
}

for filename, (title, prompt) in categories.items():
    content = get_content(prompt)
    if content:
        create_png(title, content, filename)
        print(f"Created {filename}")
    
    # Delay to respect free tier quota
    time.sleep(5)
