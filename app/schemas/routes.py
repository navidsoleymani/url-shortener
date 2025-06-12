from pydantic import BaseModel, HttpUrl, Field


class HealthCheckResponse(BaseModel):
    """
    Response model for the health check endpoint.
    """
    status: str = Field(
        ...,
        example="ok",
        description="Receiving 'ok' indicates that everything is running correctly."
    )


class URLCreateRequestBody(BaseModel):
    """
    Request body for shortening a new URL.
    """
    original_url: HttpUrl = Field(
        ...,
        example="https://example.com/long/url/to/be/shortened",
        description="The original URL that needs to be shortened."
    )


class URLResponse(BaseModel):
    """
    Response containing the generated short code for a given URL.
    """
    short_code: str = Field(
        ...,
        min_length=4,
        max_length=32,
        example="wefwrwrf",
        description="Generated short code (4–32 alphanumeric characters)."
    )


class URLStatsResponse(BaseModel):
    """
    Response model for statistics about a shortened URL.
    """
    visits: int = Field(
        ...,
        example=42,
        description="Number of times this short URL has been visited."
    )
