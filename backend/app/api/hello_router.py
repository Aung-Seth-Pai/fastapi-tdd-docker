# backend/app/api/hello_router.py
import asyncio
from fastapi import APIRouter, Depends
from app.config import get_settings, Settings

router = APIRouter()

@router.get("/hello")
def hello(settings: Settings = Depends(get_settings)):
    return {
        "hello": "world",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "testing": settings.testing
    }

@router.get("/async_hello")
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