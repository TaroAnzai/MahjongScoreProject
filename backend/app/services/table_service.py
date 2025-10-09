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


class TableService:
    @staticmethod
    def list_by_tournament_short_key(short_key: str):
        link = _require_link(short_key, "tournament")
        tournament = _require_resource(Tournament, link.resource_id, "大会が見つかりません。")
        _ensure_access(link.access_level, AccessLevel.VIEW, "卓を閲覧する権限がありません。")
        return Table.query.filter_by(tournament_id=tournament.id).all()

    @staticmethod
    def create_table(data: dict, short_key: str) -> Table:
        tournament_id = data.get("tournament_id")
        name = data.get("name")
        if not tournament_id or not name:
            raise ServiceValidationError("tournament_id と name は必須です。")

        link = _require_link(short_key, "tournament")
        tournament = _require_resource(Tournament, tournament_id, "大会が見つかりません。")
        if link.resource_id != tournament.id:
            raise ServicePermissionError("共有リンクの対象大会が一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "卓を作成する権限がありません。")

        table = Table(
            tournament_id=tournament.id,
            name=name,
            type=data.get("type", "normal"),
            created_by=tournament.created_by,
        )
        db.session.add(table)
        db.session.flush()
        create_default_share_links("table", table.id, table.created_by)
        db.session.refresh(table)
        return table

    @staticmethod
    def get_table(table_id: int, short_key: str) -> Table:
        link = _require_link(short_key, "table")
        _ensure_access(link.access_level, AccessLevel.VIEW, "卓を閲覧する権限がありません。")
        if link.resource_id != table_id:
            raise ServicePermissionError("共有リンクがこの卓を指していません。")
        table = _require_resource(Table, table_id, "卓が見つかりません。")
        return table

    @staticmethod
    def update_table(table_id: int, data: dict, short_key: str) -> Table:
        link = _require_link(short_key, "table")
        _ensure_access(link.access_level, AccessLevel.EDIT, "卓を更新する権限がありません。")
        if link.resource_id != table_id:
            raise ServicePermissionError("共有リンクがこの卓を指していません。")

        table = _require_resource(Table, table_id, "卓が見つかりません。")

        if "name" in data:
            table.name = data["name"]
        if "type" in data:
            table.type = data["type"]

        db.session.commit()
        db.session.refresh(table)
        return table

    @staticmethod
    def delete_table(table_id: int, short_key: str) -> None:
        table = _require_resource(Table, table_id, "卓が見つかりません。")
        link = _require_link(short_key, "tournament")
        if link.resource_id != table.tournament_id:
            raise ServicePermissionError("共有リンクの対象大会が一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "卓を削除する権限がありません。")

        db.session.delete(table)
        db.session.commit()
