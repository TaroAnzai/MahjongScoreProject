from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import AccessLevel, Group, Tournament
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
# 内部共通関数
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


def _require_group(short_key: str):
    """共有キーからグループを特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("group_keyが無効です。")
    if link.resource_type != "group":
        raise ServicePermissionError("group_keyの対象が一致しません。")

    group = Group.query.get(link.resource_id)
    if not group:
        raise ServiceNotFoundError("グループが見つかりません。")
    return link, group


def _ensure_access(link, required: AccessLevel, message: str):
    """アクセスレベルチェック"""
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


# =========================================================
# サービス関数群
# =========================================================
def create_tournament(data: dict, group_key: str) -> Tournament:
    """グループ共有キーから大会を作成"""
    link, group = _require_group(group_key)
    _ensure_access(link, AccessLevel.EDIT, "大会を作成する権限がありません。")

    name = data.get("name")
    if not name:
        raise ServiceValidationError("大会名は必須です。")

    tournament = Tournament(
        group_id=group.id,
        name=name,
        description=data.get("description"),
        rate=data.get("rate"),
        created_by=group.created_by,
        started_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    db.session.add(tournament)
    db.session.flush()
    create_default_share_links("tournament", tournament.id, tournament.created_by)
    db.session.refresh(tournament)
    tournament.current_user_access =  AccessLevel.OWNER
    return tournament

def get_tournaments_by_group(group_key: str):
    """グループ内の大会一覧を取得"""
    link, group = _require_group(group_key)
    if not group:
        raise ServiceNotFoundError("指定されたグループが見つかりません。")
    _ensure_access(link, AccessLevel.VIEW, "大会を閲覧する権限がありません。")
    tournaments = (
        db.session.query(Tournament)
        .filter(Tournament.group_id == group.id)
        .order_by(Tournament.created_at.desc())
        .all()
    )
    tournaments = [setattr(t, "current_user_access", link.access_level) or t for t in tournaments]
    return tournaments
def get_tournament_by_key(short_key: str) -> Tournament:
    """大会共有キーから大会取得"""
    link, tournament = _require_tournament(short_key)
    tournament.current_user_access = link.access_level
    # ✅ 親グループにも同じアクセス権を適用
    if tournament.group:
        tournament.group.current_user_access = link.access_level
    return tournament


def update_tournament(short_key: str, data: dict) -> Tournament:
    """大会共有キーから大会更新"""
    link, tournament = _require_tournament(short_key)
    _ensure_access(link, AccessLevel.EDIT, "大会を更新する権限がありません。")

    if "name" in data:
        tournament.name = data["name"]
    if "description" in data:
        tournament.description = data["description"]
    if "rate" in data:
        tournament.rate = data["rate"]
    if "started_at" in data:
        tournament.started_at = data["started_at"]

    db.session.commit()
    db.session.refresh(tournament)
    tournament.current_user_access = link.access_level
    return tournament


def delete_tournament(short_key: str) -> None:
    """大会共有キーから大会削除"""
    link, tournament = _require_tournament(short_key)
    _ensure_access(link, AccessLevel.EDIT, "大会を削除する権限がありません。")
    try:
        db.session.delete(tournament)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ServiceValidationError("この大会には関連データが存在するため削除できません。")
