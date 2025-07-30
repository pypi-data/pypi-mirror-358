"""
Middleware components for the API
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging
from typing import Dict, Any
from collections import defaultdict, deque
import asyncio


# Rate limiting storage
rate_limit_storage: Dict[str, deque] = defaultdict(lambda: deque())
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds


class RateLimitMiddleware:
    """Simple rate limiting middleware"""

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            client_ip = request.client.host

            # Check rate limit
            now = time.time()
            client_requests = rate_limit_storage[client_ip]

            # Remove old requests outside the window
            while client_requests and client_requests[0] < now - RATE_LIMIT_WINDOW:
                client_requests.popleft()

            # Check if limit exceeded
            if len(client_requests) >= RATE_LIMIT_REQUESTS:
                response = HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
                await response(scope, receive, send)
                return

            # Add current request
            client_requests.append(now)

        # Continue to next middleware/app
        await self.app(scope, receive, send)


class LoggingMiddleware:
    """Logging middleware for API requests"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = logging.getLogger(__name__)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            request = Request(scope, receive)

            # Log request
            self.logger.info(
                f"Request: {request.method} {request.url.path} "
                f"from {request.client.host}"
            )

            # Process request
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    status_code = message["status"]

                    # Log response
                    self.logger.info(
                        f"Response: {status_code} "
                        f"({process_time:.3f}s) "
                        f"for {request.method} {request.url.path}"
                    )

                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


def setup_middleware(app: FastAPI):
    """Setup all middleware for the FastAPI app"""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Configure appropriately for production
    )

    # Custom rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    # Custom logging middleware
    app.add_middleware(LoggingMiddleware)


def get_rate_limiter():
    """Dependency for rate limiting"""
    return lambda: None  # Rate limiting is handled by middleware


class SecurityMiddleware:
    """Security headers middleware"""

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                # Add security headers
                security_headers = {
                    b"X-Content-Type-Options": b"nosniff",
                    b"X-Frame-Options": b"DENY",
                    b"X-XSS-Protection": b"1; mode=block",
                    b"Strict-Transport-Security": b"max-age=31536000; includeSubDomains",
                    b"Content-Security-Policy": b"default-src 'self'",
                }

                headers.update(security_headers)
                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)


class MetricsMiddleware:
    """Middleware to collect API metrics"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.request_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_count = defaultdict(int)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            request = Request(scope, receive)
            path = request.url.path
            method = request.method

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    process_time = time.time() - start_time

                    # Record metrics
                    endpoint = f"{method} {path}"
                    self.request_count[endpoint] += 1
                    self.response_times[endpoint].append(process_time)

                    if status_code >= 400:
                        self.error_count[endpoint] += 1

                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        metrics = {
            "request_count": dict(self.request_count),
            "error_count": dict(self.error_count),
            "average_response_time": {},
        }

        for endpoint, times in self.response_times.items():
            if times:
                metrics["average_response_time"][endpoint] = sum(times) / len(times)

        return metrics
