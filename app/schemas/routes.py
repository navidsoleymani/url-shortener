from pydantic import BaseModel, HttpUrl, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(
        example="ok",
        description="Receiving \"ok\" indicates that everything is correct."
    )


class URLResponse(BaseModel):
    short_code: str = Field(
        min_length=4,
        max_length=32,
        example="wefwrwrf",
        description="Short code (4-32 chars, alphanumeric)"
    )


class URLCreateRequestBody(BaseModel):
    original_url: HttpUrl = Field(
        example="https://example.com/long/url/to/be/shortened",
        description="The original URL to be shortened"
    )


class URLStatsResponse(BaseModel):
    visits: int = Field(

    )
