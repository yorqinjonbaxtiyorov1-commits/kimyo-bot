import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8927870856:AAE22Y0N-B9AzIAEqTM6dnvAPae0wc6je60"  # Telegram Bot Tokeningiz
ADMIN_ID = 6420660423  # O'zingizning Telegram ID raqamingizni yozing (rasmlar shu IDga boradi)
CHANNEL_USERNAME = "@bakht1yorov_y"  # O'zingizning kanalingiz usernamesi (masalan: @my_channel)
# ===================================================

# Conversation statuslari
WAITING_FOR_TASK = 1

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Foydalanuvchi kanalga a'zo ekanligini tekshirish."""
    if not CHANNEL_USERNAME or CHANNEL_USERNAME == "@ozingizning_kanalingiz":
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logging.error(f"A'zolikni tekshirishda xatolik: {e}")
        # Agar bot kanalda admin bo'lmasa yoki xato bersa, bot to'xtab qolmasligi uchun True qaytaradi
        return True

def get_main_keyboard():
    """Asosiy klaviatura tugmalari."""
    keyboard = [
        [KeyboardButton("📤 Vazifa olish"), KeyboardButton("📥 Vazifa topshirish")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start buyrug'i uchun javob."""
    user = update.effective_user
    is_sub = await check_subscription(user.id, context)

    if not is_sub:
        channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        await update.message.reply_text(
            f"🚀 Botdan foydalanish uchun avval rasmiy kanalimizga a'zo bo'ling:\n{channel_link}\n\n"
            f"A'zo bo'lgach, qayta /start boshing."
        )
        return

    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}!\n"
        f"Uyga vazifa botiga xush kelibsiz. Kerakli bo'limni tanlang:",
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalar va xabarlarni qayta ishlash."""
    user = update.effective_user
    text = update.message.text

    # Obunani tekshirish
    is_sub = await check_subscription(user.id, context)
    if not is_sub:
        channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        await update.message.reply_text(
            f"🚀 Botdan foydalanish uchun avval rasmiy kanalimizga a'zo bo'ling:\n{channel_link}"
        )
        return

    if text == "📤 Vazifa olish":
        await update.message.reply_text(
            "📚 Bugungi uyga vazifangiz:\n\n"
            "1. Darslikdagi 12-15 mavzularni o'qib chiqish.\n"
            "2. 45, 46 va 47-masalalarni yechish.\n\n"
            "Vazifani bajarib bo'lgach, '📥 Vazifa topshirish' tugmasi orqali rasm shaklida yuboring!"
        )
    elif text == "📥 Vazifa topshirish":
        await update.message.reply_text(
            "📝 Bajarilgan vazifangizning rasmini (yoki matn shaklida) yuboring:"
        )
        return WAITING_FOR_TASK
    else:
        await update.message.reply_text(
            "Iltimos, pastdagi tugmalardan birini tanlang.",
            reply_markup=get_main_keyboard()
        )

async def receive_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'quvchi yuborgan rasm yoki matnli vazifani qabul qilish va adminga yuborish."""
    user = update.effective_user

    # Agar foydalanuvchi rasm yuborgan bo'lsa
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        caption = (
            f"📩 **Yangi vazifa keldi!**\n\n"
            f"👤 O'quvchi: {user.full_name} (@{user.username or 'username_yoq'})\n"
            f"🆔 ID: `{user.id}`\n"
            f'💬 Izoh: {update.message.caption or "Izoh yoq"}'
        )
        # Adminga rasm yuborish
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_file_id,
                caption=caption,
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Adminga yuborishda xatolik: {e}")

    # Agar foydalanuvchi matn yuborgan bo'lsa
    elif update.message.text:
        msg_text = (
            f"📩 **Yangi vazifa (Matn):**\n\n"
            f"👤 O'quvchi: {user.full_name} (@{user.username or 'username_yoq'})\n"
            f"🆔 ID: `{user.id}`\n\n"
            f"📝 **Vazifa:**\n{update.message.text}"
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=msg_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Adminga yuborishda xatolik: {e}")

    await update.message.reply_text(
        "✅ Rahmat! Vazifangiz qabul qilindi va o'qituvchiga yuborildi.",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Amalni bekor qilish."""
    await update.message.reply_text("Amal bekor qilindi.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

def main():
    """Botni ishga tushirish."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📥 Vazifa topshirish$"), handle_message)],
        states={
            WAITING_FOR_TASK: [
                MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, receive_task)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
