import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
from telegram.error import TelegramError

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==================== SOZLAMALAR ====================
TOKEN = "8927870856:AAE22Y0N-B9AzIAEqTM6dnvAPae0wc6je60"
CHANNEL_ID = "@bakht1yorov_y"  # Masalan: @kimyo_kanali
CHANNEL_LINK = "https://t.me/bakht1yorov_y"

# O'zingizning Telegram ID raqamingiz (O'quvchilar vazifa yuborganda sizga keladi)
ADMIN_ID = 6420660423

# GitHub'dagi fayllaringizning to'g'ri (direct/raw) havolalari
FILE_10_1 = "https://raw.githubusercontent.com/yorqinjonbaxtiyorov1-commits/kimyo-bot/main/10_1_sinf.pdf"
FILE_10_2 = "https://raw.githubusercontent.com/yorqinjonbaxtiyorov1-commits/kimyo-bot/main/10_2_sinf.pdf"
# =====================================================

# Conversation holatlari
GET_NAME = 1
SEND_TASK = 2

async def check_sub(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Kanalga obunani tekshirish"""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except TelegramError:
        return False

def main_menu_keyboard():
    """Bosh menyu tugmalari"""
    reply_keyboard = [
        ["📥 Vazifa olish", "📤 Vazifa topshirish"]
    ]
    return ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_sub = await check_sub(user_id, context)

    if not is_sub:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subscription")]
        ]
        await update.message.reply_text(
            " Botdan foydalanish uchun avval rasmiy kanalimizga a'zo bo'ling:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    # Agar obuna bo'lgan bo'lsa, ism so'raymiz
    await update.message.reply_text(
        "Xush kelibsiz! Iltimos, ism va familiyangizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    return GET_NAME

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    is_sub = await check_sub(user_id, context)

    if is_sub:
        await query.edit_message_text("✅ Obuna tasdiqlandi! Endi ism va familiyangizni kiriting:")
        return GET_NAME
    else:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subscription")]
        ]
        await query.edit_message_text(
            "❌ Siz hali kanalga a'zo bo'lmadingiz. Iltimos, avval a'zo bo'ling!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

async def get_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    context.user_data['full_name'] = user_name
    
    await update.message.reply_text(
        f"Rahmat, {user_name}! Kerakli bo'limni tanlang:",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📥 Vazifa olish":
        keyboard = [
            [InlineKeyboardButton("📘 10.1-sinf", callback_data="class_10_1")],
            [InlineKeyboardButton("📙 10.2-sinf", callback_data="class_10_2")],
            [InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_main")]
        ]
        await update.message.reply_text("Sinfni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "📤 Vazifa topshirish":
        await update.message.reply_text(
            "Vazifangizni rasm yoki PDF fayl ko'rinishida yuboring:"
        )
        return SEND_TASK

async def file_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "class_10_1":
        await query.message.reply_document(document=FILE_10_1, caption="10.1-sinf uchun vazifa")
    elif query.data == "class_10_2":
        await query.message.reply_document(document=FILE_10_2, caption="10.2-sinf uchun vazifa")
    elif query.data == "back_to_main":
        await query.message.delete()
        await query.message.reply_text("Bosh menyu:", reply_markup=main_menu_keyboard())

async def receive_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    full_name = context.user_data.get('full_name', 'Ismi kiritilmagan')
    caption_text = f"📩 **Yangi vazifa keldi!**\n\n👤 **O'quvchi:** {full_name}\n🔗 **Username:** @{user.username if user.username else 'Yo'q'}\n🆔 **ID:** {user.id}"

    # Agar rasm yuborsa
    if update.message.photo:
        photo_file = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file, caption=caption_text, parse_mode="Markdown")
        await update.message.reply_text("✅ Vazifangiz o'qituvchiga muvaffaqiyatli yuborildi!", reply_markup=main_menu_keyboard())
    # Agar PDF yoki boshqa fayl yuborsa
    elif update.message.document:
        doc_file = update.message.document.file_id
        await context.bot.send_document(chat_id=ADMIN_ID, document=doc_file, caption=caption_text, parse_mode="Markdown")
        await update.message.reply_text("✅ Vazifangiz o'qituvchiga muvaffaqiyatli yuborildi!", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text("Iltimos, faqat rasm yoki PDF fayl yuboring!")
        return SEND_TASK

    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(check_sub_callback, pattern="^check_subscription$"),
            MessageHandler(filters.Regex("^(📤 Vazifa topshirish)$"), handle_text_buttons)
        ],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_handler)],
            SEND_TASK: [MessageHandler(filters.PHOTO | filters.Document.ALL, receive_task)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^(📥 Vazifa olish)$"), handle_text_buttons))
    app.add_handler(CallbackQueryHandler(file_callback_handler))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
