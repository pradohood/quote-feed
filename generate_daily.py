import os
import datetime
import textwrap
import time
from google import genai
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480 
WHITE = 255
BLACK = 0

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_content(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{prompt}. Keep it under 180 characters. Kid-friendly for ages 11 and below."
        )
        return response.text.strip()
    except Exception as e:
        print(f"API Error (using backup): {e}")
        return None

def create_png(title, text, filename):
    img = Image.new('L', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    
    # --- FONT SIZES ---
    try:
        # Title = Big (50)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        
        # Content = Medium (35) - The main focus
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        
        # Date = Small (24) - Readable but secondary
        date_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        title_font = body_font = date_font = ImageFont.load_default()

    # 1. Draw Header
    draw.text((40, 30), title, font=title_font, fill=BLACK)
    draw.line((40, 100, WIDTH-40, 100), fill=BLACK, width=4)

    # 2. Draw Content
    lines = textwrap.wrap(text, width=35) 
    y_text = 140
    for line in lines:
        draw.text((40, y_text), line, font=body_font, fill=BLACK)
        y_text += 50 # Line spacing

    # 3. Draw Date (Centered at Bottom)
    today = datetime.datetime.now().strftime("%A, %b %d, %Y")
    
    # Calculate center position for the date
    bbox = draw.textbbox((0, 0), today, font=date_font)
    text_width = bbox[2] - bbox[0]
    x_date = (WIDTH - text_width) / 2
    
    # Position at y=430 (near bottom)
    draw.text((x_date, 430), today, font=date_font, fill=BLACK)

    img.save(filename)
    print(f"SUCCESS: Created {filename}")

# --- TASKS ---
tasks = {
    "history.png": {
        "title": "ON THIS DAY",
        "prompt": "Tell me an interesting historical event for today. Use the current date in the Philippines",
        "backup": "On this day: The world kept spinning! (API connection failed)"
    },
    "animal.png": {
        "title": "ANIMAL FACT",
        "prompt": "Tell me a cool, animal fact.",
        "backup": "Did you know? Cats sleep 70% of their lives!"
    },
    "affirmation.png": {
        "title": "DAILY AFFIRMATION",
        "prompt": "Give me a positive kid-friendly affirmation. Ideally related to school",
        "backup": "I am capable of solving any problem!"
    },
    "joke.png": {
        "title": "DAD JOKE",
        "prompt": "Tell me a funny dad joke.",
        "backup": "Why did the computer go to the doctor? It had a virus!"
    }
}

# --- RUN ---
for filename, data in tasks.items():
    print(f"Generating {filename}...")
    content = get_content(data["prompt"]) or data["backup"]
    create_png(data["title"], content, filename)
    time.sleep(5)
