from fastapi import FastAPI
from src.interface.user.router import router as user_router

app = FastAPI(title="baekend")

app.include_router(user_router)


@app.get("/health")
def health():
    return {"status": "ok"}
