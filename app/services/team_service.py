from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import Team, TeamMember, TeamResponseWrapper
from app.models import TeamDB, UserDB
from app.schemas.errors import ServiceException, ErrorCode


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def create_team(self, data: Team) -> TeamResponseWrapper:
        """
        Создает команду.
        Создает пользователей (=участников команды).
        """
        if await self.user_repo.get_team_by_name(data.team_name):
            raise ServiceException(
                code=ErrorCode.TEAM_EXISTS,
                message="team_name already exists",
                status_code=400,
            )

        new_team = TeamDB(team_name=data.team_name)

        new_users = []

        for member in data.members:
            # TODO: check if user exists globally, if exists, we add them
            # if user doesn't exist, we create them

            user = UserDB(
                user_id=member.user_id,
                username=member.username,
                is_active=member.is_active,
                team=new_team,
            )
            new_users.append(user)

        await self.user_repo.create_team(new_team)
        self.session.add_all(new_users)
        await self.session.commit()
        return TeamResponseWrapper(team=data)

    async def get_team(self, team_name: str) -> Team:
        team_db = await self.user_repo.get_team_by_name(team_name)
        if not team_db:
            raise ServiceException(ErrorCode.NOT_FOUND, f"team {team_name} not found", 404)

        members_dto = [TeamMember(user_id=u.user_id, username=u.username, is_active=u.is_active) for u in team_db.members]

        return Team(team_name=team_db.team_name, members=members_dto)
