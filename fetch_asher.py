#!/usr/bin/env python3
"""
Fetch the latest comic from Asher Perlman's Substack and format for TRMNL e-ink display.
Designed for GitHub Actions with proper exit codes and logging.
"""

import requests
import feedparser
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps
from urllib.parse import urljoin
import io
import logging
import sys
import os

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
RSS_URL = "https://asherperlman.substack.com/feed"
FILENAME = "asher_comic.png"
REQUEST_TIMEOUT = 15  # seconds
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_latest_comic():
    """Fetch the latest comic from the Substack RSS feed."""
    logger.info("Fetching Substack RSS from: %s", RSS_URL)
    try:
        feed = feedparser.parse(RSS_URL)
    except Exception as e:
        logger.error(f"Failed to parse RSS feed: {e}")
        return None
    
    if not feed.entries:
        logger.error("No posts found in RSS feed")
        return None
    
    logger.info(f"Found {len(feed.entries)} posts in feed")
    
    # Get the HTML content of the most recent post
    latest_post = feed.entries[0]
    post_title = latest_post.get('title', 'Unknown')
    logger.info(f"Processing latest post: {post_title}")
    
    # Safely extract HTML content
    if not latest_post.get('content'):
        logger.error("Latest post has no content field")
        return None
    
    try:
        html_content = latest_post.content[0].value
    except (IndexError, AttributeError) as e:
        logger.error(f"Could not extract content from post: {e}")
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    largest_img = None
    max_area = 0
    img_count = 0
    
    logger.info("Scanning post for images...")
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        if not img_url:
            continue
        
        # Resolve relative URLs (if any)
        if not img_url.startswith(('http://', 'https://')):
            img_url = urljoin(RSS_URL, img_url)
        
        try:
            img_count += 1
            logger.debug(f"Downloading image {img_count}: {img_url[:80]}...")
            
            response = requests.get(
                img_url,
                headers=HEADERS,
                stream=True,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Load image into memory to ensure it's fully downloaded
            img_data = io.BytesIO(response.content)
            img_temp = Image.open(img_data)
            
            # Convert to grayscale for e-ink
            img_temp = img_temp.convert("L")
            
            area = img_temp.width * img_temp.height
            logger.debug(f"  Image {img_count}: {img_temp.width}×{img_temp.height} ({area:,} px)")
            
            if area > max_area:
                max_area = area
                largest_img = img_temp
                logger.info(f"  → New largest image found ({area:,} px)")
                
        except requests.exceptions.Timeout:
            logger.warning(f"  Timeout downloading image {img_count}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"  Failed to download image {img_count}: {e}")
        except (OSError, IOError) as e:
            logger.warning(f"  Failed to process image {img_count}: {e}")
        except Exception as e:
            logger.warning(f"  Unexpected error with image {img_count}: {e}")
    
    if largest_img:
        logger.info(f"Successfully extracted comic ({max_area:,} pixels)")
        return largest_img
    else:
        logger.error(f"No valid images found in post (scanned {img_count} images)")
        return None

def format_for_trmnl(comic_img):
    """Resize and save the comic for TRMNL display (800x480, grayscale)."""
    logger.info("Formatting image for TRMNL display (800×480)...")
    
    try:
        # Use 'pad' mode to preserve aspect ratio, pad with white borders
        final_image = ImageOps.pad(comic_img, (WIDTH, HEIGHT), color=255)
        
        # Save as PNG (lossless for e-ink)
        final_image.save(FILENAME, quality=95)
        
        file_size = os.path.getsize(FILENAME)
        logger.info(f"✓ Successfully saved {FILENAME} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to format/save image: {e}")
        return False

def create_fallback_image():
    """Create a placeholder image when no comic is available."""
    logger.info("Creating fallback placeholder image...")
    try:
        img = Image.new('L', (WIDTH, HEIGHT), 255)  # White background
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                size=40
            )
        except (FileNotFoundError, OSError):
            logger.warning("TrueType font not found, using default font")
            font = ImageFont.load_default()
        
        msg = "Comic on a break today.\nCheck back tomorrow!"
        
        # Center the text
        bbox = draw.textbbox((0, 0), msg, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (WIDTH - text_width) / 2
        y = (HEIGHT - text_height) / 2
        
        draw.text((x, y), msg, font=font, fill=0, align="center")
        img.save(FILENAME)
        
        file_size = os.path.getsize(FILENAME)
        logger.info(f"✓ Successfully created fallback {FILENAME} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create fallback image: {e}")
        return False

def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("Asher Perlman Comic Fetcher")
    logger.info("=" * 70)
    
    try:
        comic = get_latest_comic()
        if comic:
            logger.info("Comic found, formatting for display...")
            if not format_for_trmnl(comic):
                logger.error("Failed to format comic image")
                return False
        else:
            logger.warning("No comic found in feed, creating fallback...")
            if not create_fallback_image():
                logger.error("Failed to create fallback image")
                return False
    
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        logger.info("Attempting to create fallback...")
        create_fallback_image()
        return False
    
    # Verify file was created
    if not os.path.exists(FILENAME):
        logger.error(f"CRITICAL: File {FILENAME} was not created!")
        return False
    
    logger.info("=" * 70)
    logger.info(f"✓ SUCCESS: {FILENAME} ready for upload")
    logger.info(f"  Path: {os.path.abspath(FILENAME)}")
    logger.info("=" * 70)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
