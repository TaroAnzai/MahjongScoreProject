# app/utils/share_link_utils.py
from datetime import datetime, timezone
import secrets
from app import db
from app.models import ShareLink, AccessLevel
from app.service_errors import ServiceValidationError


def generate_short_key(length: int = 12) -> str:
    """ランダムな短縮キーを生成"""
    return secrets.token_urlsafe(length)[:length]


def create_unique_share_link(resource_type: str, resource_id: int, created_by: str, access_level: AccessLevel):
    """
    指定されたリソースに対してユニークな共有リンクを作成する。
    同じresource_type / resource_id / access_level の組み合わせが存在すれば再利用する。
    """
    existing = ShareLink.query.filter_by(
        resource_type=resource_type,
        resource_id=resource_id,
        access_level=access_level
    ).first()
    if existing:
        return existing

    for _ in range(5):  # 衝突回避のため最大5回試行
        short_key = generate_short_key(12)
        if not ShareLink.query.filter_by(short_key=short_key).first():
            link = ShareLink(
                short_key=short_key,
                resource_type=resource_type,
                resource_id=resource_id,
                created_by=created_by,
                access_level=access_level,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(link)
            db.session.flush()
            return link

    raise ServiceValidationError("共有リンクの生成に失敗しました。")


def get_share_link_by_key(short_key: str) -> ShareLink | None:
    """short_key から ShareLink を取得"""
    return ShareLink.query.filter_by(short_key=short_key).first()


def create_default_share_links(resource_type: str, resource_id: int, created_by: str) -> dict[str, str]:
    """
    各リソース作成時に共通的に呼び出す関数。
    Groupの場合は OWNER, EDIT, VIEW の3種類、
    その他（Tournament, Table, Game）は EDIT, VIEW の2種類を自動生成。

    戻り値:
        {
            "owner": "...",  # Group のみ
            "edit": "...",
            "view": "..."
        }
    """
    links = {}
    if resource_type == "group":
        levels = [AccessLevel.OWNER, AccessLevel.EDIT, AccessLevel.VIEW]
    else:
        levels = [AccessLevel.EDIT, AccessLevel.VIEW]

    for level in levels:
        link = create_unique_share_link(
            resource_type=resource_type,
            resource_id=resource_id,
            created_by=created_by,
            access_level=level
        )
        links[level.value] = link.short_key

    db.session.commit()
    return links

