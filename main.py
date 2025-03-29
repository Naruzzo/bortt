import logging
import requests
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Bot & API Configuration (Using tokens from first code)
TELEGRAM_BOT_TOKEN = "7614473367:AAFUWjK8H0ibnzAl63Lz30CAMPVGT9Ew0kg"
API_TOKEN = "RDeBNsLgiNb136Rxi4g7T9cL83qix0Js7hds9jOlFOpGS4xZ9aL0xcpl3fkk66TNKnyUccPa7utNNhy2JTTYPMOMBQd2crQQg3L9"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.vercel.app"

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Platform-specific URL patterns
PLATFORM_PATTERNS = {
    "instagramdownloader1": r"instagram\.com",
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
    url = update.message.text.strip()
    platform = detect_platform(url)
    
    if not platform:
        await update.message.reply_text("❌ Unsupported platform. Send a valid media link.")
        return
    
    params = {"url": url, "token": API_TOKEN}
    response = requests.get(f"{API_URL}/{platform}", params=params)
    
    try:
        data = response.json()
        logger.info(f"API Response: {data}")  # Debugging
        
        if isinstance(data, dict):
            video_url = data.get("url")
            content_type = data.get("type", "").lower()
            
            if video_url and "video" in content_type:
                await update.message.reply_video(video_url)
                return
        
        await update.message.reply_text("❌ No video found. Try another link.")
    except Exception as e:
        logger.error(f"Error processing API response: {e}")
        await update.message.reply_text("❌ Failed to fetch media. Try again.")

def main():
    """Run the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
