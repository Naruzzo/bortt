import logging
import requests
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# Bot & API Configuration
TELEGRAM_BOT_TOKEN = "7614473367:AAFUWjK8H0ibnzAl63Lz30CAMPVGT9Ew0kg"
API_TOKEN = "naPgeLxXnVkIkEkreCXB7IPu5rgI6zyeOcTU8vnztOAaaF58oSO8TH7x8AFYqQvxeBZMeqyosghQOW5mTrx3yn0cTlV5Z7XFUkLQ"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.onrender.com"

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
        is_video = True

        # Priority check for video URLs
        for key in ["media", "video_url", "download_url", "url", "formats", "videos"]:
            if key in data:
                if key in ["media", "formats", "videos"]:
                    items = data[key]
                    if isinstance(items, list) and items:
                        items = sorted(
                            [i for i in items if "url" in i],
                            key=lambda x: int(x.get("height", 0)) * int(x.get("width", 0)),
                            reverse=True
                        )
                        if items:
                            media_url = items[0]["url"]
                            break
                elif isinstance(data[key], str):
                    media_url = data[key]
                    break

        # Fallback to image
        if not media_url:
            is_video = False
            for key in ["image_url", "thumbnail", "thumbnails"]:
                if key in data:
                    if key == "thumbnails" and isinstance(data[key], list) and data[key]:
                        thumbs = sorted(
                            [t for t in data[key] if "url" in t],
                            key=lambda x: int(x.get("width", 0)) * int(x.get("height", 0)),
                            reverse=True
                        )
                        if thumbs:
                            media_url = thumbs[0]["url"]
                            break
                    elif isinstance(data[key], str):
                        media_url = data[key]
                        break

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
