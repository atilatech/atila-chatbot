import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from utils.credentials import BOT_TOKEN
from utils.database import save_data

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_welcome = f"""
           Connect Mentors with UDG students.
           Please include what you can provide mentorship about and
           if a match is found we will contact you.
           Example:\n
           """
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=bot_welcome,
                                   reply_to_message_id=update.message.message_id)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    mentor = {
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'telegram_username': update.message.from_user.username,
        'telegram_id': update.message.from_user.id,
        'source': 'telegram',
        'description': message_text,
    }

    save_data('mentors', mentor)

    message = 'Thank you for your response. We will contact you if a mentorship match is found'
    print('message', message)
    await context.bot.send_message(update.effective_chat.id, text=message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))

    application.run_polling()
