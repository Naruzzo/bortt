import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Bot & API Configuration
TELEGRAM_BOT_TOKEN = "7886947654:AAEsdg4jwCBBvvCqbEjZM-ZCCjm6sDPnM9k"
API_TOKEN = "RDeBNsLgiNb136Rxi4g7T9cL83qix0Js7hds9jOlFOpGS4xZ9aL0xcpl3fkk66TNKnyUccPa7utNNhy2JTTYPMOMBQd2crQQg3L9"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.vercel.app"
CHANNEL_INVITE_LINK = "https://t.me/Glavniga_suratlar_RASMIY"  # Public channel link

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Available social media platforms
PLATFORMS = {
    "📸 Instagram": "instagramdownloader1",
    "🎵 TikTok": "tiktokdownloader",
    "📘 Facebook": "facebookdownloader1",
    "🐦 Twitter": "twitterdownloader",
    "📌 Pinterest": "pinterestdownloader1",
    "👻 Snapchat": "snapchatdownloader",
    "🧵 Threads": "threadsdownloader",
    "❤️ Likee": "likeedownloader"
}

async def start(update: Update, context: CallbackContext):
    """Send start message with keyboard buttons."""
    keyboard = [[KeyboardButton(name)] for name in PLATFORMS.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🎥 *Welcome to the Media Downloader Bot!* 🎥\n\n"
        "✅ YOU MUST JOIN OUR CHANNEL!: [📢 Join Here]({})\n"
        "👇 *Tap a button to continue:*".format(CHANNEL_INVITE_LINK),
        reply_markup=reply_markup,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def platform_selected(update: Update, context: CallbackContext):
    """Handle platform selection from keyboard."""
    platform = update.message.text

    if platform not in PLATFORMS:
        await update.message.reply_text("⚠️ *Invalid selection.* Please choose a platform from the keyboard.")
        return

    context.user_data["platform"] = platform
    await update.message.reply_text(f"📥 *You selected:* {platform}\n\nNow, send the media link.", parse_mode="Markdown")

async def download_media(update: Update, context: CallbackContext):
    """Download media from the selected platform."""
    if "platform" not in context.user_data:
        await update.message.reply_text("⚠️ *Please select a platform first using /start.*", parse_mode="Markdown")
        return

    platform = context.user_data["platform"]
    url = update.message.text

    params = {"url": url, "token": API_TOKEN}
    response = requests.get(f"{API_URL}/{PLATFORMS[platform]}", params=params)

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, platform_selected))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
