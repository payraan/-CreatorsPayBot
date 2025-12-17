import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    await conn.execute("""
        INSERT INTO creators (slug, name, wallet_bsc, wallet_polygon, wallet_tron)
        VALUES ('skillvid', 'SkillVid', '0x1234567890abcdef1234567890abcdef12345678', '0x1234567890abcdef1234567890abcdef12345678', 'TXyz1234567890abcdef1234567890abcd')
        ON CONFLICT (slug) DO NOTHING
    """)
    
    print("Test creator added successfully!")
    await conn.close()

asyncio.run(main())
