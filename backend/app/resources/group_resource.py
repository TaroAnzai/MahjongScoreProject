# app/resources/group_resource.py
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import jsonify
from flask_login import login_required
from app.schemas.group_schema import GroupSchema, GroupCreateSchema, GroupUpdateSchema
from app.services.group_service import (
    get_all_groups,
    get_group,
    create_group,
    update_group,
    delete_group,
)

group_bp = Blueprint("Groups", __name__, url_prefix="/api/groups", description="Group operations")


@group_bp.route("/")
class GroupsResource(MethodView):
    @group_bp.response(200, GroupSchema(many=True))
    @login_required
    def get(self):
        """Get all groups"""
        return get_all_groups()

    @group_bp.arguments(GroupCreateSchema)
    @group_bp.response(201, GroupSchema)
    def post(self, new_data):
        """Create a new group"""
        return create_group(new_data)


@group_bp.route("/<int:group_id>")
class GroupResource(MethodView):
    @group_bp.response(200, GroupSchema)
    def get(self, group_id):
        """Get a single group by ID"""
        return get_group(group_id)

    @group_bp.arguments(GroupUpdateSchema)
    @group_bp.response(200, GroupSchema)
    def put(self, update_data, group_id):
        """Update a group"""
        return update_group(group_id, update_data)

    def delete(self, group_id):
        """Delete a group"""
        delete_group(group_id)
        return jsonify({"message": "Group deleted"}), 200
