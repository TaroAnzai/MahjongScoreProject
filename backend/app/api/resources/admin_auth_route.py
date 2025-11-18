# app/api/admin_auth_route.py
from flask import  request
from flask_smorest import Blueprint

from app.api.schemas.admin_auth_schema import AdminLoginSchema, AdminMeResponseSchema
from app.api.schemas.common_schemas import MessageSchema
from app.api.services.admin_auth_service import admin_login, admin_logout
from app.utils.auth import require_admin_user
from app.decorators import with_common_error_responses
from app.service_errors import ServiceError, format_error_response
from flask import jsonify
admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/api/admin")

@admin_auth_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code

# --- 管理者ログイン ---
@admin_auth_bp.route("/login", methods=["POST"])
@admin_auth_bp.arguments(AdminLoginSchema)
@admin_auth_bp.response(200, MessageSchema)
@with_common_error_responses(admin_auth_bp)
def login(data):
    result = admin_login(data["username"], data["password"])
    return result


# --- 管理者ログアウト ---
@admin_auth_bp.route("/logout", methods=["POST"])
@require_admin_user
@admin_auth_bp.response(200, MessageSchema)
@with_common_error_responses(admin_auth_bp)
def logout():
    return admin_logout()


# --- 管理者ステータス確認（任意） ---
@admin_auth_bp.route("/me", methods=["GET"])
@admin_auth_bp.response(200, AdminMeResponseSchema)
@with_common_error_responses(admin_auth_bp)
def me():
    return {"is_admin": bool(request.cookies.get("mahjong_session") and request.cookies)}, 200
