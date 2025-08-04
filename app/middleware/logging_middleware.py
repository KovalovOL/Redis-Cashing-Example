from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from fastapi import Request

from app.core.log_context import *


class LoggingContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        ip_address_ctx.set(ip)

        request_id = str(uuid4())
        request_id_ctx.set(request_id)

        responce = await call_next(request)
        return responce
