from collections.abc import Awaitable, Callable
from urllib.parse import urlencode

from fastapi import Request, Response
from pydantic.alias_generators import to_snake
from starlette.middleware.base import BaseHTTPMiddleware

__all__ = [
    "CamelCaseQueryParamsMiddleware",
]


class CamelCaseQueryParamsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to normalize query parameter names from camelCase or PascalCase
    into snake_case for downstream FastAPI handlers.

    This middleware rewrites the incoming request's `query_string` so that
    all route functions, dependencies, and parameter declarations continue
    to use snake_case seamlessly.

    Example:
        ```
        # Client request: GET /items/?pageSize=10&userID=42
        # Handler signature: def read_items(page_size: int, user_id: str)
        # Received parameters: page_size=10, user_id="42"
        ```

    Use case:
        Ideal when interfacing with external clients who expect camelCase APIs,
        while the backend logic uses snake_case naming conventions.

    Usage:
        app = FastAPI()
        app.add_middleware(CamelCaseQueryParamsMiddleware)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        query_params = {
            to_snake(key): value for key, value in request.query_params.multi_items()
        }

        request.scope["query_string"] = urlencode(query_params, doseq=True).encode(
            "utf-8",
        )

        return await call_next(request)
