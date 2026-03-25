import requests
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
# Shopify stores have a hidden .json endpoint that lists all products!
SHOPIFY_JSON_URL = "https://shop.ashermaxperlman.com/products.json?limit=250"
FILENAME = "asher_comic.png"

def get_random_comic_from_shop():
    print("Fetching comic list from Asher's print shop...")
    
    try:
        # Pretend to be a normal web browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(SHOPIFY_JSON_URL, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        products = data.get('products', [])
        
        # Filter out non-comic items (like hats, pins, mugs)
        # We only want items with "Print" in the title
        comic_prints = [p for p in products if "Print" in p.get('title', '') and "Custom" not in p.get('title', '')]
        
        if not comic_prints:
            print("Error: Could not find any comic prints in the shop data.")
            return None
            
        # Pick a random comic for today
        daily_comic = random.choice(comic_prints)
        print(f"Selected comic: {daily_comic['title']}")
        
        # Get the highest resolution image URL for this product
        img_url = daily_comic['images'][0]['src']
        
        # Download the image
        img_response = requests.get(img_url, headers=headers, stream=True)
        img_response.raise_for_status()
        
        # Convert to Grayscale for E-Ink
        return Image.open(img_response.raw).convert("L")
        
    except Exception as e:
        print(f"Failed to fetch from shop: {e}")
        return None

def format_for_trmnl(comic_img):
    print("Formatting for TRMNL display...")
    # Pad the square image with white borders to fit the 800x480 screen perfectly
    final_image = ImageOps.pad(comic_img, (WIDTH, HEIGHT), color=255)
    final_image.save(FILENAME)
    print(f"SUCCESS: Saved {FILENAME}")

def create_fallback_image():
    print("Creating fallback placeholder image...")
    img = Image.new('L', (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    msg = "Comic on a break today.\nCheck back tomorrow!"
    
    bbox = draw.textbbox((0, 0), msg, font=font)
    x = (WIDTH - (bbox[2] - bbox[0])) / 2
    y = (HEIGHT - (bbox[3] - bbox[1])) / 2
    
    draw.text((x, y), msg, font=font, fill=0, align="center")
    img.save(FILENAME)
    print(f"SUCCESS: Created fallback {FILENAME}")

# --- EXECUTION ---
try:
    comic = get_random_comic_from_shop()
    if comic:
        format_for_trmnl(comic)
    else:
        print("No comic found. Triggering fallback.")
        create_fallback_image()
except Exception as e:
    print(f"Critical error: {e}")
    create_fallback_image()
