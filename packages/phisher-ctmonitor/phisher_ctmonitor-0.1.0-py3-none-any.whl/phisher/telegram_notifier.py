from telegram import Bot
import asyncio

def notify_in_telegram(message, chat_id, bot_token):
    """ Function to notify in telegram """
        
    bot = Bot(token=bot_token)

    async def send_message(text, chat_id):
        async with bot:
            await bot.send_message(text=text, chat_id=chat_id)

    async def run_bot(messages, chat_id=chat_id):
        await send_message(messages, chat_id)


    def send_sync(message):
        asyncio.run(run_bot(message, chat_id))

    send_sync(message)