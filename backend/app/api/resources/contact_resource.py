# backend/app/api/resources/contact_resource.py

from flask import jsonify, request
from flask_smorest import Blueprint

from app.api.schemas.contact_schemas import (
    ContactCreateSchema,
    ContactSchema,
)
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
