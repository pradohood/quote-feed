import os
import datetime
import textwrap
from google import genai
from PIL import Image, ImageDraw, ImageFont

# 7.3" E-Ink Resolution (Change to 800x480 if your specific model varies)
WIDTH, HEIGHT = 800, 480 
WHITE = 255
BLACK = 0

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_content(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"{prompt}. Keep it under 200 characters. Kid-friendly for ages 11 and under."
    )
    return response.text.strip()

def create_png(title, text, filename):
    # Create monochrome canvas
    img = Image.new('L', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Use default font (or upload a .ttf to your repo for better looks)
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        title_font = body_font = ImageFont.load_default()

    # Draw Header & Date
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    draw.text((40, 30), title, font=title_font, fill=BLACK)
    draw.text((40, 80), date_str, font=body_font, fill=BLACK)
    draw.line((40, 120, WIDTH-40, 120), fill=BLACK, width=3)

    # Wrap and Draw Content
    lines = textwrap.wrap(text, width=45) 
    y_text = 150
    for line in lines:
        draw.text((40, y_text), line, font=body_font, fill=BLACK)
        y_text += 45

    img.save(filename)

# Daily Prompts
tasks = {
    "history.png": ("ON THIS DAY", "Give an interesting kid-friendly historical event for today's date."),
    "animal.png": ("ANIMAL FACT", "Give a cool, surprising animal fact for kids."),
    "affirmation.png": ("DAILY AFFIRMATION", "Give a short positive affirmation for a child."),
    "joke.png": ("DAD JOKE", "Give a funny, clean dad joke for kids.")
}

for file, (title, prompt) in tasks.items():
    content = get_content(prompt)
    create_png(title, content, file)
