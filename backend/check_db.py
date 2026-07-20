import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from api.config import get_settings

async def check():
    s = get_settings()
    engine = create_async_engine(s.database_url)
    async with engine.connect() as conn:
        q = "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
        result = await conn.execute(text(q))
        tables = [row[0] for row in result.fetchall()]
        print("Tables in Neon DB:")
        for t in tables:
            print(" [OK]", t)
        print("Total:", len(tables), "tables")
    await engine.dispose()

asyncio.run(check())
