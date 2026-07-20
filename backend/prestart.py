import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from api.config import get_settings

async def main():
    s = get_settings()
    if not s.database_url:
        print("DATABASE_URL not set, skipping prestart.")
        return
    
    # Alembic's sync engine needs sync URL, but we can do a quick check via async
    engine = create_async_engine(s.database_url)
    
    async with engine.connect() as conn:
        # Check if birth_profiles exists
        result = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'birth_profiles');")
        )
        has_tables = result.scalar()
        
        # Check if alembic_version has any rows
        has_alembic_rows = False
        if has_tables:
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');")
            )
            if result.scalar():
                row_res = await conn.execute(text("SELECT count(*) FROM alembic_version"))
                if row_res.scalar() > 0:
                    has_alembic_rows = True
        
    await engine.dispose()
    
    if has_tables and not has_alembic_rows:
        print("Existing database detected without alembic_version rows. Stamping initial schema...")
        # Stamp with the initial schema revision so alembic knows it's already applied
        os.system("alembic stamp 2b735dc1e338")
    else:
        print("Database is ready for normal migrations.")

if __name__ == "__main__":
    asyncio.run(main())
