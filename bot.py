import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import inline_handlers_2_mysql
#from handlers import inline_handlers_2_sql
#from handlers import handlers

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_routers(inline_handlers_2_mysql.router)
    #dp.include_routers(inline_handlers_2_sql.router)
    #dp.include_routers(handlers.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
