# app/resources/group_resource.py
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request, jsonify
from app.schemas.group_schema import GroupSchema, GroupCreateSchema, GroupUpdateSchema
from app.services.group_service import (
    get_group_by_short_key,
    create_group,
    update_group,
    delete_group,
)
from app.service_errors import (
    ServicePermissionError,
    ServiceValidationError,
    ServiceNotFoundError,
)

group_bp = Blueprint("Groups", __name__, url_prefix="/api/groups", description="Group operations")


@group_bp.route("")
class GroupsResource(MethodView):
    @group_bp.arguments(GroupCreateSchema)
    @group_bp.response(201, GroupSchema)
    def post(self, new_data):
        """Create a new group"""
        try:
            group = create_group(new_data)
            return group
        except ServiceValidationError as e:
            abort(400, message=e.message)


@group_bp.route("/<string:short_key>")
class GroupByKeyResource(MethodView):
    @group_bp.response(200, GroupSchema)
    def get(self, short_key):
        """Get a group by its short key"""
        try:
            group = get_group_by_short_key(short_key)
            return group
        except ServiceNotFoundError as e:
            abort(404, message=e.message)


@group_bp.route("/<int:group_id>")
class GroupResource(MethodView):
    @group_bp.arguments(GroupUpdateSchema)
    @group_bp.response(200, GroupSchema)
    def put(self, update_data, group_id):
        """Update a group (OWNER link required)"""
        short_key = request.args.get("short_key")
        if not short_key:
            abort(400, message="short_key is required")
        try:
            group = update_group(group_id, update_data, short_key)
            return group
        except ServicePermissionError as e:
            abort(403, message=e.message)
        except ServiceNotFoundError as e:
            abort(404, message=e.message)

    def delete(self, group_id):
        """Delete a group (OWNER link required)"""
        short_key = request.args.get("short_key")
        if not short_key:
            abort(400, message="short_key is required")
        try:
            delete_group(group_id, short_key)
            return jsonify({"message": "Group deleted"}), 200
        except ServicePermissionError as e:
            abort(403, message=e.message)
        except ServiceNotFoundError as e:
            abort(404, message=e.message)
