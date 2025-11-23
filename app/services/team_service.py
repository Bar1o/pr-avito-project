from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TeamDB, UserDB
from app.repositories.user_repository import UserRepository
from app.schemas.errors import ErrorCode, ServiceException
from app.schemas.schemas import Team, TeamMember


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def create_team(self, data: Team) -> Team:
        """
        Upsert = update + insert.
        1. Создает команду, создает пользователей (=участников команды).
        2. Обновляет команду: обновляет пользователей.
        """
        unique_members_map = {member.user_id: member for member in data.members}
        data.members = list(unique_members_map.values())

        if await self.user_repo.get_team_by_name(data.team_name):
            existing_team_dto = await self.get_team(data.team_name)
            existing_members_sorted = sorted(existing_team_dto.members, key=lambda x: x.user_id)
            new_members_sorted = sorted(data.members, key=lambda x: x.user_id)

            if existing_members_sorted == new_members_sorted:
                raise ServiceException(
                    code=ErrorCode.TEAM_EXISTS,
                    message="team already exists",
                    status_code=400,
                )

        result = await self.session.execute(select(UserDB.user_id).where(UserDB.team_name == data.team_name))
        current_user_ids = set(result.scalars().all())  # пользователи, которые уже есть в БД

        incoming_user_ids = {member.user_id for member in data.members}
        ids_to_delete = current_user_ids - incoming_user_ids
        if ids_to_delete:
            stmt_delete = delete(UserDB).where(
                (UserDB.team_name == data.team_name) & (UserDB.user_id.in_(ids_to_delete))
            )
            await self.session.execute(stmt_delete)

        team = TeamDB(team_name=data.team_name)
        await self.session.merge(team)

        for member in data.members:
            user = UserDB(
                user_id=member.user_id,
                username=member.username,
                team_name=data.team_name,
                is_active=member.is_active,
            )
            await self.session.merge(user)

        await self.session.commit()
        return data

    async def get_team(self, team_name: str) -> Team:
        team_db = await self.user_repo.get_team_by_name(team_name)
        if not team_db:
            raise ServiceException(ErrorCode.NOT_FOUND, f"team {team_name} not found", 404)

        members_dto = [
            TeamMember(user_id=u.user_id, username=u.username, is_active=u.is_active) for u in team_db.members
        ]

        return Team(team_name=team_db.team_name, members=members_dto)
