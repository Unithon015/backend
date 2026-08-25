from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database import engine
from src.infrastructure.db.base import Base
from src.infrastructure.db import models  # noqa: F401 — ensures models are registered
from src.interface.user.router import router as user_router
from src.interface.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="baekend", lifespan=lifespan)
app.include_router(user_router)
app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}
