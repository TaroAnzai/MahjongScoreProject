# app/decorators/require_admin_user.py
from functools import wraps
from flask import session
from app.service_errors import ServicePermissionError


def require_admin_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            raise ServicePermissionError("管理者ログインが必要です")
        return f(*args, **kwargs)
    return decorated

