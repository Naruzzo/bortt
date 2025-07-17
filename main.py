import logging
import requests
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# Bot & API Configuration
TELEGRAM_BOT_TOKEN = "7614473367:AAFUWjK8H0ibnzAl63Lz30CAMPVGT9Ew0kg"
API_TOKEN = "naPgeLxXnVkIkEkreCXB7IPu5rgI6zyeOcTU8vnztOAaaF58oSO8TH7x8AFYqQvxeBZMeqyosghQOW5mTrx3yn0cTlV5Z7XFUkLQ"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.vercel.app/"

# Enable Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# URL patterns matched to exact API endpoint names
PLATFORM_PATTERNS = {
    "instagramdownloader": r"instagram\.com",
    "tiktokdownloader": r"tiktok\.com",
    "facebookdownloader": r"facebook\.com",
    "twitterdownloader": r"twitter\.com",
    "pinterestdownloader": r"pinterest\.com",
    "snapchatdownloader": r"snapchat\.com",
    "threadsdownloader": r"threads\.net",
    "likeedownloader": r"likee\.com",
    "youtubedownloader": r"(youtube\.com|youtu\.be)"
}

def detect_platform(url: str) -> str:
    for platform, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, url):
            return platform
    return None

async def download_media(update: Update, context: CallbackContext):
    await update.message.reply_text("⏳ Processing...")
    url = update.message.text.strip()
    platform = detect_platform(url)

    if not platform:
        await update.message.reply_text("❌ Unsupported platform.")
        return

    try:
        response = requests.get(f"{API_URL}/{platform}", params={"url": url, "token": API_TOKEN})
        if response.status_code != 200:
            await update.message.reply_text("❌ API error.")
            return

        data = response.json()
        media_url = None
        is_video = False

        # Check for video first
        if "video" in data and isinstance(data["video"], str):
            media_url = data["video"]
            is_video = True
        # Fallback to image or thumbnail
        elif "image" in data and isinstance(data["image"], str):
            media_url = data["image"]
        elif "thumbnail" in data and isinstance(data["thumbnail"], str):
            media_url = data["thumbnail"]

        if not media_url:
            await update.message.reply_text("❌ No media found.")
            return

        try:
            if is_video:
                await update.message.reply_video(media_url)
            else:
                await update.message.reply_photo(media_url)
        except Exception:
            try:
                await update.message.reply_document(media_url)
            except Exception:
                await update.message.reply_text("❌ Failed to send media.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Unexpected error.")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    app.run_polling()

if __name__ == "__main__":
    main()
