# project/app/main.py

import asyncio
from fastapi import FastAPI, Depends
from app.config import get_settings, Settings

app = FastAPI()

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
        "testing": settings.testing
    }