import asyncpg
import os

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    
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

db = Database()
