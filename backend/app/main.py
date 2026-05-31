# project/backend/app/main.py

from fastapi import FastAPI
from app.api.hello_router import router as hello_router
from app.db import init_db
import logging

log = logging.getLogger("uvicorn")

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(hello_router, prefix="/api", tags=["hello"])
    return app

app = create_app()
init_db(app)