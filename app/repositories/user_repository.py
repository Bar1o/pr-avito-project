from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import UserDB, TeamDB


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> UserDB | None:
        result = await self.session.execute(select(UserDB).where(UserDB.id == user_id))
        return result.scalars().first()

    async def get_team_members(self, team_name: str) -> list[UserDB]:
        result = await self.session.execute(select(UserDB).where(UserDB.team_name == team_name))
        return list(result.scalars().all())
