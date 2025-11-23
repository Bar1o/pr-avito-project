from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.endpoints import pull_requests, teams, users
from app.models import Base
from app.schemas.errors import ErrorDetails, ErrorResponse, ServiceException


app = FastAPI(title="Avito PR Service")


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
