# project/backend/app/main.py

import logging

from fastapi import FastAPI

from app.api.hello_router import router as hello_router
from app.api.summaries import router as summaries
from app.db import init_db

log = logging.getLogger("uvicorn")


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(hello_router, prefix="/api", tags=["hello"])
    app.include_router(summaries, prefix="/api", tags=["summaries"])
    return app


app = create_app()
init_db(app)
