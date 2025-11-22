from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.schemas import Team, TeamMember
from app.schemas.errors import ErrorResponse

from app.services.team_service import TeamService

router = APIRouter()


@router.post("/add", response_model=Team, status_code=201, responses={400: {"model": ErrorResponse}})
async def add_team(team_data: Team, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    return await service.create_team(team_data)
