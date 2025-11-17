from flask_smorest import Blueprint
from flask import jsonify
from app.service_errors import ServiceError,format_error_response
from app.utils.auth import require_admin_user
from app.decorators import with_common_error_responses
from app.api.services.admin_service import get_all_groups_service, delete_group_service
from app.api.schemas.admin_schemas import AdminGroupSchema

admin_group_bp = Blueprint("admin_groups", __name__, url_prefix="/api/admin/groups")
@admin_group_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code

# -------------------------------------------------
# 1. すべてのグループを取得
# -------------------------------------------------
@admin_group_bp.get("")
@require_admin_user
@admin_group_bp.response(200, AdminGroupSchema (many=True))
@with_common_error_responses(admin_group_bp)
def get_all_groups():
    """すべてのグループを取得"""
    return get_all_groups_service()


# -------------------------------------------------
# 2. 指定したグループを削除
# -------------------------------------------------
@admin_group_bp.delete("/<string:group_key>")
@require_admin_user
@with_common_error_responses(admin_group_bp)
def delete_group(group_key):
    """指定したグループを削除"""
    return delete_group_service(group_key)
