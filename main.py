import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# 1. BotFather bergan API Token
TOKEN = "8927870856:AAE22Y0N-B9AzIAEqTM6dnvAPae0wc6je60"

# 2. @userinfobot bergan sizning shaxsiy Telegram ID'ingiz (masalan: 123456789)
ADMIN_ID = 6420660423

# Bosqichlar
ASK_NAME = 1

# Doimiy ekran pastida turadigan tugmalar
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📥 Vazifa olish"), KeyboardButton("📤 Vazifa topshirish")]
    ],
    resize_keyboard=True
)

# /start bosilganda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agar foydalanuvchi oldin ismini kiritmagan bo'lsa
    if 'full_name' not in context.user_data:
        await update.message.reply_text(
            "Assalomu alaykum! Botdan foydalanish uchun iltimos, **Ism va Familiyangizni** kiriting:\n"
            "(Masalan: Ali Valiyev)",
            parse_mode="Markdown"
        )
        return ASK_NAME
    else:
        await update.message.reply_text(
            f"Xush kelibsiz, {context.user_data['full_name']}!\n"
            "Kerakli bo'limni pastdagi tugmalardan tanlang:",
            reply_markup=MAIN_KEYBOARD
        )
        return ConversationHandler.END

# Ism-familiyani saqlab olish
async def save_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    context.user_data['full_name'] = user_name
    
    await update.message.reply_text(
        f"Rahmat, **{user_name}**! Ma'lumotlaringiz saqlandi.\n\n"
        "Endi pastdagi tugmalardan foydalanishingiz mumkin:",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )
    return ConversationHandler.END

# 📥 Vazifa olish tugmasi bosilganda
async def get_homework(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = "vazifa.pdf"
    
    if os.path.exists(file_path):
        await update.message.reply_document(
            document=open(file_path, 'rb'),
            caption="📖 Mana bugungi uyga vazifa! Barcha topshiriqlarni diqqat bilan bajaring."
        )
    else:
        await update.message.reply_text("❌ Hozircha vazifa fayli yuklanmagan.")

# 📤 Vazifa topshirish tugmasi bosilganda
async def submit_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for_homework'] = True
    await update.message.reply_text(
        "📝 **Vazifangizni yuklang!**\n\n"
        "Bajargan vazifangizni rasm (foto) yoki PDF hujjat ko'rinishida yuboring.",
        parse_mode="Markdown"
    )

# O'quvchi vazifa (fayl/rasm) yuborganda ustozga yetkazish
async def receive_homework(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agar topshirish tugmasi bosilmagan bo'lsa shunchaki e'tiborsiz qoldirish yoki ogohlantirish
    student_name = context.user_data.get('full_name', update.effective_user.full_name)
    username = update.effective_user.username
    user_link = f"@{username}" if username else "Username yo'q"
    
    caption_text = (
        f"📥 **Yangi uyga vazifa keldi!**\n\n"
        f"👤 **O'quvchi:** {student_name}\n"
        f"🔗 **Profilli:** {user_link}"
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
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Ism so'rash uchun conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_name)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    app.add_handler(conv_handler)
    
    # Menyu tugmalarini eshitish
    app.add_handler(MessageHandler(filters.Regex("^📥 Vazifa olish$"), get_homework))
    app.add_handler(MessageHandler(filters.Regex("^📤 Vazifa topshirish$"), submit_prompt))
    
    # Rasm va fayllarni qabul qilish
    app.add_handler(MessageHandler(filters.DOCUMENT | filters.PHOTO, receive_homework))
    
    print("Bot ishga tushdi...")
    app.run_polling()
