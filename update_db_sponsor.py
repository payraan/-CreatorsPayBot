import asyncio
import asyncpg
from config import DATABASE_URL

async def update_db():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # اضافه کردن ستون telegram_id به جدول creators
    await conn.execute("""
        ALTER TABLE creators ADD COLUMN IF NOT EXISTS telegram_id BIGINT
    """)
    
    # ساخت جدول sponsor_leads
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS sponsor_leads (
            id SERIAL PRIMARY KEY,
            creator_id INT REFERENCES creators(id),
            sponsor_name VARCHAR(255) NOT NULL,
            contact_info VARCHAR(255) NOT NULL,
            budget_range VARCHAR(50),
            description TEXT,
            sponsor_tg_id BIGINT,
            assigned_to INT REFERENCES creators(id),
            status VARCHAR(50) DEFAULT 'NEW',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    await conn.close()
    print("✅ Database updated successfully!")

asyncio.run(update_db())
