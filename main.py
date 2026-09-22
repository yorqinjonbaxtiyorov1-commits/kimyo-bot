import os
import http.server
import socketserver
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 1. BotFather bergan API Token
TOKEN = "8927870856:AAHICXbggtOtL_BosPINspAZaYQVCT7o3pM"

# 2. Sizning shaxsiy Telegram ID'ingiz (@userinfobot orqali olgan soningiz)
ADMIN_ID = 6420660423 # <--- Bu yerga o'zingizning Telegram ID'ingizni yozing!

# Render'da Web Service o'chib qolmasligi uchun soxta server
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

# Ekran pastida doimiy turadigan tugmalar
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📥 Vazifa olish"), KeyboardButton("📤 Vazifa topshirish")]
    ],
    resize_keyboard=True
)

# /start bosilganda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Oldingi holatlarni to'liq tozalanadi
    context.user_data.clear()

    if 'full_name' not in context.user_data:
        context.user_data['waiting_for_name'] = True
        await update.message.reply_text(
            "Assalomu alaykum! Botdan foydalanish uchun iltimos, **Ism va Familiyangizni** kiriting:\n"
            "(Masalan: Ali Valiyev)",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"Xush kelibsiz, {context.user_data['full_name']}!\n"
            "Kerakli bo'limni pastdagi tugmalardan tanlang:",
            reply_markup=MAIN_KEYBOARD
        )

# Matnli xabarlar kelganda (Ism yoki Menyu tugmalari)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # 1. Agar bot ism-familiya kutayotgan bo'lsa
    if context.user_data.get('waiting_for_name'):
        context.user_data['full_name'] = text
        context.user_data['waiting_for_name'] = False
        await update.message.reply_text(
            f"Rahmat, **{text}**! Ma'lumotlaringiz saqlandi.\n\n"
            "Endi pastdagi tugmalardan foydalanishingiz mumkin:",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return

    # 2. Vazifa olish tugmasi
    if text == "📥 Vazifa olish":
        file_path = "vazifa.pdf"
        if os.path.exists(file_path):
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                caption="📖 Mana bugungi uyga vazifa! Barcha topshiriqlarni diqqat bilan bajaring."
            )
        else:
            await update.message.reply_text("❌ Hozircha vazifa fayli yuklanmagan.")
        return

    # 3. Vazifa topshirish tugmasi
    if text == "📤 Vazifa topshirish":
        context.user_data['waiting_for_homework'] = True
        await update.message.reply_text(
            "📝 **Vazifangizni yuklang!**\n\n"
            "Bajargan vazifangizni rasm (foto) yoki PDF hujjat ko'rinishida shu yerga yuboring.",
            parse_mode="Markdown"
        )
        return

# Rasm yoki Fayl (PDF) kelganda ustozga yetkazish
async def receive_homework(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student_name = context.user_data.get('full_name', update.effective_user.full_name)
    username = update.effective_user.username
    user_link = f"@{username}" if username else "Username yo'q"

    caption_text = (
        f"📥 **Yangi uyga vazifa keldi!**\n\n"
        f"👤 **O'quvchi:** {student_name}\n"
        f"🔗 **Profili:** {user_link}"
    )

    # Fayl (PDF/Document) kelganda
    if update.message.document:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=update.message.document.file_id,
            caption=caption_text,
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Vazifangiz qabul qilindi va ustozga yetkazildi!", reply_markup=MAIN_KEYBOARD)
        context.user_data['waiting_for_homework'] = False

    # Rasm kelganda
    elif update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption_text,
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Vazifangiz qabul qilindi va ustozga yetkazildi!", reply_markup=MAIN_KEYBOARD)
        context.user_data['waiting_for_homework'] = False

if __name__ == '__main__':
    # Soxta portni ishga tushirish (Render uchun)
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.DOCUMENT | filters.PHOTO, receive_homework))

    print("Bot ishga tushdi...")
    app.run_polling()
