# backend/tests/conftest.py

import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport 
# from starlette.testclient import TestClient

from app import main
from app.config import get_settings, Settings
from tortoise.contrib.test import initializer, finalizer

def get_settings_override():
    return Settings(
        testing=1, 
        database_url=os.environ.get("DATABASE_URL")
        )
 
# # define eventloop fixture for async tests
# @pytest.fixture(scope="session")
# def event_loop(request):
#     """ create an event loop for entire test session """
#     import asyncio
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()

@pytest.fixture(scope="session", autouse=True)
def initialize_tests():
    """
        Initialize Tortoise ORM with the test database.
        This creates tables in web_test.
    """
    initializer(
        modules=["app.models.text_summary"],
        db_url=os.environ.get("DATABASE_URL"),
        app_label="models"
    )
    yield
    finalizer()

@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def async_client():
    main.app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(transport=ASGITransport(app=main.app), 
                           base_url="http://test") as ac:
        yield ac
    main.app.dependency_overrides.clear()
