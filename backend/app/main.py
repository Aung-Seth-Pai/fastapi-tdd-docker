# project/backend/app/main.py

import asyncio
from fastapi import FastAPI, Depends
from app.config import get_settings, Settings
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()
register_tortoise(
    app,
    db_url=str(get_settings().database_url),
    modules={"models": ["app.models"]},
    generate_schemas=False,
    add_exception_handlers=True
)

@app.get("/hello")
def hello(settings: Settings = Depends(get_settings)):
    return {
        "hello": "world",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "testing": settings.testing
    }

@app.get("/async_hello")
async def async_hello(settings: Settings = Depends(get_settings)):
    print("Simulating async operation...")
    await asyncio.sleep(5) # Simulate async operation
    print("Async operation completed.")
    return {
        "hello": "world",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "testing": settings.testing,
        "db_url": settings.database_url
    }