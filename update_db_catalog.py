import asyncio
import asyncpg
from config import DATABASE_URL

async def update_db():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # اضافه کردن ستون‌های جدید به جدول creators
    columns = [
        ("platform", "VARCHAR(20) DEFAULT 'YOUTUBE'"),
        ("category", "VARCHAR(50)"),
        ("followers_count", "INT"),
        ("min_sponsor_price", "INT"),
        ("max_sponsor_price", "INT"),
        ("profile_link", "VARCHAR(255)"),
        ("description", "TEXT"),
        ("is_public", "BOOLEAN DEFAULT FALSE")
    ]
    
    for col_name, col_type in columns:
        try:
            await conn.execute(f"ALTER TABLE creators ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added column: {col_name}")
        except asyncpg.exceptions.DuplicateColumnError:
            print(f"⏭️ Column already exists: {col_name}")
    
    # ساخت جدول دسته‌بندی‌ها
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            emoji VARCHAR(10),
            slug VARCHAR(50) UNIQUE NOT NULL
        )
    """)
    print("✅ Created table: categories")
    
    # اضافه کردن دسته‌بندی‌های پیش‌فرض
    categories = [
        ("گیمینگ", "🎮", "gaming"),
        ("آشپزی", "🍳", "cooking"),
        ("تکنولوژی", "💻", "tech"),
        ("آموزشی", "📚", "education"),
        ("سرگرمی", "🎬", "entertainment"),
        ("لایف‌استایل", "💄", "lifestyle"),
        ("ورزشی", "⚽", "sports"),
        ("موسیقی", "🎵", "music"),
        ("سفر", "✈️", "travel"),
        ("کسب‌وکار", "💼", "business")
    ]
    
    for name, emoji, slug in categories:
        try:
            await conn.execute("""
                INSERT INTO categories (name, emoji, slug) 
                VALUES ($1, $2, $3)
                ON CONFLICT (slug) DO NOTHING
            """, name, emoji, slug)
        except:
            pass
    print("✅ Added default categories")
    
    await conn.close()
    print("\n🎉 Database updated successfully!")

asyncio.run(update_db())
