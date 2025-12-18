import asyncpg
from config import DATABASE_URL

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
    
    async def close(self):
        if self.pool:
            await self.pool.close()
    
    async def get_creator_by_slug(self, slug: str):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM creators WHERE slug = $1 AND is_active = TRUE",
                slug
            )
    
    async def add_user(self, user_id: int, username: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (telegram_id, username)
                VALUES ($1, $2)
                ON CONFLICT (telegram_id) DO UPDATE SET username = $2
            """, user_id, username)
    
    async def get_user_id(self, telegram_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id FROM users WHERE telegram_id = $1",
                telegram_id
            )
            return row['id'] if row else None
    
    async def create_transaction(self, ref_code: str, user_id: int, creator_id: int, amount: float, network: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO transactions (ref_code, user_id, creator_id, amount_expected, network, status)
                VALUES ($1, $2, $3, $4, $5, 'PENDING_TXID')
            """, ref_code, user_id, creator_id, amount, network)
    
    async def update_transaction_proof(self, ref_code: str, proof_type: str, proof_value: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE transactions 
                SET tx_proof_type = $2, tx_proof_value = $3, status = 'PENDING_REVIEW'
                WHERE ref_code = $1
            """, ref_code, proof_type, proof_value)
    
    async def get_transaction_by_ref(self, ref_code: str):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT t.*, u.telegram_id, u.username, c.name as creator_name
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                JOIN creators c ON t.creator_id = c.id
                WHERE t.ref_code = $1
            """, ref_code)
    
    async def approve_transaction(self, ref_code: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE transactions 
                SET status = 'APPROVED', amount_received = amount_expected
                WHERE ref_code = $1
            """, ref_code)
    
    async def reject_transaction(self, ref_code: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE transactions 
                SET status = 'REJECTED'
                WHERE ref_code = $1
            """, ref_code)
    
    async def get_user_donations(self, telegram_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT t.amount_expected, t.status, t.created_at, c.name as creator_name
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                JOIN creators c ON t.creator_id = c.id
                WHERE u.telegram_id = $1
                ORDER BY t.created_at DESC
                LIMIT 10
            """, telegram_id)
    
    async def get_user_stats(self, telegram_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_donations,
                    COALESCE(SUM(CASE WHEN status = 'APPROVED' THEN amount_received ELSE 0 END), 0) as total_amount
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE u.telegram_id = $1
            """, telegram_id)
    
    async def get_creator_debt(self, slug: str):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT 
                    c.name,
                    c.commission_rate,
                    COALESCE(SUM(t.amount_received), 0) as total_received,
                    COUNT(CASE WHEN t.status = 'APPROVED' THEN 1 END) as approved_count
                FROM creators c
                LEFT JOIN transactions t ON c.id = t.creator_id AND t.status = 'APPROVED'
                WHERE c.slug = $1
                GROUP BY c.id, c.name, c.commission_rate
            """, slug)
    
    async def add_creator(self, slug: str, name: str, wallet_bsc: str, wallet_polygon: str, wallet_tron: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO creators (slug, name, wallet_bsc, wallet_polygon, wallet_tron)
                VALUES ($1, $2, $3, $4, $5)
            """, slug, name, wallet_bsc, wallet_polygon, wallet_tron)
    
    async def link_creator_telegram(self, slug: str, telegram_id: int) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE creators 
                SET telegram_id = $2
                WHERE slug = $1
            """, slug, telegram_id)
            return result != "UPDATE 0"
    
    async def get_all_creators(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT id, slug, name, telegram_id, is_active
                FROM creators
                ORDER BY id DESC
            """)
    
    # --- بخش اسپانسرینگ ---
    async def add_lead(self, sponsor_name: str, contact: str, budget: str, desc: str, sponsor_tg_id: int, creator_id: int = None):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                INSERT INTO sponsor_leads (sponsor_name, contact_info, budget_range, description, sponsor_tg_id, creator_id)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, sponsor_name, contact, budget, desc, sponsor_tg_id, creator_id)

    async def get_lead(self, lead_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT l.*, c.name as creator_name, c.telegram_id as creator_tg_id, c.slug as creator_slug
                FROM sponsor_leads l
                LEFT JOIN creators c ON l.creator_id = c.id
                WHERE l.id = $1
            """, lead_id)

    async def update_lead_status(self, lead_id: int, status: str):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE sponsor_leads SET status = $2 WHERE id = $1", lead_id, status)

db = Database()
