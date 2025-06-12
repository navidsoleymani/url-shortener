import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.db.session import get_session
from app.main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(DATABASE_URL, echo=True)
async_session_test = async_sessionmaker(engine_test, expire_on_commit=False)


async def init_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def override_get_session():
    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_test_db()
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    # Override the dependency here
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    # Clear overrides after test
    app.dependency_overrides.clear()


async def api_v1_shorten(client, url):
    return await client.post(
        url="/api/v1/shorten/",
        json={"original_url": url},
        headers={'Content-Type': 'application/json'},
    )


async def api_v1_shorten_code(client, code):
    return await client.get(f"/api/v1/{code}/", follow_redirects=False)


async def api_v1_shorten_code_state(client, code):
    return await client.get(f"/api/v1/{code}/stats/")


@pytest.mark.asyncio
async def test_ping(client):
    res = await client.get("/api/v1/ping/")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_shorten_url(client):
    test_url = "https://www.google.com/search?q=Jagvar"
    res = await api_v1_shorten(client, url=test_url)
    assert res.status_code == 200
    data = res.json()
    assert "short_code" in data
    assert data["original_url"] == test_url


@pytest.mark.asyncio
async def test_redirect(client):
    test_url = "https://www.google.com/search?q=Bentley"
    res = await api_v1_shorten(client, url=test_url)
    assert res.status_code == 200
    data = res.json()
    code = data["short_code"]

    redirect = await api_v1_shorten_code(client, code=code)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == test_url


@pytest.mark.asyncio
async def test_stats(client):
    test_url = "https://www.google.com/search?q=Pagani"
    res = await api_v1_shorten(client, url=test_url)
    assert res.status_code == 200
    code = res.json()["short_code"]

    for _ in range(3):
        await api_v1_shorten_code(client, code=code)

    stats = await api_v1_shorten_code_state(client, code=code)
    assert stats.status_code == 200
    data = stats.json()
    assert data["visits"] == 3
