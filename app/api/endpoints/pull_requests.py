from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.schemas import PullRequestResponse, PullRequestCreate
from app.services.pr_service import PRService

router = APIRouter()


@router.post("/create", response_model=PullRequestResponse, status_code=201)
async def create_pull_request(pr_data: PullRequestCreate, db: AsyncSession = Depends(get_db)):
    service = PRService(db)
    return await service.create_pr(pr_data)
