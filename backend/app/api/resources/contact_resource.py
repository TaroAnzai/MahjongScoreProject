# backend/app/api/resources/contact_resource.py

from flask import request, jsonify
from flask_smorest import Blueprint, abort

from app.api.schemas.contact_schemas import (
    ContactCreateSchema,
    ContactUpdateSchema,
    ContactSchema,
)
from app.api.schemas.common_schemas import MessageSchema
from app.api.services.contact_service import ContactService
from app.decorators import with_common_error_responses
from app.service_errors import ServiceError, format_error_response

contact_bp = Blueprint(
    "contacts",
    __name__,
    url_prefix="/api/contacts",
    description="問い合わせ（Contact）関連 API",
)
@contact_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code

# --------------------------
# CREATE: POST /contacts
# --------------------------
@contact_bp.route("/", methods=["POST"])
@contact_bp.arguments(ContactCreateSchema)
@contact_bp.response(201, ContactSchema)
@with_common_error_responses(contact_bp)
def create_contact(data):
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    contact = ContactService.create_contact(
        data,
        ip_address=ip,
        user_agent=user_agent,
    )
    return contact


# --------------------------
# LIST: GET /contacts
# --------------------------
@contact_bp.route("/", methods=["GET"])
@contact_bp.response(200, ContactSchema(many=True))
@with_common_error_responses(contact_bp)
def list_contacts():
    return ContactService.list_contacts()


# --------------------------
# GET ONE: GET /contacts/<id>
# --------------------------
@contact_bp.route("/<int:contact_id>", methods=["GET"])
@contact_bp.response(200, ContactSchema)
@with_common_error_responses(contact_bp)
def get_contact(contact_id):
    contact = ContactService.get_contact(contact_id)
    if not contact:
        abort(404, message="Contact not found")
    return contact


# --------------------------
# UPDATE (PATCH): /contacts/<id>
# --------------------------
@contact_bp.route("/<int:contact_id>", methods=["PATCH"])
@contact_bp.arguments(ContactUpdateSchema)
@contact_bp.response(200, ContactSchema)
@with_common_error_responses(contact_bp)
def update_contact(data, contact_id):
    contact = ContactService.update_contact(contact_id, data)
    if not contact:
        abort(404, message="Contact not found")
    return contact


# --------------------------
# DELETE /contacts/<id>
# --------------------------
@contact_bp.route("/<int:contact_id>", methods=["DELETE"])
@contact_bp.response(204, MessageSchema)
def delete_contact(contact_id):
    success = ContactService.delete_contact(contact_id)
    if not success:
        abort(404, message="Contact not found")
    return {"message": "Contact deleted"}
