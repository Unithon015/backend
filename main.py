from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.application.incident_index.scheduler import (
    build_daily_2026_scheduler,
    should_start_daily_sync,
)
from src.interface.auth.router import router as auth_router
from src.interface.content.router import router as content_router
from src.database import engine
from src.infrastructure.db import models  # noqa: F401 - registers application models
from src.infrastructure.db.base import Base as ApplicationBase
from src.infrastructure.persistence.models import Base as IncidentIndexBase
from src.interface.namu_wiki.router import router as namu_wiki_router
from src.interface.user.router import router as user_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(ApplicationBase.metadata.create_all)
        await connection.run_sync(IncidentIndexBase.metadata.create_all)

    scheduler = None
    if should_start_daily_sync():
        scheduler = build_daily_2026_scheduler()
        scheduler.start()
    try:
        yield
    finally:
        if scheduler is not None:
            scheduler.shutdown(wait=False)

app = FastAPI(title="baekend", lifespan=lifespan)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(content_router)
app.include_router(namu_wiki_router)


@app.get("/health")
def health():
    return {"status": "ok"}
