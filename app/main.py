from fastapi import FastAPI
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.community import router as community_router

from app.middleware.logging_middleware import LoggingContextMiddleware


app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["User"])
app.include_router(community_router, prefix="/communites", tags=["Community"])

app.add_middleware(LoggingContextMiddleware)


async def ping():
    return {"ping", "pong"}