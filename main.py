import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import db
from handlers import start, donation, admin, sponsorship, catalog

async def main():
    await db.connect()
    
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(donation.router)
    dp.include_router(sponsorship.router)
    dp.include_router(admin.router)
    
    print("Bot started!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
