from functools import wraps

from app.api.schemas.common_schemas import ErrorResponseSchema
from app.api.schemas.v2_schema import V2ErrorSchema


def with_common_error_responses(bp):
    """共通のエラーレスポンス（400,401,403）を追加する簡素版デコレーター"""

    def decorator(func):
        @bp.alt_response(
            400,
            {
                "description": "Bad Request",
                "schema": ErrorResponseSchema,
                "content_type": "application/json",
            },
        )
        @bp.alt_response(
            401,
            {
                "description": "Unauthorized",
                "schema": ErrorResponseSchema,
                "content_type": "application/json",
            },
        )
        @bp.alt_response(
            403,
            {
                "description": "Forbidden",
                "schema": ErrorResponseSchema,
                "content_type": "application/json",
            },
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def with_v2_error_responses(bp):
    """Document the error envelope returned by V2 service errors."""

    def decorator(func):
        wrapped = func
        for status, description in reversed(
            (
                (400, "Bad Request"),
                (403, "Forbidden"),
                (404, "Not Found"),
                (409, "Conflict"),
            )
        ):
            wrapped = bp.alt_response(
                status,
                {
                    "description": description,
                    "schema": V2ErrorSchema,
                    "content_type": "application/json",
                },
            )(wrapped)
        return wraps(func)(wrapped)

    return decorator
