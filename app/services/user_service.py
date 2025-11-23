from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.errors import ErrorCode, ServiceException
from app.schemas.schemas import PullRequestShort, User, UserIsActiveUpdate, UserResponseWrapper, UserReviewsResponse


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def set_is_active(self, data: UserIsActiveUpdate) -> User:
        user = await self.repo.get_by_id(data.user_id)
        if not user:
            raise ServiceException(ErrorCode.NOT_FOUND, "user not found", 404)

        user.is_active = data.is_active
        await self.session.commit()

        return UserResponseWrapper(
            user=User(
                user_id=user.user_id,
                username=user.username,
                team_name=user.team_name,
                is_active=user.is_active,
            )
        )

    async def get_user_reviews(self, user_id: str) -> UserReviewsResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ServiceException(ErrorCode.NOT_FOUND, "user not found", 404)

        prs_dto = [
            PullRequestShort(
                pull_request_id=pr.pull_request_id,
                pull_request_name=pr.pull_request_name,
                author_id=pr.author_id,
                status=pr.status,
            )
            for pr in user.assigned_prs
        ]

        return UserReviewsResponse(user_id=user.user_id, pull_requests=prs_dto)
