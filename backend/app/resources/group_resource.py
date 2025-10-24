from flask.views import MethodView
from flask_smorest import Blueprint, abort

from app.decorators import with_common_error_responses
from app.schemas.common_schemas import MessageSchema
from app.schemas.group_schema import (
    GroupCreateSchema,
    GroupUpdateSchema,
    GroupSchema,
)
from app.schemas.tournament_schema import TournamentSchema, TournamentCreateSchema
from app.service_errors import ServiceError
from flask import jsonify
from app.service_errors import format_error_response

from app.services.group_service import (
    create_group,
    get_group_by_key,
    update_group,
    delete_group,
)
from app.services.tournament_service import create_tournament, get_tournaments_by_group


# ✅ Blueprint設定（命名を仕様準拠に統一）
group_bp = Blueprint(
    "groups",
    __name__,
    url_prefix="/api/groups",
    description="グループ管理API",
)
@group_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code

# =========================================================
# 作成
# =========================================================
@group_bp.route("")
class GroupsResource(MethodView):
    """POST: 新規作成"""
    @group_bp.arguments(GroupCreateSchema)
    @group_bp.response(201, GroupSchema)
    @with_common_error_responses(group_bp)
    def post(self, new_data):
        """グループ新規作成"""
        return create_group(new_data)



# =========================================================
# グループ単体操作
# =========================================================
@group_bp.route("/<string:group_key>")
class GroupByKeyResource(MethodView):
    """GET / PUT / DELETE: グループ単体操作"""

    @group_bp.response(200, GroupSchema)
    @with_common_error_responses(group_bp)
    def get(self, group_key):
        """グループ詳細取得"""
        return get_group_by_key(group_key)


    @group_bp.arguments(GroupUpdateSchema)
    @group_bp.response(200, GroupSchema)
    @with_common_error_responses(group_bp)
    def put(self, update_data, group_key):
        """グループ更新"""
        return update_group(group_key, update_data)


    @group_bp.response(200, MessageSchema)
    @with_common_error_responses(group_bp)
    def delete(self, group_key):
        """グループ削除"""
        delete_group(group_key)
        return {"message": "Group deleted"}


# =========================================================
# 大会作成
# =========================================================
@group_bp.route("/<string:group_key>/tournaments")
class TournamentCreateResource(MethodView):
    """GET: グループ内大会一覧 / POST: 指定グループに大会作成"""

    @group_bp.arguments(TournamentCreateSchema)
    @group_bp.response(201, TournamentSchema)
    @with_common_error_responses(group_bp)
    def post(self, new_data, group_key):
        """グループ共有キーから大会を作成"""
        return create_tournament(new_data, group_key)


    @group_bp.response(200, TournamentSchema(many=True))
    @with_common_error_responses(group_bp)
    def get(self, group_key):
        """グループキーから大会一覧を取得"""
        return get_tournaments_by_group(group_key)

