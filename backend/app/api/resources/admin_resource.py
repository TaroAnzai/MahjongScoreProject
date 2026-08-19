from flask import jsonify
from flask_smorest import Blueprint

from app.api.schemas.admin_schemas import AdminGroupSchema
from app.api.schemas.contact_schemas import (
    ContactSchema,
    ContactUpdateSchema,
)
from app.api.services.admin_service import delete_group_service, get_all_groups_service
from app.api.services.contact_service import ContactService
from app.decorators import with_common_error_responses
from app.service_errors import ServiceError, format_error_response
from app.utils.auth import require_admin_user

admin_group_bp = Blueprint("admin_resources", __name__, url_prefix="/api/admin")


@admin_group_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code


# -------------------------------------------------
# 1. すべてのグループを取得
# -------------------------------------------------
@admin_group_bp.get("/groups")
@require_admin_user
@admin_group_bp.response(200, AdminGroupSchema(many=True))
@with_common_error_responses(admin_group_bp)
def get_all_groups():
    """すべてのグループを取得"""
    return get_all_groups_service()


# -------------------------------------------------
# 2. 指定したグループを削除
# -------------------------------------------------
@admin_group_bp.delete("/groups/<string:group_key>")
@require_admin_user
@with_common_error_responses(admin_group_bp)
def delete_group(group_key):
    """指定したグループを削除"""
    return delete_group_service(group_key)


# --------------------------
# LIST: GET /contacts
# --------------------------
@admin_group_bp.route("/contacts", methods=["GET"])
@require_admin_user
@admin_group_bp.response(200, ContactSchema(many=True))
@with_common_error_responses(admin_group_bp)
def list_contacts():
    return ContactService.list_contacts()


# --------------------------
# GET ONE: GET /contacts/<id>
# --------------------------
@admin_group_bp.route("/contacts/<int:contact_id>", methods=["GET"])
@require_admin_user
@admin_group_bp.response(200, ContactSchema)
@require_admin_user
@with_common_error_responses(admin_group_bp)
def get_contact(contact_id):
    contact = ContactService.get_contact(contact_id)
    return contact


# --------------------------
# UPDATE (PATCH): /contacts/<id>
# --------------------------
@admin_group_bp.route("/contacts/<int:contact_id>", methods=["PATCH"])
@admin_group_bp.arguments(ContactUpdateSchema)
@require_admin_user
@admin_group_bp.response(200, ContactSchema)
@with_common_error_responses(admin_group_bp)
def update_contact(data, contact_id):
    contact = ContactService.update_contact(contact_id, data)
    return contact


# --------------------------
# DELETE /contacts/<id>
# --------------------------
@admin_group_bp.route("/contacts/<int:contact_id>", methods=["DELETE"])
@require_admin_user
@admin_group_bp.response(204)
def delete_contact(contact_id):
    ContactService.delete_contact(contact_id)
    return ""
