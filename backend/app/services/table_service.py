from datetime import datetime, timezone
from app import db
from app.models import AccessLevel, Table, Tournament
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
def _require_tournament(short_key: str):
    """共有キーから大会を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "tournament":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    tournament = Tournament.query.get(link.resource_id)
    if not tournament:
        raise ServiceNotFoundError("大会が見つかりません。")
    return link, tournament


def _require_table(short_key: str):
    """共有キーから卓を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "table":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    table = Table.query.get(link.resource_id)
    if not table:
        raise ServiceNotFoundError("卓が見つかりません。")
    return link, table


def _ensure_access(link, required: AccessLevel, message: str):
    """アクセスレベルチェック"""
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


# =========================================================
# 卓作成
# =========================================================
def create_table(data: dict, tournament_key: str) -> Table:
    """大会共有キーから卓を作成"""
    link, tournament = _require_tournament(tournament_key)
    _ensure_access(link, AccessLevel.EDIT, "卓を作成する権限がありません。")

    name = data.get("name")
    if not name:
        raise ServiceValidationError("卓名は必須です。")

    table = Table(
        tournament_id=tournament.id,
        name=name,
        type=data.get("type", "normal"),
        created_by=tournament.created_by,
        created_at=datetime.now(timezone.utc),
    )

    db.session.add(table)
    db.session.flush()
    create_default_share_links("table", table.id, table.created_by)
    db.session.refresh(table)
    return table


# =========================================================
# 卓取得
# =========================================================
def get_table_by_key(short_key: str) -> Table:
    """卓共有キーから卓を取得"""
    _, table = _require_table(short_key)
    return table


# =========================================================
# 卓更新
# =========================================================
def update_table(short_key: str, data: dict) -> Table:
    """卓共有キーから卓を更新"""
    link, table = _require_table(short_key)
    _ensure_access(link, AccessLevel.EDIT, "卓を更新する権限がありません。")

    if "name" in data:
        table.name = data["name"]
    if "type" in data:
        table.type = data["type"]

    db.session.commit()
    db.session.refresh(table)
    return table


# =========================================================
# 卓削除
# =========================================================
def delete_table(short_key: str) -> None:
    """卓共有キーから卓を削除"""
    link, table = _require_table(short_key)
    _ensure_access(link, AccessLevel.OWNER, "卓を削除する権限がありません。")

    db.session.delete(table)
    db.session.commit()
