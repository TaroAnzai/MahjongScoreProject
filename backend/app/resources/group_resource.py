from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.group_schema import (
    GroupCreateSchema,
    GroupQuerySchema,
    GroupSchema,
    GroupUpdateSchema,
)
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.group_service import (
    create_group,
    delete_group,
    get_group_by_short_key,
    update_group,
)


group_bp = Blueprint(
    "Groups",
    __name__,
    url_prefix="/api/groups",
    description="Group operations",
)


@group_bp.route("")
class GroupsResource(MethodView):
    @group_bp.arguments(GroupCreateSchema)
    @group_bp.response(201, GroupSchema)
    @with_common_error_responses(group_bp)
    def post(self, new_data):
        try:
            return create_group(new_data)
        except (ServiceValidationError,) as e:
            abort(e.status_code, message=e.message)


@group_bp.route("/<string:short_key>")
class GroupByKeyResource(MethodView):
    @group_bp.response(200, GroupSchema)
    @with_common_error_responses(group_bp)
    def get(self, short_key):
        try:
            return get_group_by_short_key(short_key)
        except (ServiceNotFoundError,) as e:
            abort(e.status_code, message=e.message)


@group_bp.route("/<int:group_id>")
class GroupResource(MethodView):
    @group_bp.arguments(GroupQuerySchema, location="query")
    @group_bp.arguments(GroupUpdateSchema)
    @group_bp.response(200, GroupSchema)
    @with_common_error_responses(group_bp)
    def put(self, query_args, update_data, group_id):
        short_key = query_args["short_key"]
        try:
            return update_group(group_id, update_data, short_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @group_bp.arguments(GroupQuerySchema, location="query")
    @group_bp.response(200, MessageSchema)
    @with_common_error_responses(group_bp)
    def delete(self, query_args, group_id):
        short_key = query_args["short_key"]
        try:
            delete_group(group_id, short_key)
            return {"message": "Group deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
