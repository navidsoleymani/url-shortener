import json
import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        body_bytes = await request.body()
        try:
            body_str = body_bytes.decode("utf-8")
        except UnicodeDecodeError:
            body_str = str(body_bytes)

        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        headers = dict(request.headers)
        headers_filtered = {k: v for k, v in headers.items() if k.lower() not in {"authorization", "cookie"}}

        response = await call_next(Request(request.scope, receive))
        process_time = (time.time() - start_time) * 1000

        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        try:
            response_body_str = response_body.decode("utf-8")
        except Exception:
            response_body_str = "<binary>"

        logger.info(json.dumps({
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "status_code": response.status_code,
            "duration_ms": round(process_time, 2),
            "headers": headers_filtered,
            "request_body": body_str,
            "response_body": response_body_str[:1000]
        }))

        return StreamingResponse(iter([response_body]), status_code=response.status_code,
                                 headers=dict(response.headers))


def add_logging_middleware(app):
    app.add_middleware(LoggingMiddleware)
