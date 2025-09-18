from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = time.time()
        request_times = self.clients.get(ip, [])
        request_times = [t for t in request_times if now - t < self.window_seconds]
        if len(request_times) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Too many requests")
        request_times.append(now)
        self.clients[ip] = request_times
        return await call_next(request)
