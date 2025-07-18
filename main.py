import logging
import requests
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from aiohttp import web

# Config
BOT_TOKEN = "7614473367:AAFUWjK8H0ibnzAl63Lz30CAMPVGT9Ew0kg"
API_TOKEN = "naPgeLxXnVkIkEkreCXB7IPu5rgI6zyeOcTU8vnztOAaaF58oSO8TH7x8AFYqQvxeBZMeqyosghQOW5mTrx3yn0cTlV5Z7XFUkLQ"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.vercel.app"
WEBHOOK_URL = f"https://naruzzo.alwaysdata.net/{BOT_TOKEN}"

# Logging
logging.basicConfig(level=logging.INFO)

# Platform patterns
PLATFORMS = {
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

def detect_platform(url: str):
    for name, pattern in PLATFORMS.items():
        if re.search(pattern, url):
            return name
    return None

async def handle(update: Update, context: CallbackContext):
    await update.message.reply_text("⏳ Processing...")
    url = update.message.text.strip()
    platform = detect_platform(url)

    if not platform:
        await update.message.reply_text("❌ Unsupported platform.")
        return

    try:
        res = requests.get(f"{API_URL}/{platform}", params={"url": url, "token": API_TOKEN})
        data = res.json()
        media_url = data.get("video") or data.get("image")
        is_video = "video" in data

        if not media_url:
            await update.message.reply_text("❌ No media found.")
            return

        try:
            if is_video:
                await update.message.reply_video(media_url)
            else:
                await update.message.reply_photo(media_url)
        except:
            await update.message.reply_document(media_url)
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("❌ Error.")

async def webhook_handler(request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await app.update_queue.put(update)
    return web.Response()

async def main():
    global app, bot
    app = Application.builder().token(BOT_TOKEN).build()
    bot = app.bot
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    await bot.set_webhook(url=WEBHOOK_URL)

    web_app = web.Application()
    web_app.router.add_post(f"/{BOT_TOKEN}", webhook_handler)
    return web_app

if __name__ == "__main__":
    import asyncio
    web.run_app(asyncio.run(main()), port=8000)
