# backend/tests/conftest.py

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient
from tortoise import Tortoise

from app import main
from app.config import Settings, get_settings
from app.models.text_summary import TextSummary


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_URL"))


@pytest.fixture
def test_app():
    main.app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def async_client():
    main.app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as ac:
        yield ac
    main.app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def test_app_with_db():
    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.text_summary"]},
    )
    await Tortoise.generate_schemas()
    main.app.dependency_overrides[get_settings] = get_settings_override
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as ac:
        yield ac
    await TextSummary.all().delete()
    await Tortoise.close_connections()
    main.app.dependency_overrides.clear()
