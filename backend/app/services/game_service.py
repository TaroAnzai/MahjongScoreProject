from app import db
from app.models import AccessLevel, Game, Table
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.utils.share_link_utils import create_default_share_links, get_share_link_by_key

_ACCESS_PRIORITY = {
    AccessLevel.VIEW: 1,
    AccessLevel.EDIT: 2,
    AccessLevel.OWNER: 3,
}


def _require_link(short_key: str, expected_resource: str):
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != expected_resource:
        raise ServicePermissionError("共有リンクの対象が一致しません。")
    return link


def _require_resource(model, resource_id: int, not_found_message: str):
    resource = model.query.get(resource_id)
    if not resource:
        raise ServiceNotFoundError(not_found_message)
    return resource


def _ensure_access(link_access: AccessLevel, required: AccessLevel, message: str):
    if _ACCESS_PRIORITY[link_access] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


class GameService:
    @staticmethod
    def list_by_table_short_key(short_key: str):
        link = _require_link(short_key, "table")
        table = _require_resource(Table, link.resource_id, "卓が見つかりません。")
        _ensure_access(link.access_level, AccessLevel.VIEW, "対局を閲覧する権限がありません。")
        return Game.query.filter_by(table_id=table.id).all()

    @staticmethod
    def create_game(data: dict, short_key: str) -> Game:
        table_id = data.get("table_id")
        game_index = data.get("game_index")
        if table_id is None or game_index is None:
            raise ServiceValidationError("table_id と game_index は必須です。")

        link = _require_link(short_key, "table")
        table = _require_resource(Table, table_id, "卓が見つかりません。")
        if link.resource_id != table.id:
            raise ServicePermissionError("共有リンクの対象卓が一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "対局を作成する権限がありません。")

        game = Game(
            table_id=table.id,
            game_index=game_index,
            memo=data.get("memo"),
            played_at=data.get("played_at"),
            created_by=table.created_by,
        )
        db.session.add(game)
        db.session.flush()
        create_default_share_links("game", game.id, game.created_by)
        db.session.refresh(game)
        return game

    @staticmethod
    def get_game(game_id: int, short_key: str) -> Game:
        link = _require_link(short_key, "game")
        _ensure_access(link.access_level, AccessLevel.VIEW, "対局を閲覧する権限がありません。")
        if link.resource_id != game_id:
            raise ServicePermissionError("共有リンクがこの対局を指していません。")
        game = _require_resource(Game, game_id, "対局が見つかりません。")
        return game

    @staticmethod
    def update_game(game_id: int, data: dict, short_key: str) -> Game:
        link = _require_link(short_key, "game")
        _ensure_access(link.access_level, AccessLevel.EDIT, "対局を更新する権限がありません。")
        if link.resource_id != game_id:
            raise ServicePermissionError("共有リンクがこの対局を指していません。")

        game = _require_resource(Game, game_id, "対局が見つかりません。")

        if "game_index" in data:
            game.game_index = data["game_index"]
        if "memo" in data:
            game.memo = data["memo"]
        if "played_at" in data:
            game.played_at = data["played_at"]

        db.session.commit()
        db.session.refresh(game)
        return game

    @staticmethod
    def delete_game(game_id: int, short_key: str) -> None:
        game = _require_resource(Game, game_id, "対局が見つかりません。")
        table = _require_resource(Table, game.table_id, "卓が見つかりません。")
        link = _require_link(short_key, "table")
        if link.resource_id != table.id:
            raise ServicePermissionError("共有リンクの対象卓が一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "対局を削除する権限がありません。")

        db.session.delete(game)
        db.session.commit()
