import pytest
from app.models import AccessLevel, Player



def _create_player(client, group_key, name="Alice"):
    """新仕様：グループキーをURLに含めて作成"""
    return client.post(
        f"/api/groups/{group_key}/players",
        json={"name": name},
    )


@pytest.mark.api
class TestPlayerEndpoints:
    def test_create_player_requires_group_edit(self, client, db_session, create_group):
        group_data, links = create_group("Player Group")

        # ✅ group_keyをURLに使用
        res = _create_player(client, links[AccessLevel.EDIT.value])
        assert res.status_code == 201
        player = res.get_json()
        assert player["group_id"] == group_data["id"]

    def test_create_player_with_view_forbidden(self, client, db_session, create_group):
        group_data, links = create_group("Player Group")
        res = _create_player(client, links[AccessLevel.VIEW.value])
        assert res.status_code == 403

    def test_get_player_requires_view(self, client, db_session, create_group):
        group_data, links = create_group()
        create_res = _create_player(client, links[AccessLevel.EDIT.value])
        player = create_res.get_json()

        ok = client.get(f"/api/groups/{links[AccessLevel.VIEW.value]}/players/{player['id']}")
        assert ok.status_code == 200

        other_group, other_links = create_group("Other Group")
        forbidden = client.get(f"/api/groups/{other_links[AccessLevel.VIEW.value]}/players/{player['id']}")
        assert forbidden.status_code == 404

    def test_update_player_requires_edit(self, client, db_session, create_group):
        group_data, links = create_group()
        create_res = _create_player(client, links[AccessLevel.EDIT.value])
        player = create_res.get_json()

        # VIEW権限では更新不可
        forbidden = client.put(
            f"/api/groups/{links[AccessLevel.VIEW.value]}/players/{player['id']}",
            json={"nickname": "NG"},
        )
        assert forbidden.status_code == 403

        # EDIT権限で更新OK
        allowed = client.put(
            f"/api/groups/{links[AccessLevel.EDIT.value]}/players/{player['id']}",
            json={"nickname": "Allowed"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Player, player["id"])
        assert updated.nickname == "Allowed"

    def test_delete_player_requires_group_edit(self, client, db_session, create_group):
        group_data, links = create_group("Player Group")
        create_res = _create_player(client, links[AccessLevel.EDIT.value])
        player = create_res.get_json()

        forbidden = client.delete(f"/api/groups/{links[AccessLevel.VIEW.value]}/players/{player['id']}")
        assert forbidden.status_code == 403

        allowed = client.delete(f"/api/groups/{links[AccessLevel.EDIT.value]}/players/{player['id']}")
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Player deleted"
        assert db_session.get(Player, player["id"]) is None
