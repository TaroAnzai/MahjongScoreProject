"""
share_link_utils.py

短縮キー方式による共有リンク生成およびアクセス制御の共通関数群。
JWTを使用せず、DB上のShareLinkテーブルを基準に安全にアクセス制御を行う。
"""

import secrets
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import ShareLink, Group, Tournament, Table, Game
from typing import Optional

# =========================================================
# 短縮キー生成
# =========================================================
def generate_short_key(length: int = 10) -> str:
    """
    ランダムな英数字の短縮キーを生成する（URL共有用）。
    例: 'A9ZB23KDQP'
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# =========================================================
# 共有リンクの一意生成
# =========================================================
def create_unique_share_link(
    resource_type: str,
    resource_id: int,
    created_by: str,
    access_level: str = "VIEW",
    max_retries: int = 5,
) -> ShareLink:
    """
    一意な short_key を持つ ShareLink を生成して DB に保存する。
    万一重複した場合は再生成を試行する。

    Args:
        resource_type: "group" | "tournament" | "table" | "game"
        resource_id: リソースID
        created_by: 作成者UUID（Group作成者）
        access_level: "VIEW" | "EDIT" | "OWNER"
        max_retries: 衝突時の再試行回数
    """
    for _ in range(max_retries):
        short_key = generate_short_key()
        link = ShareLink(
            short_key=short_key,
            resource_type=resource_type,
            resource_id=resource_id,
            access_level=access_level,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(link)
        try:
            db.session.commit()
            return link
        except IntegrityError:
            db.session.rollback()
            continue
    raise RuntimeError("Failed to generate unique short_key after several attempts")


# =========================================================
# アクセス制御
# =========================================================
def can_create_child(link: ShareLink, parent_type: str, parent_id: int) -> bool:
    """
    共有リンク保持者が子リソースを作成できるか判定する。
    例: グループ共有者が大会を追加できるか
    """
    if link.access_level not in ["EDIT", "OWNER"]:
        return False

    # グループのリンク → グループ配下すべて作成可能
    if link.resource_type == "group" and parent_type == "group" and link.resource_id == parent_id:
        return True
    if link.resource_type == "group" and parent_type == "tournament":
        tournament = Tournament.query.get(parent_id)
        if not tournament: return False
        group = tournament.group_id
        return link.resource_id == group

    # 大会のリンク → その大会配下（Table, Game）作成可能
    if link.resource_type == "tournament" and parent_type in ["tournament", "table"]:
        if parent_type == "table":
            table = Table.query.get(parent_id)
            if not table:
                return False
            return table.tournament_id == link.resource_id
        return link.resource_id == parent_id

    # テーブルリンク → そのテーブル配下のGame作成可能
    if link.resource_type == "table" and parent_type == "table":
        return link.resource_id == parent_id

    return False


def can_edit_or_delete(resource, link: ShareLink) -> bool:
    """
    対象リソースを編集・削除できるか判定。
    - 自身が作成したもの or 上位オーナーであればTrue。
    """
    if link.access_level == "OWNER":
        return True

    # 作成者一致チェック
    if hasattr(resource, "created_by") and resource.created_by == link.created_by:
        return True

    # 上位階層のオーナー判定
    if isinstance(resource, Tournament):
        return resource.group.created_by == link.created_by
    elif isinstance(resource, Table):
        return resource.tournament.group.created_by == link.created_by
    elif isinstance(resource, Game):
        return resource.table.tournament.group.created_by == link.created_by

    return False


def get_share_link_by_key(short_key: str) -> Optional[ShareLink]:
    """
    短縮キーから ShareLink を取得。
    """
    return ShareLink.query.filter_by(short_key=short_key).first()
