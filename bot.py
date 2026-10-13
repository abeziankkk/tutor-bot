import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Два шага диалога записи: спрашиваем имя, потом время
ASK_NAME, ASK_TIME = range(2)


def main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 Цены", callback_data="prices")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
        [InlineKeyboardButton("📝 Записаться на пробный урок", callback_data="signup")],
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
    else:
        text = "Связаться со мной: @твой_username"

    try:
        await query.edit_message_text(text, reply_markup=main_menu())
    except BadRequest:
        # Telegram ругается, если нажать ту же кнопку дважды: текст не изменился
        pass


async def signup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Как тебя зовут? (Чтобы отменить, напиши /cancel)")
    return ASK_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Когда тебе удобно? Напиши день и время.")
    return ASK_TIME


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name", "—")
    when = update.message.text.strip()
    user = update.effective_user
    username = f"@{user.username}" if user.username else "username не указан"

    # Отправляем заявку владельцу бота
    await context.bot.send_message(
        chat_id=int(ADMIN_ID),
        text=(
            "📝 Новая заявка на пробный урок\n"
            f"Имя: {name}\n"
            f"Удобное время: {when}\n"
            f"Telegram: {username}"
        ),
    )

    await update.message.reply_text(
        "Спасибо! Заявка отправлена, я скоро свяжусь с тобой.",
        reply_markup=main_menu(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Запись отменена.", reply_markup=main_menu())
    return ConversationHandler.END


def main():
    if not TOKEN:
        raise SystemExit("Не найден BOT_TOKEN в файле .env")
    if not ADMIN_ID or not ADMIN_ID.isdigit():
        raise SystemExit("Не найден ADMIN_ID (число) в файле .env")

    app = Application.builder().token(TOKEN).build()

    signup = ConversationHandler(
        entry_points=[CallbackQueryHandler(signup_start, pattern="^signup$")],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(signup)
    app.add_handler(CallbackQueryHandler(button, pattern="^(prices|contacts)$"))
    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()