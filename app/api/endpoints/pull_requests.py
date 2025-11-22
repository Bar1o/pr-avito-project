from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.schemas import PullRequestCreate, PRResponseWrapper, PullRequestMerge, PullRequestReassign, ReassignResponse
from app.schemas.errors import ErrorResponse
from app.services.pr_service import PRService

router = APIRouter()


@router.post(
    "/create",
    response_model=PRResponseWrapper,
    status_code=201,
    responses={
        201: {"description": "PR создан"},
        404: {"model": ErrorResponse, "description": "Автор/команда не найдены"},
        409: {"model": ErrorResponse, "description": "PR уже существует"},
    },
)
async def create_pull_request(data: PullRequestCreate, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.create_pr(data)


@router.post(
    "/merge",
    response_model=PRResponseWrapper,
    responses={
        200: {"description": "PR в состоянии MERGED"},
        404: {"model": ErrorResponse, "description": "PR не найден"},
    },
)
async def merge_pr(data: PullRequestMerge, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.merge_pr(data.pull_request_id)


@router.post(
    "/reassign",
    response_model=ReassignResponse,
    responses={
        200: {"description": "Переназначение выполнено"},
        404: {"model": ErrorResponse, "description": "PR или пользователь не найден"},
        409: {"model": ErrorResponse, "description": "Нарушение доменных правил"},
    },
)
async def reassign_reviewer(data: PullRequestReassign, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.reassign_reviewer(data.pull_request_id, data.old_user_id)
