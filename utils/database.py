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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS listen_configs (
                code TEXT PRIMARY KEY,
                source_channel_id INTEGER,
                source_user_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mirrors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                dest_channel_id INTEGER,
                FOREIGN KEY(code) REFERENCES listen_configs(code) ON DELETE CASCADE
            )
        """)

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

async def create_listen(code: str, source_channel_id: int, source_user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO listen_configs (code, source_channel_id, source_user_id) VALUES (?, ?, ?)",
            (code, source_channel_id, source_user_id)
        )
        await db.commit()

async def get_listen_by_code(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT source_channel_id, source_user_id FROM listen_configs WHERE code = ?", (code,)) as cursor:
            return await cursor.fetchone()

async def delete_listen(code: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("DELETE FROM listen_configs WHERE code = ?", (code,)) as cursor:
            rows_deleted = cursor.rowcount
        if rows_deleted > 0:
            await db.execute("DELETE FROM mirrors WHERE code = ?", (code,))
            await db.commit()
            return True
        return False

async def add_mirror(code: str, dest_channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO mirrors (code, dest_channel_id) VALUES (?, ?)",
            (code, dest_channel_id)
        )
        await db.commit()

async def remove_mirror(code: str, dest_channel_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("DELETE FROM mirrors WHERE code = ? AND dest_channel_id = ?", (code, dest_channel_id)) as cursor:
            rows_deleted = cursor.rowcount
        await db.commit()
        return rows_deleted > 0

async def get_mirrors_for_source(source_channel_id: int, source_user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT m.dest_channel_id 
            FROM listen_configs l
            JOIN mirrors m ON l.code = m.code
            WHERE l.source_channel_id = ? AND l.source_user_id = ?
        """, (source_channel_id, source_user_id)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
