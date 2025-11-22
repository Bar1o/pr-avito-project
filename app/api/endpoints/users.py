from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.schemas import UserIsActiveUpdate, UserResponseWrapper, UserReviewsResponse
from app.schemas.errors import ErrorResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/setIsActive",
    response_model=UserResponseWrapper,
    responses={
        200: {"description": "Обновлённый пользователь"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
)
async def set_is_active(data: UserIsActiveUpdate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.set_is_active(data)


@router.get(
    "/getReview",
    response_model=UserReviewsResponse,
    responses={
        200: {"description": "Список PR'ов пользователя"},
        404: {"model": ErrorResponse, "description": "Пользователь не найден"},
    },
)
async def get_user_reviews(user_id: str = Query(..., description="Идентификатор пользователя"), db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_user_reviews(user_id)
