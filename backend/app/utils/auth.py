import os
from functools import wraps
from flask import request, jsonify
from app.service_errors import ServicePermissionError, ServiceValidationError

def require_admin_key(f):
    """管理者キーによる簡易認証"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_key = request.headers.get("X-Admin-Key")
        expected_key = os.getenv("ADMIN_SECRET_KEY")
        if not expected_key:
            raise ServicePermissionError("サーバー設定に ADMIN_SECRET_KEY がありません。")

        if admin_key != expected_key:
            raise ServicePermissionError("管理者キーが無効です。")

        return f(*args, **kwargs)
    return decorated_function
