import random

from sqlalchemy.ext.asyncio import AsyncSession
from app.models import PullRequestDB
from app.repositories.pr_repository import PRRepository
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import PullRequestCreate, PullRequestResponse
from app.schemas.errors import ServiceException, ErrorResponse, ErrorCode


class PRService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pr_repo = PRRepository(session)
        self.user_repo = UserRepository(session)

    async def create_pr(self, data: PullRequestCreate) -> PullRequestResponse:
        if await self.pr_repo.get_by_id(data.pull_request_id):
            raise ServiceException(
                code=ErrorCode.TEAM_EXISTS,
                message="PR id already exists",
                status_code=409,
            )

        author = await self.user_repo.get_by_id(data.author_id)
        if not author:
            raise ServiceException(
                code=ErrorCode.NOT_FOUND,
                message="author not found",
                status_code=404,
            )

        if not author.team_name:
            raise ServiceException(
                code=ErrorCode.NOT_FOUND,
                message="team not found",
                status_code=404,
            )

        team_members = await self.user_repo.get_team_members(author.team_name)

        candidates = [u for u in team_members if u.is_active and u.id != author.id]

        k = min(len(candidates), 2)
        selected_reviewers = random.sample(candidates, k)

        new_pr = PullRequestDB(
            id=data.pull_request_id,
            name=data.pull_request_name,
            author_id=author.id,
            status="OPEN",
            reviewers=selected_reviewers,
        )
        await self.pr_repo.create(new_pr)
        await self.session.commit()

        return PullRequestResponse(
            pull_request_id=new_pr.id,
            pull_request_name=new_pr.name,
            author_id=new_pr.author_id,
            status=new_pr.status,
            assigned_reviewers=[u.id for u in new_pr.reviewers],
            created_at=new_pr.created_at,
        )

    # how do i update reviewers?
    # how do i set status merge? where is its logic?
