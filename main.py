import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Bot & API Configuration
TELEGRAM_BOT_TOKEN = "7886947654:AAEsdg4jwCBBvvCqbEjZM-ZCCjm6sDPnM9k"
API_TOKEN = "RDeBNsLgiNb136Rxi4g7T9cL83qix0Js7hds9jOlFOpGS4xZ9aL0xcpl3fkk66TNKnyUccPa7utNNhy2JTTYPMOMBQd2crQQg3L9"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.vercel.app"
CHANNEL_INVITE_LINK = "https://t.me/+kRK2t9FQFrdmZDIy"  # Private channel link

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

# Store verified users
verified_users = set()

async def start(update: Update, context: CallbackContext):
    """Check if the user is verified before allowing them to use the bot."""
    user_id = update.message.from_user.id

    if user_id not in verified_users:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton("✅ Verify Membership", callback_data="verify")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🚨 *You must join our private channel before using the bot!* 🚨\n\n"
            "👉 Click the **Join Channel** button, then press **Verify Membership**.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    # Inline keyboard for selecting a platform
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name in PLATFORMS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎥 *Select a platform to download media:*", reply_markup=reply_markup, parse_mode="Markdown")

async def verify_membership(update: Update, context: CallbackContext):
    """Verify user manually."""
    user_id = update.callback_query.from_user.id
    verified_users.add(user_id)  # Mark user as verified
    await update.callback_query.message.edit_text("✅ *Verification successful!* You can now use the bot. Send /start.", parse_mode="Markdown")

async def button_handler(update: Update, context: CallbackContext):
    """Handle platform selection."""
    user_id = update.callback_query.from_user.id

    if user_id not in verified_users:
        await update.callback_query.message.reply_text("⚠️ You must verify membership first using /start.")
        return

    query = update.callback_query
    await query.answer()
    context.user_data["platform"] = query.data
    await query.message.edit_text(f"📥 *You selected:* {query.data}\n\nNow, send the media link.", parse_mode="Markdown")

async def download_media(update: Update, context: CallbackContext):
    """Download media from the selected platform."""
    user_id = update.message.from_user.id

    if user_id not in verified_users:
        await update.message.reply_text("⚠️ You must verify membership first using /start.")
        return

    if "platform" not in context.user_data:
        await update.message.reply_text("⚠️ *Please select a platform first using /start.*", parse_mode="Markdown")
        return

    platform = context.user_data["platform"]
    url = update.message.text

    params = {"url": url, "token": API_TOKEN}
    response = requests.get(f"{API_URL}/{PLATFORMS[platform]}", params=params)

    try:
        data = response.json()
        logger.info(f"API Response: {data}")  # Print API response for debugging

        if isinstance(data, dict):  # Ensure it's a dictionary
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
    app.add_handler(CallbackQueryHandler(verify_membership, pattern="verify"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
