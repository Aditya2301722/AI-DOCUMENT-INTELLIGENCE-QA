from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class GlobalErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        # ✅ Let FastAPI handle HTTPExceptions (409, 404, etc.)
        except HTTPException as exc:
            raise exc

        # ❌ Catch only unexpected errors
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "Something went wrong. Please try again later."
                }
            )
