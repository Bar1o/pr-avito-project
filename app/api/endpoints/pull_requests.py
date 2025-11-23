from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.docs.pr_docs import create_pr_responses, merge_pr_responses, reassign_pr_responses
from app.schemas.schemas import (
    PRResponseWrapper,
    PullRequestCreate,
    PullRequestMerge,
    PullRequestReassign,
    ReassignResponse,
)
from app.services.pr_service import PRService

router = APIRouter()


@router.post(
    "/create",
    response_model=PRResponseWrapper,
    status_code=201,
    responses=create_pr_responses,
)
async def create_pull_request(data: PullRequestCreate, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.create_pr(data)


@router.post(
    "/merge",
    response_model=PRResponseWrapper,
    responses=merge_pr_responses,
)
async def merge_pr(data: PullRequestMerge, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.merge_pr(data.pull_request_id)


@router.post(
    "/reassign",
    response_model=ReassignResponse,
    responses=reassign_pr_responses,
)
async def reassign_reviewer(data: PullRequestReassign, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.reassign_reviewer(data.pull_request_id, data.old_user_id)
