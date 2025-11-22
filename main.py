from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.endpoints import pull_requests
from app.db.session import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(title="Avito PR Service", lifespan=lifespan)

app.include_router(pull_requests.router, prefix="/pullRequest", tags=["PullRequests"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
