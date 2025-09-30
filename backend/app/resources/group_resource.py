# app/resources/group_resource.py
from flask_smorest import Blueprint, abort
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

blp = Blueprint("Groups", __name__, url_prefix="/api/groups", description="Group operations")


@blp.route("/")
class GroupsResource:
    @blp.response(200, GroupSchema(many=True))
    @login_required
    def get(self):
        """Get all groups"""
        return get_all_groups()

    @blp.arguments(GroupCreateSchema)
    @blp.response(201, GroupSchema)
    def post(self, new_data):
        """Create a new group"""
        return create_group(new_data)


@blp.route("/<int:group_id>")
class GroupResource:
    @blp.response(200, GroupSchema)
    def get(self, group_id):
        """Get a single group by ID"""
        return get_group(group_id)

    @blp.arguments(GroupUpdateSchema)
    @blp.response(200, GroupSchema)
    def put(self, update_data, group_id):
        """Update a group"""
        return update_group(group_id, update_data)

    def delete(self, group_id):
        """Delete a group"""
        delete_group(group_id)
        return jsonify({"message": "Group deleted"}), 200
