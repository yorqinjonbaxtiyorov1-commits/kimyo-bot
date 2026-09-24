import os
import time
import threading
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token va Admin ID
TOKEN = "8927870856:AAE22Y0N-B9AzIAEqTM6dnvAPae0wc6je60"
ADMIN_ID = 6420660423  # <--- Shu yerga o'zingizning Telegram ID raqamingizni yozing!

# Botni sleep rejimiga tushib qolmasligi uchun Avto-Ping funksiyasi
def auto_ping():
    time.sleep(10)
    while True:
        try:
            # Telegram API'ga so'rov yuborish orqali botni faol ushlab turadi
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=10)
            logging.info("Auto-ping muvaffaqiyatli bajarildi!")
        except Exception as e:
            logging.error(f"Auto-ping xatosi: {e}")
        time.sleep(300)  # Har 5 daqiqada (300 soniya) bir marta takrorlanadi

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Assalomu alaykum! Kimyo darsidan uy vazifasi botiga xush kelibsiz.\n\n"
        "Iltimos, **Ism va Familiyangizni** kiriting:\n"
        "(Masalan: Ali Valiyev)",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if 'full_name' not in context.user_data:
        context.user_data['full_name'] = text
        await update.message.reply_text(
            f"Rahmat, **{text}**! Kerakli bo'limni tanlang:",
            parse_mode="Markdown",
            reply_markup=MAIN_KEYBOARD
        )
        return

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
        await update.message.reply_text("❌ Vazifani yuborishda xatolik yuz berdi. ADMIN_ID to'g'riligini tekshiring.")

if __name__ == '__main__':
    # Auto-ping tizimini orqa fonda ishga tushirish
    threading.Thread(target=auto_ping, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, receive_homework))

    print("Bot ishga tushdi...")
    app.run_polling()
