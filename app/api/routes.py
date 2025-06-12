from fastapi import APIRouter, HTTPException, Request, Depends, status, Body, Path
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.db.session import get_session
from app.schemas.routes import (
    HealthCheckResponse,
    URLResponse,
    URLCreateRequestBody,
    URLStatsResponse,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["URL Shortener"],
    redirect_slashes=True,
)


@router.get(
    "/ping/",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check if the service is running and reachable.",
)
def ping(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Simple health check endpoint to verify the service is up.
    """
    return {"status": "ok"}


@router.post(
    "/shorten/",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten a URL",
    description="Takes a long URL and returns a shortened version of it.",
    response_description="The shortened URL details",
    responses={
        201: {"description": "Successfully shortened the URL"},
        422: {"description": "Validation Error"},
    },
)
async def shorten_url(
    data: URLCreateRequestBody = Body(..., description="The original URL to shorten."),
    session: AsyncSession = Depends(get_session),
):
    """
    Accepts a long URL and generates a shortened version.
    """
    return await crud.create_short_url(data.original_url, session)


@router.get(
    "/{short_code}/",
    summary="Redirect to Original URL",
    description="Redirects the user to the original long URL using the short code.",
    responses={
        302: {"description": "Redirected successfully"},
        404: {"description": "Short code not found"},
    },
)
async def redirect(
    short_code: str = Path(..., description="The short code to redirect to the original URL."),
    request: Request = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Redirect to the original URL if the short code exists.
    Also logs the visit with client's IP.
    """
    url = await crud.get_url_by_code(short_code, session)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    record = url.tuple()[0]
    await crud.create_visit(record.id, request.client.host, session)
    return RedirectResponse(record.original_url)


@router.get(
    "/{short_code}/stats/",
    response_model=URLStatsResponse,
    summary="Get URL Statistics",
    description="Returns the number of visits for a given short URL.",
    responses={
        200: {"description": "Returns visit count for the short URL"},
        404: {"description": "Short code not found"},
    },
)
async def stats(
    short_code: str = Path(..., description="The short code to get statistics for."),
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieves the number of visits for the given short URL code.
    """
    visits = await crud.count_visits(short_code, session)
    if visits is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"visits": visits}
