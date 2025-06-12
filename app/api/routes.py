from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.db.session import get_session
from app.schemas.routes import (
    HealthCheckResponse, URLResponse, URLCreateRequestBody,
    URLStatsResponse)

router = APIRouter(
    prefix="/api/v1",
    tags=["URL Shortener"],
    redirect_slashes=True
)


@router.get(
    "/ping/",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check if the service is running"
)
def ping(request: Request, session: AsyncSession = Depends(get_session)):
    return {"status": "ok"}


@router.post(
    "/shorten/",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten URL",
    response_description="The shortened URL information"
)
async def shorten_url(data: URLCreateRequestBody, session: AsyncSession = Depends(get_session)):
    return await crud.create_short_url(data.original_url, session)


@router.get(
    "/{short_code}/",
    summary="Redirect to original URL",
    response_description="Redirects to the original URL",
    responses={
        404: {"detail": "URL not found"},
    }
)
async def redirect(short_code: str, request: Request, session: AsyncSession = Depends(get_session)):
    url = await crud.get_url_by_code(short_code, session)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    rec = url.tuple()[0]
    await crud.create_visit(rec.id, request.client.host, session)
    return RedirectResponse(rec.original_url)


@router.get(
    "/{short_code}/stats/",
    response_model=URLStatsResponse,
    summary="Get URL statistics",
    responses={
        404: {"description": "URL not found"},
        200: {"visits": "URL visits count"},
    }
)
async def stats(short_code: str, session: AsyncSession = Depends(get_session)):
    visits = await crud.count_visits(short_code, session)
    return {"visits": visits}
