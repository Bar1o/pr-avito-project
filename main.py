from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.endpoints import pull_requests, teams, users  # Added users
from app.db.session import engine
from app.models import Base
from app.schemas.errors import ServiceException, ErrorResponse, ErrorDetails


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(title="Avito PR Service", lifespan=lifespan)


@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    content = ErrorResponse(error=ErrorDetails(code=exc.code, message=exc.message)).model_dump()

    return JSONResponse(status_code=exc.status_code, content=content)


app.include_router(pull_requests.router, prefix="/pullRequest", tags=["PullRequests"])
app.include_router(teams.router, prefix="/team", tags=["Teams"])
app.include_router(users.router, prefix="/users", tags=["Users"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
