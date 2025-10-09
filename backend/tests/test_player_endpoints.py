import pytest

from app.models import AccessLevel, Player


def _create_group(client, name="Player Group"):
    response = client.post("/api/groups", json={"name": name})
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["share_links"]}
    return data, links


def _create_player(client, short_key, group_id, name="Alice"):
    return client.post(
        f"/api/players?short_key={short_key}",
        json={"group_id": group_id, "name": name},
    )


@pytest.mark.api
class TestPlayerEndpoints:
    def test_create_player_requires_group_edit(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_player(client, links[AccessLevel.EDIT.value], group_data["id"])
        assert res.status_code == 201
        player = res.get_json()
        assert player["group_id"] == group_data["id"]

    def test_create_player_with_view_forbidden(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_player(client, links[AccessLevel.VIEW.value], group_data["id"])
        assert res.status_code == 403

    def test_get_player_requires_view(self, client, db_session):
        group_data, links = _create_group(client)
        create_res = _create_player(client, links[AccessLevel.EDIT.value], group_data["id"])
        player_id = create_res.get_json()["id"]

        ok = client.get(f"/api/players/{player_id}?short_key={links[AccessLevel.VIEW.value]}")
        assert ok.status_code == 200

        other_group, other_links = _create_group(client, name="Other")
        forbidden = client.get(
            f"/api/players/{player_id}?short_key={other_links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

    def test_update_player_requires_edit(self, client, db_session):
        group_data, links = _create_group(client)
        create_res = _create_player(client, links[AccessLevel.EDIT.value], group_data["id"])
        player_id = create_res.get_json()["id"]

        forbidden = client.put(
            f"/api/players/{player_id}?short_key={links[AccessLevel.VIEW.value]}",
            json={"nickname": "NG"},
        )
        assert forbidden.status_code == 403

        allowed = client.put(
            f"/api/players/{player_id}?short_key={links[AccessLevel.EDIT.value]}",
            json={"nickname": "Allowed"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Player, player_id)
        assert updated.nickname == "Allowed"

    def test_delete_player_requires_group_edit(self, client, db_session):
        group_data, links = _create_group(client)
        create_res = _create_player(client, links[AccessLevel.EDIT.value], group_data["id"])
        player_id = create_res.get_json()["id"]

        forbidden = client.delete(
            f"/api/players/{player_id}?short_key={links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

        allowed = client.delete(
            f"/api/players/{player_id}?short_key={links[AccessLevel.EDIT.value]}"
        )
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Player deleted"
        assert db_session.get(Player, player_id) is None
