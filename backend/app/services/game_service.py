from datetime import datetime, timezone
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


# =========================================================
# 内部ユーティリティ
# =========================================================
def _require_table(short_key: str):
    """共有キーから卓を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("table_keyが無効です。")
    if link.resource_type != "table":
        raise ServicePermissionError("table_keyの対象が一致しません。")

    table = Table.query.get(link.resource_id)
    if not table:
        raise ServiceNotFoundError("卓が見つかりません。")
    return link, table


def _require_game(short_key: str):
    """共有キーから対局を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("game_keyが無効です。")
    if link.resource_type != "game":
        raise ServicePermissionError("game_keyの対象が一致しません。")

    game = Game.query.get(link.resource_id)
    if not game:
        raise ServiceNotFoundError("対局が見つかりません。")
    return link, game


def _ensure_access(link, required: AccessLevel, message: str):
    """アクセスレベルチェック"""
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


# =========================================================
# サービス関数群
# =========================================================
def create_game(data: dict, table_key: str) -> Game:
    """卓共有キーから対局を作成"""
    link, table = _require_table(table_key)
    _ensure_access(link, AccessLevel.EDIT, "対局を作成する権限がありません。")

    game_index = data.get("game_index")
    if game_index is None:
        raise ServiceValidationError("game_index は必須です。")

    game = Game(
        table_id=table.id,
        game_index=game_index,
        memo=data.get("memo"),
        played_at=data.get("played_at"),
        created_by=table.created_by,
        created_at=datetime.now(timezone.utc),
    )

    db.session.add(game)
    db.session.flush()
    create_default_share_links("game", game.id, game.created_by)
    db.session.refresh(game)
    return game

def get_games_by_table(table_key: str):
    """卓共有キーから対局一覧を取得"""
    link, table = _require_table(table_key)
    _ensure_access(link, AccessLevel.VIEW, "対局を閲覧する権限がありません。")

    games = Game.query.filter_by(table_id=table.id).order_by(Game.game_index.asc()).all()
    return games
def get_game_by_key(short_key: str) -> Game:
    """対局共有キーから取得"""
    _, game = _require_game(short_key)
    return game


def update_game(short_key: str, data: dict) -> Game:
    """対局共有キーから更新"""
    link, game = _require_game(short_key)
    _ensure_access(link, AccessLevel.EDIT, "対局を更新する権限がありません。")

    if "game_index" in data:
        game.game_index = data["game_index"]
    if "memo" in data:
        game.memo = data["memo"]
    if "played_at" in data:
        game.played_at = data["played_at"]

    db.session.commit()
    db.session.refresh(game)
    return game


def delete_game(short_key: str) -> None:
    """対局共有キーから削除"""
    link, game = _require_game(short_key)
    _ensure_access(link, AccessLevel.EDIT, "対局を削除する権限がありません。")

    db.session.delete(game)
    db.session.commit()
