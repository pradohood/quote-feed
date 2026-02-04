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

def get_content_safe(prompt):
    # LIST OF MODELS TO TRY IN ORDER
    # 1. Lite (Best for quotas)
    # 2. Flash Latest (Stable 1.5 alias found in your list)
    model_chain = ["gemini-2.0-flash-lite-001", "gemini-flash-latest"]
    
    for model_name in model_chain:
        try:
            print(f"Attempting with model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=f"{prompt}. Keep it under 180 characters. Kid-friendly for ages 11 and below."
            )
            return response.text.strip()
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            # Loop continues to the next model...
            time.sleep(1)
            
    return None # Triggers backup text if ALL models fail

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

# --- TASKS ---
tasks = {
    "history.png": {
        "title": "ON THIS DAY",
        "prompt": "Tell me an interesting historical event for today.",
        "backup": "On this day: The world kept spinning! (API Quota Hit - Resetting soon!)"
    },
    "animal.png": {
        "title": "ANIMAL FACT",
        "prompt": "Tell me a cool animal fact.",
        "backup": "Did you know? Cats sleep 70% of their lives! (Backup Fact)"
    },
    "affirmation.png": {
        "title": "AFFIRMATION",
        "prompt": "Give me a positive kid-friendly affirmation.",
        "backup": "I am capable of solving any problem! (Backup Affirmation)"
    },
    "joke.png": {
        "title": "DAD JOKE",
        "prompt": "Tell me a funny dad joke.",
        "backup": "Why did the computer go to the doctor? It had a virus! (Backup Joke)"
    }
}

# --- RUN ---
for filename, data in tasks.items():
    print(f"--- Generating {filename} ---")
    
    # This will try Lite -> Flash Latest -> Backup
    content = get_content_safe(data["prompt"])
    
    if not content:
        print("All models failed. Using BACKUP text.")
        content = data["backup"]
        
    create_png(data["title"], content, filename)
    
    print("Waiting 20 seconds...")
    time.sleep(20)
