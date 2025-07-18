import logging
import requests
import re
import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from aiohttp import web

# --- Config ---
BOT_TOKEN = "7614473367:AAFUWjK8H0ibnzAl63Lz30CAMPVGT9Ew0kg"
API_TOKEN = "naPgeLxXnVkIkEkreCXB7IPu5rgI6zyeOcTU8vnztOAaaF58oSO8TH7x8AFYqQvxeBZMeqyosghQOW5mTrx3yn0cTlV5Z7XFUkLQ"
API_URL = "https://full-media-downloader-pro-zfkrvjl323.vercel.app"
WEBHOOK_URL = f"https://naruzzo.alwaysdata.net/{BOT_TOKEN}"

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Platform Patterns ---
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
    try:
        await update.message.reply_text("⏳ Processing...")
        url = update.message.text.strip()
        platform = detect_platform(url)
        
        if not platform:
            await update.message.reply_text("❌ Unsupported platform.")
            return
        
        # Use async HTTP request instead of sync requests
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/{platform}", params={"url": url, "token": API_TOKEN}) as response:
                data = await response.json()
        
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
        logging.error(f"Error in handle: {e}")
        await update.message.reply_text("❌ Error occurred while processing.")

async def webhook_handler(request):
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        
        # Process the update using the application
        await app.process_update(update)
        
        return web.Response(text="OK")
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)

async def init_app():
    global app
    
    # Initialize the application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    
    # Initialize the application
    await app.initialize()
    
    # Set webhook
    await app.bot.set_webhook(url=WEBHOOK_URL)
    
    # Create aiohttp app
    web_app = web.Application()
    web_app.router.add_post(f"/{BOT_TOKEN}", webhook_handler)
    
    return web_app

async def main():
    web_app = await init_app()
    
    # Run the web app
    runner = web.AppRunner(web_app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logging.info(f"Bot started on port {port}")
    
    # Keep the application running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        await runner.cleanup()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
