# hok/cache_manager.py
import aiosqlite
import orjson as json
import time
from typing import Any, Optional, List

DB_FILE = "hok_api_cache.db"
CACHE_TTL_SECONDS = 3000
PARAM_REUSE_COOLDOWN_SECONDS = 3600

class CacheManager:
    """
    Manages SQLite database for caching API responses and other persistent data,
    including the pool of security parameters.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CacheManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_file: str = DB_FILE):
        if not hasattr(self, '_initialized'):
            self.db_file = db_file
            self._initialized = True

    async def initialize(self):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("PRAGMA busy_timeout = 5000;")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    timestamp INTEGER
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS key_value_store (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS param_pool (
                    param TEXT PRIMARY KEY,
                    use_count INTEGER NOT NULL DEFAULT 0,
                    last_used_timestamp INTEGER NOT NULL DEFAULT 0
                )
            """)
            await db.commit()

    async def get(self, key: str) -> Optional[Any]:
        """Retrieves a cached API response if it exists and is not expired."""
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT value, timestamp FROM api_cache WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    value, timestamp = row
                    if time.time() - timestamp < CACHE_TTL_SECONDS:
                        return json.loads(value)
        return None

    async def set(self, key: str, value: Any):
        """Stores an API response in the cache with a TTL."""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(
                "REPLACE INTO api_cache (key, value, timestamp) VALUES (?, ?, ?)",
                (key, json.dumps(value), int(time.time())),
            )
            await db.commit()

    async def add_new_params(self, params: List[str]):
        """Adds a list of new specialencodeparams to the pool, ignoring duplicates."""
        async with aiosqlite.connect(self.db_file) as db:
            data = [(param,) for param in params]
            await db.executemany(
                "INSERT OR IGNORE INTO param_pool (param, use_count, last_used_timestamp) VALUES (?, 0, 0)",
                data
            )
            await db.commit()

    async def get_available_param_uses_count(self) -> int:
        """Counts the total number of available uses (params used < 2 times)."""
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT COUNT(*) FROM param_pool WHERE use_count < 2") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_and_update_available_param(self) -> Optional[str]:
        """
        Atomically finds an available param, increments its use count,
        updates its timestamp, and returns it.
        """
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("BEGIN")
            try:
                # Prio 1: Find a param that has been used 0 or 1 times.
                async with db.execute(
                    "SELECT param FROM param_pool WHERE use_count < 2 ORDER BY use_count ASC, last_used_timestamp ASC LIMIT 1"
                ) as cursor:
                    row = await cursor.fetchone()

                # Prio 2: If no fresh params, find one that has been used twice but has cooled down.
                if not row:
                    cooldown_time = int(time.time()) - PARAM_REUSE_COOLDOWN_SECONDS
                    async with db.execute(
                        """
                        SELECT param FROM param_pool
                        WHERE use_count >= 2 AND last_used_timestamp < ?
                        ORDER BY last_used_timestamp ASC LIMIT 1
                        """,
                        (cooldown_time,)
                    ) as cursor:
                        row = await cursor.fetchone()

                if row:
                    param = row[0]
                    await db.execute(
                        """
                        UPDATE param_pool
                        SET use_count = use_count + 1, last_used_timestamp = ?
                        WHERE param = ?
                        """,
                        (int(time.time()), param)
                    )
                    await db.commit()
                    return param
                else:
                    await db.rollback()
                    return None
            except Exception:
                await db.rollback()
                raise


cache_manager = CacheManager()
