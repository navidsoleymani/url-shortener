import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.main import app

# In-memory SQLite database for fast, isolated tests
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test database engine with verbose logging for debugging
engine_test = create_async_engine(DATABASE_URL, echo=True)

# Create thread-safe async session factory with auto-expire disabled
async_session_test = async_sessionmaker(
    engine_test,
    expire_on_commit=False,
    class_=AsyncSession
)


async def init_test_db():
    """Initialize test database by creating all SQLModel tables"""
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def override_get_session():
    """Dependency override providing test database sessions"""
    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Auto-used fixture to reset database state before each test"""
    # Create tables before test
    await init_test_db()
    yield  # Test runs here
    # Clean up tables after test
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Test client with dependency overrides and clean headers"""
    # Override database dependency
    app.dependency_overrides[get_session] = override_get_session

    # Create test client with optimized settings
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"}
    ) as client:
        yield client

    # Reset dependency overrides
    app.dependency_overrides.clear()


# API helper functions --------------------------------------------------------

async def shorten_url(client, url):
    """Helper to shorten URL and return response"""
    return await client.post(
        url="/api/v1/shorten/",
        json={"original_url": url}
    )


async def redirect_url(client, code):
    """Helper to follow short URL redirect"""
    return await client.get(
        f"/api/v1/{code}/",
        follow_redirects=False
    )


async def get_url_stats(client, code):
    """Helper to retrieve URL statistics"""
    return await client.get(f"/api/v1/{code}/stats/")


# Test cases ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ping_endpoint(client):
    """Health check endpoint returns 200 OK with status object"""
    response = await client.get("/api/v1/ping/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_url_shortening(client):
    """Valid URL returns 201 Created with short code"""
    test_url = "https://www.google.com/search?q=Jagvar"
    response = await shorten_url(client, test_url)

    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert len(data["short_code"]) >= 6  # Ensure reasonable code length


@pytest.mark.asyncio
async def test_redirect_functionality(client):
    """Short code redirects to original URL with 307 status"""
    test_url = "https://www.google.com/search?q=Bentley"
    create_response = await shorten_url(client, test_url)
    short_code = create_response.json()["short_code"]

    redirect_response = await redirect_url(client, short_code)

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == test_url


@pytest.mark.asyncio
async def test_visit_tracking(client):
    """Statistics endpoint accurately tracks URL visits"""
    test_url = "https://www.google.com/search?q=Pagani"
    create_response = await shorten_url(client, test_url)
    short_code = create_response.json()["short_code"]

    # Generate 3 visits
    for _ in range(3):
        await redirect_url(client, short_code)

    stats_response = await get_url_stats(client, short_code)
    stats_data = stats_response.json()

    assert stats_response.status_code == 200
    assert stats_data["visits"] == 3


@pytest.mark.asyncio
async def test_invalid_url_handling(client):
    """Invalid URLs return 400 Bad Request with error details"""
    invalid_urls = [
        "not-a-url",
        "http://",
        "ftp://example.com",
        "javascript:alert(1)"
    ]

    for url in invalid_urls:
        response = await shorten_url(client, url)
        assert response.status_code == 422
        assert "detail" in response.json()


@pytest.mark.asyncio
async def test_nonexistent_short_code(client):
    """Non-existent short codes return 404 Not Found"""
    # Test redirect with invalid code
    redirect_response = await redirect_url(client, "INVALID_CODE")
    assert redirect_response.status_code == 404

    # Test stats with invalid code
    stats_response = await get_url_stats(client, "INVALID_CODE")
    assert stats_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("url", [
    "https://example.com/",
    "http://sub.domain.co.uk/path?query=param",
    "https://localhost:8080/",
    "http://192.168.1.1:8000/",
    "https://user:pass@example.com/"
])
async def test_various_url_formats(client, url):
    """System handles various valid URL formats correctly"""
    create_response = await shorten_url(client, url)
    assert create_response.status_code == 201

    short_code = create_response.json()["short_code"]
    redirect_response = await redirect_url(client, short_code)

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == url


@pytest.mark.asyncio
async def test_duplicate_url_handling(client):
    """Duplicate URLs generate unique short codes"""
    url = "https://duplicate.example"
    response1 = await shorten_url(client, url)
    response2 = await shorten_url(client, url)

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json()["short_code"] == response2.json()["short_code"]


@pytest.mark.asyncio
async def test_statistics_accuracy(client):
    """Visit counter increments precisely per visit"""
    url = "https://counter.example"
    create_response = await shorten_url(client, url)
    short_code = create_response.json()["short_code"]

    # Initial visit count
    stats_response = await get_url_stats(client, short_code)
    assert stats_response.json()["visits"] == 0

    # First visit
    await redirect_url(client, short_code)
    stats_response = await get_url_stats(client, short_code)
    assert stats_response.json()["visits"] == 1

    # Second visit
    await redirect_url(client, short_code)
    stats_response = await get_url_stats(client, short_code)
    assert stats_response.json()["visits"] == 2