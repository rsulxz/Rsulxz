import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

def is_tiktok(url):
    return "tiktok.com" in url or "vm.tiktok.com" in url

def is_instagram(url):
    return "instagram.com" in url or "instagr.am" in url

def extract_urls(text):
    return re.findall(r'https?://[^\s]+', text)

def download_video(url):
    output_path = "/tmp/%(id)s.%(ext)s"
    ydl_opts = {
        "outtmpl": output_path,
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                filename = filename.rsplit(".", 1)[0] + ".mp4"
            return filename if os.path.exists(filename) else None
    except Exception as e:
        print(f"Error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً! أرسل رابط TikTok أو Instagram وأحمله لك! 🎬"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    urls = extract_urls(text)
    if not urls:
        await update.message.reply_text("❌ أرسل رابط TikTok أو Instagram!")
        return
    url = urls[0]
    if not (is_tiktok(url) or is_instagram(url)):
        await update.message.reply_text("⚠️ الرابط مو من TikTok أو Instagram!")
        return
    platform = "TikTok 🎵" if is_tiktok(url) else "Instagram 📸"
    msg = await update.message.reply_text(f"⏳ جاري التحميل من {platform}...")
    filepath = download_video(url)
    if filepath and os.path.exists(filepath):
        if os.path.getsize(filepath) > 50 * 1024 * 1024:
            await msg.edit_text("❌ الفيديو أكبر من 50MB!")
            os.remove(filepath)
            return
        await msg.edit_text("📤 جاري الإرسال...")
        with open(filepath, "rb") as f:
            await update.message.reply_video(video=f, caption=f"✅ {platform}")
        await msg.delete()
        os.remove(filepath)
    else:
        await msg.edit_text("❌ فشل التحميل! الحساب خاص أو الرابط غلط.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
