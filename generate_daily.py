import os
import datetime
import textwrap
from google import genai
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480  # Standard 7.3" e-ink resolution
WHITE = 255
BLACK = 0
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_gemini_content(prompt):
    """Fetches text content from Gemini."""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"{prompt}. Keep it short for an e-ink screen. Maximum 200 characters. Kid-friendly (under 11)."
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error fetching Gemini content: {e}")
        return "Oops! Could not load today's content."

def create_image(title, content, filename):
    """Creates a high-contrast B&W image with text."""
    img = Image.new('L', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Github runners usually have 'DejaVuSans.ttf' or 'LiberationSans-Regular.ttf'
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
        font_content = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        font_title = font_content = font_date = ImageFont.load_default()

    # Layout
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    draw.text((40, 30), title, font=font_title, fill=BLACK)
    
    # Wrap text to fit screen width
    wrapped_text = textwrap.fill(content, width=40)
    draw.multiline_text((40, 140), wrapped_text, font=font_content, fill=BLACK, spacing=12)
    
    # Footer
    draw.line((40, 410, WIDTH-40, 410), fill=BLACK, width=2)
    draw.text((40, 425), today, font=font_date, fill=BLACK)
    
    img.save(filename)

# Define the 4 prompts
categories = {
    "history.png": ("ON THIS DAY", "Tell me one interesting historical event that happened today. Make it fun for a 10 year old."),
    "animal.png": ("ANIMAL FACT", "Tell me an amazing, surprising animal fact for kids."),
    "affirmation.png": ("AFFIRMATION", "Give me a positive, empowering daily affirmation for a child."),
    "joke.png": ("DAD JOKE", "Tell me a clean, funny dad joke for kids.")
}

# Run generation
for filename, (title, prompt) in categories.items():
    content = get_gemini_content(prompt)
    create_image(title, content, filename)
    print(f"Generated {filename}")
