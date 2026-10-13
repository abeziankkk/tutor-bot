import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram.error import BadRequest

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


def main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 Цены", callback_data="prices")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот репетитора. Выбери, что тебя интересует:",
        reply_markup=main_menu(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "prices":
        text = "Цены (пример):\n• Пробный урок: бесплатно\n• Урок 60 минут: 15 €"
    elif query.data == "contacts":
        text = "Связаться со мной: @твой_username"
    else:
        text = "Не понял, попробуй ещё раз."

    try:
        await query.edit_message_text(text, reply_markup=main_menu())
    except BadRequest:
        # Telegram ругается, если нажать ту же кнопку дважды: текст не изменился
        pass


def main():
    if not TOKEN:
        raise SystemExit("Не найден BOT_TOKEN в файле .env")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()