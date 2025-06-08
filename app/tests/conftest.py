import pytest
from fastapi.testclient import TestClient

from app.database import engine
from app.main import app
from app.models import Base
from typing import AsyncGenerator
from httpx import AsyncClient

@pytest.fixture(autouse=True)
async def prepare_database() -> AsyncGenerator[AsyncClient, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client() -> AsyncGenerator[AsyncClient, None]:
    with TestClient(app) as client:
        yield client
