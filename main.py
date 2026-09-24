import os
import http.server
import socketserver
import threading
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Logging (xatoliklarni kuzatish uchun)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 1. Bot Tokeningiz
TOKEN = "8927870856:AAE22Y0N-B9AzIAEqTM6dnvAPae0wc6je60"

# 2. Sizning Telegram ID raqamingiz (O'ZINGIZNING ID RAQAMINGIZNI YOZING!)
ADMIN_ID = 6420660423  # <--- Shu yerga haqiqiy ID raqamingizni yozing!

# Render o'chib qolmasligi uchun soxta veb-server
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

# Asosiy menyu tugmalari
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("📥 Vazifa olish"), KeyboardButton("📤 Vazifa topshirish")]],
    resize_keyboard=True
)

# Sinfni tanlash tugmalari
CLASS_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("🏫 10.1-sinf"), KeyboardButton("🏫 10.2-sinf")],
     [KeyboardButton("⬅️ Ortga")]],
    resize_keyboard=True
)

# /start bosilganda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Assalomu alaykum! Kimyo darsidan uy vazifasi botiga xush kelibsiz.\n\n"
        "Iltimos, **Ism va Familiyangizni** kiriting:\n"
        "(Masalan: Ali Valiyev)",
        parse_mode="Markdown"
    )

# Matnli xabarlar kelganda
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 1. Ism-familiya kiritish bosqichi
    if 'full_name' not in context.user_data:
        context.user_data['full_name'] = text
        await update.message.reply_text(
            f"Rahmat, **{text}**! Kerakli bo'limni tanlang:",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return

    # 2. Asosiy menyu buyruqlari
    if text == "📥 Vazifa olish":
        await update.message.reply_text(
            "Qaysi sinf uchun vazifa olmoqchisiz? Tanlang:",
            reply_markup=CLASS_KEYBOARD
        )
        return

    if text == "📤 Vazifa topshirish":
        await update.message.reply_text(
            "📝 Bajargan vazifangizni rasm (foto) yoki PDF fayl ko'rinishida shu yerga yuboring."
        )
        return

    if text == "⬅️ Ortga":
        await update.message.reply_text(
            "Asosiy menyu:",
            reply_markup=MAIN_KEYBOARD
        )
        return

    # 3. Sinflar bo'yicha fayllarni yuborish
    if text == "🏫 10.1-sinf":
        file_path = "vazifa_10_1.pdf"
        if os.path.exists(file_path):
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                caption="📖 **10.1-sinf** uchun topshiriq va testlar!",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Hozircha 10.1-sinf uchun vazifa yuklanmagan.")
        return

    if text == "🏫 10.2-sinf":
        file_path = "vazifa_10_2.pdf"
        if os.path.exists(file_path):
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                caption="📖 **10.2-sinf** uchun topshiriq va testlar!",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Hozircha 10.2-sinf uchun vazifa yuklanmagan.")
        return

# O'quvchi uy vazifasini (rasm yoki fayl) yuborganda ustozga yetkazish
async def receive_homework(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_name = context.user_data.get('full_name', update.effective_user.full_name)
    username = update.effective_user.username
    user_link = f"@{username}" if username else f"ID: {update.effective_user.id}"

    caption_text = (
        f"📥 **Yangi uyga vazifa keldi!**\n\n"
        f"👤 **O'quvchi:** {student_name}\n"
        f"🔗 **Profil:** {user_link}"
    )

    try:
        if update.message.document:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=update.message.document.file_id,
                caption=caption_text,
                parse_mode="Markdown"
            )
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption_text,
                parse_mode="Markdown"
            )
        
        await update.message.reply_text("✅ Uy vazifangiz ustozga muvaffaqiyatli yetkazildi!", reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await update.message.reply_text("❌ Vazifani yuborishda xatolik yuz berdi. Qayta urinib ko'ring.")

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receive_homework))

    print("Bot ishga tushdi...")
    app.run_polling()
