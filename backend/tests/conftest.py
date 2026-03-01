import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.database import Base
from app.config import get_settings

@pytest.fixture
async def db():
    """A fully isolated database session for each test."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    
    # 1. Cleanup & Init Phase
    async with engine.connect() as conn:
        try:
            # Try a clean drop first
            async with conn.begin():
                await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            # Atomic schema reset if drop_all fails due to deps
            async with conn.begin():
                await conn.execute(text("DROP SCHEMA public CASCADE"))
                await conn.execute(text("CREATE SCHEMA public"))
        
        # Fresh Create
        async with conn.begin():
            await conn.run_sync(Base.metadata.create_all)
    
    # 2. Test Phase
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
    
    # 3. Teardown Phase
    async with engine.connect() as conn:
        try:
            async with conn.begin():
                await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            async with conn.begin():
                await conn.execute(text("DROP SCHEMA public CASCADE"))
                await conn.execute(text("CREATE SCHEMA public"))
    
@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user for database tests."""
    from app.models.user import User
    import uuid
    
    user = User(
        id=uuid.uuid4(),
        email=f"test-{uuid.uuid4().hex[:6]}@example.com",
        name="Test User",
        onboarding_complete=True
    )
    db.add(user)
    await db.flush()
    return user
