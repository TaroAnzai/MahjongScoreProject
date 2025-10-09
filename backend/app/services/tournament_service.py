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


class TournamentService:
    @staticmethod
    def list_by_group_short_key(short_key: str):
        link = _require_link(short_key, "group")
        group = _require_resource(Group, link.resource_id, "グループが見つかりません。")
        _ensure_access(link.access_level, AccessLevel.VIEW, "大会を閲覧する権限がありません。")
        return Tournament.query.filter_by(group_id=group.id).all()

    @staticmethod
    def create_tournament(data: dict, short_key: str) -> Tournament:
        group_id = data.get("group_id")
        name = data.get("name")
        if not group_id or not name:
            raise ServiceValidationError("group_id と name は必須です。")

        link = _require_link(short_key, "group")
        group = _require_resource(Group, group_id, "グループが見つかりません。")
        if link.resource_id != group.id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "大会を作成する権限がありません。")

        tournament = Tournament(
            group_id=group.id,
            name=name,
            description=data.get("description"),
            rate=data.get("rate"),
            created_by=group.created_by,
        )
        db.session.add(tournament)
        db.session.flush()
        create_default_share_links("tournament", tournament.id, tournament.created_by)
        db.session.refresh(tournament)
        return tournament

    @staticmethod
    def get_tournament(tournament_id: int, short_key: str) -> Tournament:
        link = _require_link(short_key, "tournament")
        _ensure_access(link.access_level, AccessLevel.VIEW, "大会を閲覧する権限がありません。")
        if link.resource_id != tournament_id:
            raise ServicePermissionError("共有リンクがこの大会を指していません。")
        tournament = _require_resource(Tournament, tournament_id, "大会が見つかりません。")
        return tournament

    @staticmethod
    def update_tournament(tournament_id: int, data: dict, short_key: str) -> Tournament:
        link = _require_link(short_key, "tournament")
        _ensure_access(link.access_level, AccessLevel.EDIT, "大会を更新する権限がありません。")
        if link.resource_id != tournament_id:
            raise ServicePermissionError("共有リンクがこの大会を指していません。")

        tournament = _require_resource(Tournament, tournament_id, "大会が見つかりません。")

        if "name" in data:
            tournament.name = data["name"]
        if "description" in data:
            tournament.description = data["description"]
        if "rate" in data:
            tournament.rate = data["rate"]

        db.session.commit()
        db.session.refresh(tournament)
        return tournament

    @staticmethod
    def delete_tournament(tournament_id: int, short_key: str) -> None:
        tournament = _require_resource(Tournament, tournament_id, "大会が見つかりません。")
        link = _require_link(short_key, "group")
        if link.resource_id != tournament.group_id:
            raise ServicePermissionError("共有リンクの対象グループが一致しません。")
        _ensure_access(link.access_level, AccessLevel.EDIT, "大会を削除する権限がありません。")

        db.session.delete(tournament)
        db.session.commit()
