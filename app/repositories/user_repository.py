from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import UserDB, TeamDB


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> UserDB | None:
        query = select(UserDB).options(selectinload(UserDB.assigned_prs)).where(UserDB.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_team_by_name(self, name: str) -> TeamDB | None:
        query = select(TeamDB).options(selectinload(TeamDB.members)).where(TeamDB.team_name == name)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create_team(self, team: TeamDB):
        self.session.add(team)

    async def get_team_members(self, team_name: str) -> list[UserDB]:
        result = await self.session.execute(select(UserDB).where(UserDB.team_name == team_name))
        return list(result.scalars().all())
