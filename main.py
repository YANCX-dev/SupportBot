from aiogram import executor
from bot.handlers import *

async def on_start_up(_):
    print('Bot has been started')


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=False,
                           on_startup=on_start_up)
