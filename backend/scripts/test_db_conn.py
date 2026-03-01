
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings

async def test_conn():
    settings = get_settings()
    print(f"Testing connection to: {settings.database_url}")
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.connect() as conn:
            print("Successfully connected to the database!")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_conn())
