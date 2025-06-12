import random
import string

from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy import func

from app.db.models import URL, URLVisit


def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).lower()


async def create_short_url(original_url: HttpUrl, session: AsyncSession):
    url = await get_url(original_url, session)
    if url:
        return url

    while True:
        code = generate_code(length=random.randint(6, 15))
        existing = await get_url_by_code(code, session)
        if not existing:
            break
    short_url = URL(original_url=str(original_url), short_code=code)
    session.add(short_url)
    await session.commit()
    await session.refresh(short_url)
    return short_url


async def get_url_by_code(code: str, session: AsyncSession):
    stmt = select(URL).where(URL.short_code == code)
    result = await session.execute(stmt)
    return result.first()


async def get_url(url: HttpUrl, session: AsyncSession):
    stmt = select(URL).where(URL.original_url == str(url))
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_visit(url_id: int, ip: str, session: AsyncSession):
    visit = URLVisit(url_id=url_id, ip_address=ip)
    session.add(visit)
    await session.commit()


async def count_visits(short_code: str, session: AsyncSession):
    stmt = select(func.count(URLVisit.id)).join(URLVisit.url).where(URL.short_code == short_code)
    result = await session.execute(stmt)
    return result.scalar_one()
