import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import PullRequestDB
from app.repositories.pr_repository import PRRepository
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import PullRequestCreate, PRResponseWrapper, ReassignResponse, PullRequest
from app.schemas.errors import ServiceException, ErrorCode


class PRService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pr_repo = PRRepository(session)
        self.user_repo = UserRepository(session)

    async def create_pr(self, data: PullRequestCreate) -> PRResponseWrapper:
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

        candidates = [u for u in team_members if u.is_active and u.user_id != author.user_id]

        k = min(len(candidates), 2)
        selected_reviewers = random.sample(candidates, k)

        new_pr = PullRequestDB(
            pull_request_id=data.pull_request_id,
            pull_request_name=data.pull_request_name,
            author_id=author.user_id,
            status="OPEN",
            reviewers=selected_reviewers,
        )
        await self.pr_repo.create(new_pr)
        await self.session.commit()

        return PRResponseWrapper(pr=self._map_to_dto(new_pr))

    async def merge_pr(self, pr_id: str) -> PRResponseWrapper:
        pr = await self.pr_repo.get_by_id(pr_id)
        if not pr:
            raise ServiceException(ErrorCode.NOT_FOUND, "PR not found", 404)

        if pr.status == "MERGED":
            return PRResponseWrapper(pr=self._map_to_dto(pr))

        pr.status = "MERGED"
        pr.merged_at = datetime.now()
        await self.session.commit()

        return PRResponseWrapper(pr=self._map_to_dto(pr))

    async def reassign_reviewer(self, pr_id: str, old_user_id: str) -> ReassignResponse:
        pr = await self.pr_repo.get_by_id(pr_id)
        if not pr:
            raise ServiceException(ErrorCode.NOT_FOUND, "PR not found", 404)

        if pr.status == "MERGED":
            raise ServiceException(ErrorCode.PR_MERGED, "cannot reassign on merged PR", 409)

        current_reviewer_ids = [u.user_id for u in pr.reviewers]
        if old_user_id not in current_reviewer_ids:
            raise ServiceException(ErrorCode.NOT_ASSIGNED, "user is not a reviewer", 409)

        old_user = await self.user_repo.get_by_id(old_user_id)
        if not old_user:
            raise ServiceException(ErrorCode.NOT_FOUND, "old reviewer user not found", 404)

        team_members = await self.user_repo.get_team_members(old_user.team_name)

        candidates = [u for u in team_members if u.is_active and u.user_id != pr.author_id and u.user_id not in current_reviewer_ids]
        if not candidates:
            raise ServiceException(ErrorCode.NO_CANDIDATE, "no active replacement candidate", 409)

        new_reviewer = random.choice(candidates)

        pr.reviewers = [u for u in pr.reviewers if u.user_id != old_user_id]
        pr.reviewers.append(new_reviewer)

        await self.session.commit()

        return ReassignResponse(pr=self._map_to_dto(pr), replaced_by=new_reviewer.user_id)

    def _map_to_dto(self, pr: PullRequestDB) -> PullRequest:
        return PullRequest(
            pull_request_id=pr.pull_request_id,
            pull_request_name=pr.pull_request_name,
            author_id=pr.author_id,
            status=pr.status,
            assigned_reviewers=[u.user_id for u in pr.reviewers],
            created_at=pr.created_at,
            merged_at=pr.merged_at,
        )
