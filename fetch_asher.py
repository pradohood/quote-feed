import io
import os
import time
import random

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
SHOPIFY_JSON_URL = "https://shop.ashermaxperlman.com/products.json?limit=250"
FILENAME = "asher_comic.png"

# Last successful comic, committed to the repo so it survives between runs
CACHE_FILE = "last_comic.png"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TIMEOUT = 20
RETRIES = 3
BACKOFF = 5  # seconds, doubles each attempt

SCRIPT_VERSION = "v2-resilient"
print(f"=== fetch_asher.py {SCRIPT_VERSION} ===", flush=True)


def fetch_with_retries(url, label):
    """GET a URL, retrying transient failures. Returns Response or None."""
    delay = BACKOFF
    for attempt in range(1, RETRIES + 1):
        try:
            print(f"  {label}: attempt {attempt}/{RETRIES}...", flush=True)
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"  {label} attempt {attempt} failed: "
                  f"{type(e).__name__}: {e}", flush=True)
            if attempt < RETRIES:
                print(f"  Retrying in {delay}s...", flush=True)
                time.sleep(delay)
                delay *= 2
    return None


def get_random_comic_from_shop():
    print("Fetching comic list from Asher's print shop...", flush=True)

    response = fetch_with_retries(SHOPIFY_JSON_URL, "product list")
    if response is None:
        return None

    try:
        products = response.json().get("products", [])
    except Exception as e:
        print(f"  Could not parse product JSON: {type(e).__name__}: {e}", flush=True)
        return None

    comic_prints = [
        p for p in products
        if "Print" in p.get("title", "")
        and "Custom" not in p.get("title", "")
        and p.get("images")
    ]

    if not comic_prints:
        print(f"  No comic prints found (parsed {len(products)} products).", flush=True)
        return None

    daily_comic = random.choice(comic_prints)
    print(f"  Selected comic: {daily_comic['title']}", flush=True)

    img_url = daily_comic["images"][0]["src"]
    img_response = fetch_with_retries(img_url, "comic image")
    if img_response is None:
        return None

    try:
        # .content (not .raw) so requests handles gzip/chunked decoding
        return Image.open(io.BytesIO(img_response.content)).convert("L")
    except Exception as e:
        print(f"  Could not decode image: {type(e).__name__}: {e}", flush=True)
        return None


def format_for_trmnl(comic_img):
    print("Formatting for TRMNL display...", flush=True)
    final_image = ImageOps.pad(comic_img, (WIDTH, HEIGHT), color=255)
    final_image.save(FILENAME)
    print(f"SUCCESS: Saved {FILENAME}", flush=True)

    # Keep a copy so tomorrow's run has something to fall back on
    try:
        final_image.save(CACHE_FILE)
        print(f"  Cached as {CACHE_FILE}", flush=True)
    except Exception as e:
        print(f"  WARNING: could not write cache: {type(e).__name__}: {e}", flush=True)


def use_cached_comic():
    """Reuse the last successful comic. Returns True if it worked."""
    if not os.path.exists(CACHE_FILE):
        print(f"  No cached comic at {CACHE_FILE}.", flush=True)
        return False
    try:
        cached = Image.open(CACHE_FILE).convert("L")
        # Re-pad rather than raw-copy, so a wrong-sized cache can't reach the display
        ImageOps.pad(cached, (WIDTH, HEIGHT), color=255).save(FILENAME)
        print(f"SUCCESS: Reused cached comic from {CACHE_FILE}", flush=True)
        return True
    except Exception as e:
        print(f"  Could not reuse cache: {type(e).__name__}: {e}", flush=True)
        return False


def create_fallback_image():
    print("Creating fallback placeholder image...", flush=True)
    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except Exception:
        font = ImageFont.load_default()

    msg = "Comic on a break today.\nCheck back tomorrow!"

    # multiline_textbbox so the two lines are centred correctly
    bbox = draw.multiline_textbbox((0, 0), msg, font=font, align="center")
    x = (WIDTH - (bbox[2] - bbox[0])) / 2
    y = (HEIGHT - (bbox[3] - bbox[1])) / 2

    draw.multiline_text((x, y), msg, font=font, fill=0, align="center")
    img.save(FILENAME)
    print(f"SUCCESS: Created fallback {FILENAME}", flush=True)


# --- EXECUTION ---
# Ladder: live comic -> yesterday's cached comic -> placeholder
try:
    comic = get_random_comic_from_shop()
except Exception as e:
    print(f"Unexpected error while fetching: {type(e).__name__}: {e}", flush=True)
    comic = None

if comic is not None:
    format_for_trmnl(comic)
else:
    print("Live fetch failed. Trying cached comic...", flush=True)
    if not use_cached_comic():
        print("No cache available. Using placeholder.", flush=True)
        create_fallback_image()
