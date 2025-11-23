from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.errors import ErrorResponse
from app.schemas.schemas import Team
from app.services.team_service import TeamService

router = APIRouter()


@router.post(
    "/add",
    response_model=Team,
    status_code=201,
    responses={
        201: {"model": Team, "description": "Команда создана"},
        400: {"model": ErrorResponse, "description": "Команда уже существует"},
    },
)
async def add_team(team_data: Team, db: AsyncSession = Depends(get_db)):
    service = TeamService(db)
    return await service.create_team(team_data)


@router.get(
    "/get",
    response_model=Team,
    status_code=200,
    responses={
        200: {"model": Team, "description": "Объект команды"},
        404: {"model": ErrorResponse, "description": "Команда не найдена"},
    },
)
async def get_team(
    team_name: str = Query(..., description="Уникальное имя команды"), db: AsyncSession = Depends(get_db)
):
    service = TeamService(db)
    return await service.get_team(team_name)
