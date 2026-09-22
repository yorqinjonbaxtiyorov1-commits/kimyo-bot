import os
import http.server
import socketserver
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 1. Aniq tokeningiz
TOKEN = "8927870856:AAE22Y0N-B9AzIAEqTM6dnvAPae0wc6je60"

# 2. Telegram ID raqamingiz
ADMIN_ID = 6420660423  # O'zingizning Telegram ID'ingizni yozing

# Render portini ushlab turuvchi sodda veb-server
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
    try:
        with socketserver.TCPServer(("", port), QuietHandler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("📥 Vazifa olish"), KeyboardButton("📤 Vazifa topshirish")]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Assalomu alaykum! Kimyo darsidan uy vazifasi botiga xush kelibsiz.\n\n"
        "Iltimos, **Ism va Familiyangizni** kiriting:",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Ism kiritish bosqichi
    if 'full_name' not in context.user_data:
        context.user_data['full_name'] = text
        await update.message.reply_text(
            f"Rahmat, **{text}**! Kerakli bo'limni tanlang:",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return

    # Menyular
    if text == "📥 Vazifa olish":
        file_path = "vazifa.pdf"
        if os.path.exists(file_path):
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                caption="📖 Bugungi uyga vazifa!"
            )
        else:
            await update.message.reply_text("❌ Hozircha vazifa fayli yuklanmagan.")
        return

    if text == "📤 Vazifa topshirish":
        await update.message.reply_text("📝 Bajargan vazifangizni rasm yoki PDF fayl ko'rinishida yuboring.")
        return

async def receive_homework(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_name = context.user_data.get('full_name', update.effective_user.full_name)
    username = update.effective_user.username
    user_link = f"@{username}" if username else f"ID: {update.effective_user.id}"

    caption_text = f"📥 **Yangi uyga vazifa!**\n\n👤 **O'quvchi:** {student_name}\n🔗 **Profil:** {user_link}"

    if update.message.document:
        await context.bot.send_document(chat_id=ADMIN_ID, document=update.message.document.file_id, caption=caption_text, parse_mode="Markdown")
    elif update.message.photo:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption_text, parse_mode="Markdown")

    await update.message.reply_text("✅ Uy vazifangiz ustozga yetkazildi!", reply_markup=MAIN_KEYBOARD)

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.DOCUMENT | filters.PHOTO, receive_homework))
    
    print("Bot ishga tushdi...")
    app.run_polling()
