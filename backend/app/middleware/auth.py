from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import Request

from app.utils import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Only attempt to decode bearer tokens for API routes
        if request.url.path.startswith("/api/"):
            auth = request.headers.get("Authorization")
            if auth and auth.startswith("Bearer "):
                token = auth.split(None, 1)[1]
                payload = decode_token(token)
                # attach payload for downstream dependencies
                request.state.token_payload = payload
        return await call_next(request)
