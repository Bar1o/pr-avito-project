from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import Team
from app.models import TeamDB, UserDB
from app.schemas.errors import ServiceException, ErrorCode


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def create_team(self, data: Team) -> Team:
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

        new_team = TeamDB(name=data.team_name)

        new_users = []

        for member in data.members:
            # TODO: ok, let's assume that we create a user
            # if await self.user_repo.get_by_id(member.user_id):
            #     raise ServiceException(
            #         code=ErrorCode.TEAM_EXISTS,
            #         message=f"user {member.user_id} alredy exists",
            #         status_code=409,
            #     )

            user = UserDB(
                id=member.user_id,
                name=member.username,
                is_active=member.is_active,
                team=new_team,
            )
            new_users.append(user)

        await self.user_repo.create_team(new_team)
        self.session.add_all(new_users)
        await self.session.commit()
        return Team(team_name=new_team.name, members=data.members)
