import logging
import requests
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Bot & API Configuration
TELEGRAM_BOT_TOKEN = "7614473367:AAFUWjK8H0ibnzAl63Lz30CAMPVGT9Ew0kg"
API_TOKEN = "QXowf53aI7b9KvLQuBqFsBtdhidooix12QRRbkwsZLuqyYnFVqQ80qWW7bMT8UULEL5lWzcLGCaIDbboGNjrOSfweAhqF6Y8LKmp"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.onrender.com"

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Platform-specific URL patterns
PLATFORM_PATTERNS = {
    "instagramdownloader2": r"instagram\.com",
    "tiktokdownloader": r"tiktok\.com",
    "facebookdownloader1": r"facebook\.com",
    "twitterdownloader": r"twitter\.com",
    "pinterestdownloader1": r"pinterest\.com",
    "snapchatdownloader": r"snapchat\.com",
    "threadsdownloader": r"threads\.net",
    "likeedownloader": r"likee\.com"
}

def detect_platform(url: str) -> str:
    """Detect the platform based on the URL."""
    for platform, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, url):
            return platform
    return None

async def start(update: Update, context: CallbackContext):
    """Start command handler."""

async def download_media(update: Update, context: CallbackContext):
    """Detect platform and download media."""
    await update.message.reply_text("⏳ Processing your request...")
    
    url = update.message.text.strip()
    platform = detect_platform(url)
    
    if not platform:
        await update.message.reply_text("❌ Unsupported platform. Send a valid media link.")
        return
    
    params = {"url": url, "token": API_TOKEN}
    try:
        response = requests.get(f"{API_URL}/{platform}", params=params)
        logger.info(f"API Status Code: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"API returned error: {response.status_code} - {response.text}")
            await update.message.reply_text("❌ API error. Try again later.")
            return

        try:
            data = response.json()
            logger.info(f"API Response keys: {list(data.keys())}")
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Invalid JSON response: {response.text}")
            await update.message.reply_text("❌ Failed to parse API response. Try again later.")
            return

        # Prioritize finding the actual video instead of thumbnails
        media_url = None
        is_video = True
        
        # Check direct methods first (most likely to be actual video)
        if "media" in data and isinstance(data["media"], list) and data["media"]:
            for media_item in data["media"]:
                if isinstance(media_item, dict) and "url" in media_item:
                    media_url = media_item["url"]
                    break
        
        # Look for dedicated video URL (common format)
        if not media_url and "video_url" in data:
            media_url = data["video_url"]
        
        # Check for download URL (another common format)
        if not media_url and "download_url" in data:
            media_url = data["download_url"]
            
        # Check direct URL field
        if not media_url and "url" in data:
            media_url = data["url"]
        
        # Check formats array if available
        if not media_url and "formats" in data and isinstance(data["formats"], list) and data["formats"]:
            # Try to find video formats, prioritizing by quality
            formats = sorted(
                [f for f in data["formats"] if "url" in f],
                key=lambda x: int(x.get("height", 0) or 0) * int(x.get("width", 0) or 0),
                reverse=True
            )
            if formats:
                media_url = formats[0]["url"]
        
        # Look for videos array
        if not media_url and "videos" in data and isinstance(data["videos"], list) and data["videos"]:
            videos = sorted(
                [v for v in data["videos"] if "url" in v], 
                key=lambda x: int(x.get("width", 0) or 0) * int(x.get("height", 0) or 0),
                reverse=True
            )
            if videos:
                media_url = videos[0]["url"]
        
        # Last resort - check for image instead of video
        if not media_url:
            is_video = False
            # Check for image URL (common format)
            if "image_url" in data:
                media_url = data["image_url"]
                
            # Look in thumbnails as last resort (for images only)
            elif "thumbnails" in data and isinstance(data["thumbnails"], list) and data["thumbnails"]:
                thumbnails = sorted(
                    [t for t in data["thumbnails"] if "url" in t],
                    key=lambda x: int(x.get("width", 0) or 0) * int(x.get("height", 0) or 0),
                    reverse=True
                )
                if thumbnails:
                    media_url = thumbnails[0]["url"]
            
            # Try thumbnail key directly
            elif "thumbnail" in data and data["thumbnail"]:
                media_url = data["thumbnail"]
        
        # Debug log to see what URL we found
        logger.info(f"Selected media URL: {media_url}")
        logger.info(f"Is video: {is_video}")
        
        if media_url:
            # Send media without any caption
            try:
                if is_video:
                    await update.message.reply_video(media_url)
                else:
                    await update.message.reply_photo(media_url)
                return
            except Exception as e:
                logger.error(f"Error sending media: {e}")
                # Fallback: try to send as document if media sending fails
                try:
                    await update.message.reply_document(media_url)
                    return
                except Exception as doc_e:
                    logger.error(f"Error sending document: {doc_e}")
                    await update.message.reply_text("❌ Couldn't send media. Try again later.")
                    return
        
        await update.message.reply_text("❌ No media found in the response. Try another link.")
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        await update.message.reply_text("❌ Network error. Try again later.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("❌ An unexpected error occurred. Try again later.")

def main():
    """Run the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
