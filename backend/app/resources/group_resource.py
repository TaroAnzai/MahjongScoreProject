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
from app.schemas.player_schema import PlayerSchema, PlayerCreateSchema
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.services.group_service import (
    create_group,
    get_group_by_key,
    update_group,
    delete_group,
)
from app.services.tournament_service import create_tournament
from app.services.player_service import create_player, list_players_by_group_key

# ✅ Blueprint設定（命名を仕様準拠に統一）
group_bp = Blueprint(
    "groups",
    __name__,
    url_prefix="/api/groups",
    description="グループ管理API",
)


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
        try:
            return create_group(new_data)
        except ServiceValidationError as e:
            abort(e.status_code, message=e.message)


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
        try:
            return get_group_by_key(group_key)
        except ServiceNotFoundError as e:
            abort(e.status_code, message=e.message)

    @group_bp.arguments(GroupUpdateSchema)
    @group_bp.response(200, GroupSchema)
    @with_common_error_responses(group_bp)
    def put(self, update_data, group_key):
        """グループ更新"""
        try:
            return update_group(group_key, update_data)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @group_bp.response(200, MessageSchema)
    @with_common_error_responses(group_bp)
    def delete(self, group_key):
        """グループ削除"""
        try:
            delete_group(group_key)
            return {"message": "Group deleted"}
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

# =========================================================
# 大会作成
# =========================================================
@group_bp.route("/<string:group_key>/tournaments")
class TournamentCreateResource(MethodView):
    """POST: 指定グループ内に大会作成"""

    @group_bp.arguments(TournamentCreateSchema)
    @group_bp.response(201, TournamentSchema)
    @with_common_error_responses(group_bp)
    def post(self, new_data, group_key):
        """グループ共有キーから大会を作成"""
        try:
            return create_tournament(new_data, group_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

# =========================================================
# プレイヤー一覧・作成
# =========================================================
@group_bp.route("/<string:group_key>/players")
class PlayerListResource(MethodView):
    """GET: プレイヤー一覧 / POST: プレイヤー作成"""

    @group_bp.response(200, PlayerSchema(many=True))
    @with_common_error_responses(group_bp)
    def get(self, group_key):
        """グループ共有キーからプレイヤー一覧を取得"""
        try:
            return list_players_by_group_key(group_key)
        except (ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)

    @group_bp.arguments(PlayerCreateSchema)
    @group_bp.response(201, PlayerSchema)
    @with_common_error_responses(group_bp)
    def post(self, new_data, group_key):
        """グループ共有キーからプレイヤー作成"""
        try:
            return create_player(new_data, group_key)
        except (ServiceValidationError, ServicePermissionError, ServiceNotFoundError) as e:
            abort(e.status_code, message=e.message)
