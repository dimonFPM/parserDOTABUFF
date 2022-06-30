import asyncio

import aiogram
import aiogram.types as types

# https://surik00.gitbooks.io/aiogram-lessons/content/chapter1.html

token = "5226592225:AAGuyEtD_FOotorITU45tTNOLWhEcR2htVA"

bot = aiogram.Bot(token)
dp = aiogram.Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message):
    await bot.send_message(message.chat.id,
                           "Привет мой друг, если всё заработало, то значит ты вспомнил как это работает")


@dp.message_handler(content_types=["text"])
async def help(message):
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    await asyncio.sleep(3)
    await message.reply("skjeflskejf")


aiogram.executor.start_polling(dp)
