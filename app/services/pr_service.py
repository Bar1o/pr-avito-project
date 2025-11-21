import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.pr_repository import PRRepository
from app.repositories.user_repository import UserRepository
from app.schemas.classes import PullRequestCreate, PullRequestResponse


class PRService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pr_repo = PRRepository(session)
        self.user_repo = UserRepository(session)

    async def create_pr(self, data: PullRequestCreate) -> PullRequestResponse:
        pass

    # how do i update reviewers?
    # how do i set status merge? where is its logic?
