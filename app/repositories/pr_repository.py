from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import PullRequestDB


class PRRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pr_id: str) -> PullRequestDB | None:
        query = select(PullRequestDB).options(selectinload(PullRequestDB.reviewers)).where(PullRequestDB.pull_request_id == pr_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create(self, pr: PullRequestDB):
        self.session.add(pr)
