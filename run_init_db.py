import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    with open("init_db.sql", "r") as f:
        sql = f.read()
    
    await conn.execute(sql)
    print("Tables created successfully!")
    
    await conn.close()

asyncio.run(main())
