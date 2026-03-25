import requests
import feedparser
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import io

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
RSS_URL = "https://asherperlman.substack.com/feed"
FILENAME = "asher_comic.png"

def get_latest_comic():
    print("Fetching Substack RSS...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Error: Could not find any posts in the RSS feed.")
        return None

    # Get the HTML content of the most recent post
    latest_post = feed.entries[0]
    html_content = latest_post.content[0].value
    soup = BeautifulSoup(html_content, 'html.parser')
    
    largest_img = None
    max_area = 0

    print("Scanning post for the comic...")
    # Find all images in the post
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        if not img_url: 
            continue
            
        try:
            # Download the image to check its size
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            img_temp = Image.open(response.raw)
            
            # Calculate total pixels to find the main comic (ignores small icons)
            area = img_temp.width * img_temp.height
            if area > max_area:
                max_area = area
                # Convert to Grayscale for E-Ink immediately
                largest_img = img_temp.convert("L") 
        except Exception as e:
            print(f"Skipped an image due to error: {e}")
            continue

    return largest_img

def format_for_trmnl(comic_img):
    if not comic_img:
        print("No comic found to format.")
        return

    print("Formatting for TRMNL display...")
    # ImageOps.pad automatically resizes the image to fit 800x480 
    # without stretching it, and fills the empty space with white (255)
    final_image = ImageOps.pad(comic_img, (WIDTH, HEIGHT), color=255)
    
    final_image.save(FILENAME)
    print(f"SUCCESS: Saved {FILENAME}")

# --- EXECUTION ---
comic = get_latest_comic()
if comic:
    format_for_trmnl(comic)
else:
    print("Failed to generate Asher Perlman comic.")
