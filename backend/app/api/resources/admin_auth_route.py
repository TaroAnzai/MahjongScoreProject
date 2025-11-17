# app/api/admin_auth_route.py
from flask import  request
from flask_smorest import Blueprint
from marshmallow import ValidationError

from app.api.schemas.admin_auth_schema import AdminLoginSchema
from app.api.services.admin_auth_service import admin_login, admin_logout, AdminAuthError
from app.utils.auth import require_admin_user

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/admin")


# --- 管理者ログイン ---
@admin_auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = AdminLoginSchema().load(request.get_json() or {})
        result = admin_login(data["username"], data["password"])
        return result, 200

    except ValidationError as e:
        return {"error": e.normalized_messages()}, 400

    except AdminAuthError as e:
        return {"error": str(e)}, 401


# --- 管理者ログアウト ---
@admin_auth_bp.route("/logout", methods=["POST"])
@require_admin_user
def logout():
    return admin_logout(), 200


# --- 管理者ステータス確認（任意） ---
@admin_auth_bp.route("/me", methods=["GET"])
def me():
    print("cookies:", request.cookies, "session:", request.cookies.get("mahjong_session"))
    return {"is_admin": bool(request.cookies.get("mahjong_session") and request.cookies)}, 200
