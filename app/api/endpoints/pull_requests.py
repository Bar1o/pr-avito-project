from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.schemas import PullRequestResponse, PullRequestCreate
from app.services.pr_service import PRService
from app.schemas.errors import ErrorResponse


router = APIRouter()


@router.post(
    "/create",
    response_model=PullRequestResponse,
    status_code=201,
    responses={
        201: {"model": PullRequestResponse, "description": "PR создан"},
        404: {"model": ErrorResponse, "description": "Автор/команда не найдены"},
        409: {"model": ErrorResponse, "description": "PR уже существует"},
    },
)
async def create_pull_request(pr_data: PullRequestCreate, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.create_pr(pr_data)
