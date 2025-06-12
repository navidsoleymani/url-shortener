import json
import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with timing and filtering.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Read the request body (must be buffered so downstream can read it again)
        body_bytes = await request.body()
        try:
            body_str = body_bytes.decode("utf-8")
        except UnicodeDecodeError:
            body_str = "<non-utf8 body>"

        # Restore body for downstream (FastAPI only reads once)
        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        # Sanitize headers (avoid sensitive info)
        headers = {k.lower(): v for k, v in dict(request.headers).items()}
        filtered_headers = {
            k: v for k, v in headers.items() if k not in {"authorization", "cookie", "set-cookie"}
        }

        # Get the response by passing the modified request downstream
        response = await call_next(Request(request.scope, receive))
        process_time = (time.time() - start_time) * 1000

        # Read and buffer response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # Decode response body (only if text or JSON)
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type or content_type.startswith("text/"):
            try:
                response_body_str = response_body.decode("utf-8")
            except UnicodeDecodeError:
                response_body_str = "<non-utf8 response body>"
        else:
            response_body_str = f"<{content_type} content>"

        # Log the HTTP interaction
        logger.info(json.dumps({
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "status_code": response.status_code,
            "duration_ms": round(process_time, 2),
            "headers": filtered_headers,
            "request_body": body_str[:1000],          # Avoid overlogging
            "response_body": response_body_str[:1000] # Limit response size
        }))

        # Reconstruct the response for the client
        return StreamingResponse(
            iter([response_body]),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )


def add_logging_middleware(app):
    """
    Registers the custom LoggingMiddleware to FastAPI app.
    """
    app.add_middleware(LoggingMiddleware)
