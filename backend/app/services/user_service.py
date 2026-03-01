from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            id=uuid4(),
            email=user_data.email,
            name=user_data.name,
            hashed_password=AuthService.hash_password(user_data.password),
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_or_create_google_user(self, google_data: dict) -> User:
        google_id = google_data.get("sub")
        email = google_data.get("email")
        name = google_data.get("name", email.split("@")[0] if email else "User")
        avatar_url = google_data.get("picture")

        result = await self.db.execute(select(User).where(User.google_id == google_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                id=uuid4(),
                google_id=google_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
            )
            self.db.add(user)
            await self.db.flush()
        else:
            user.name = name
            user.avatar_url = avatar_url
            await self.db.flush()
        
        return user
