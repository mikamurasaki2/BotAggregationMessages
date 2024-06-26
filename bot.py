import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import inline_handlers_2_mysql


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_routers(inline_handlers_2_mysql.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
