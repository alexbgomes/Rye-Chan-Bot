import aiosqlite
import yaml
import os

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

DB_PATH = config.get("database", {}).get("path", "data/bot_database.sqlite3")

async def setup_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS confessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                count INTEGER DEFAULT 0
            )
        """)
        # Insert initial row if not exists
        await db.execute("""
            INSERT INTO confessions (id, count)
            SELECT 1, 0
            WHERE NOT EXISTS (SELECT 1 FROM confessions WHERE id = 1)
        """)
        
        # Add other tables as necessary
        
        await db.commit()

async def get_confession_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT count FROM confessions WHERE id = 1") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def increment_confession_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE confessions SET count = count + 1 WHERE id = 1")
        await db.commit()
        return await get_confession_count()
