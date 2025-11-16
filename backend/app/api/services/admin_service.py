from flask import jsonify
from flask_smorest import abort
from app.extensions import db
from app.models import (
    Group,
    Tournament,
    TournamentPlayer,
    Table,
    Player,
    TablePlayer,
    AccessLevel,
    Game,
    ShareLink,
    Score,
    )
from app.utils.share_link_utils import get_share_link_by_key
from app.service_errors import ServiceNotFoundError,ServicePermissionError

# =========================================================
# 内部ユーティリティ
# =========================================================
_ACCESS_PRIORITY = {
    AccessLevel.VIEW: 1,
    AccessLevel.EDIT: 2,
    AccessLevel.OWNER: 3,
}

def _require_group(short_key: str):
    """共有リンクからGroupを特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("共有リンクが無効です。")
    if link.resource_type != "group":
        raise ServicePermissionError("共有リンクの対象が一致しません。")

    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")
    return link, group

def _ensure_access(link, group, required: AccessLevel, message: str):
    """アクセスレベルチェック"""
    if link.resource_id != group.id:
        raise ServicePermissionError("共有リンクの対象が一致しません。")
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)
# -------------------------------------------------
# すべてのグループ取得
# -------------------------------------------------
def get_all_groups_service():
    """すべてのグループデータを取得"""
    groups = Group.query.all()

    return groups


# -------------------------------------------------
# グループ削除
# -------------------------------------------------
def delete_group_service(group_key: str):
    """共有リンクキーからGroupを特定して更新"""
    link, group = _require_group(group_key)
    _ensure_access(link, group, AccessLevel.OWNER, "グループの更新にはOWNER権限が必要です。")

    # --- 関連データ削除（順序に注意） ---
    # --- Tournament階層 ---
    tournaments = Tournament.query.filter_by(group_id=group.id).all()
    for tournament in tournaments:
        tables = Table.query.filter_by(tournament_id=tournament.id).all()
        for table in tables:
            # --- Game階層 ---
            games = Game.query.filter_by(table_id=table.id).all()
            for game in games:
                db.session.delete(game)  # Scoreはcascadeで削除される

            db.session.delete(table)  # TablePlayerはcascadeで削除される

        db.session.delete(tournament)  # TournamentPlayerはcascadeで削除される

    # --- Player削除（cascadeで自動） ---

    # --- ShareLink削除（論理参照） ---
    ShareLink.query.filter_by(resource_type="group", resource_id=group.id).delete(
        synchronize_session=False
    )

    db.session.delete(group)
    db.session.commit()

    return {"message": f"グループ '{group.name}' を削除しました。"}
