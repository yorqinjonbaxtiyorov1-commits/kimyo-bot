import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Bu yerga BotFather bergan tokenni qo'yasiz
TOKEN = "8927870856:AAE22Y0N-B9AzIAEqTM6dnvAPae0wc6je60"

# /start bosilganda tugma chiqarish
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Uyga vazifani yuklab olish", callback_data='get_homework')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Assalomu alaykum! Uyga vazifani olish uchun pastdagi tugmani bosing:",
        reply_markup=reply_markup
    )

# Tugma bosilganda vazifa faylini yuborish
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'get_homework':
        file_path = "vazifa.pdf"  # GitHub'ga yuklangan fayl nomi
        
        if os.path.exists(file_path):
            await query.message.reply_document(
                document=open(file_path, 'rb'),
                caption="📖 Barcha topshiriqlarni diqqat bilan bajaring!"
            )
        else:
            await query.message.reply_text("❌ Hozircha vazifa fayli topilmadi.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot ishga tushdi...")
    app.run_polling()
