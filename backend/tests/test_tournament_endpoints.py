import pytest

from app.models import AccessLevel, Tournament


def _create_group(client, name="Parent Group"):
    response = client.post("/api/groups", json={"name": name})
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["group_links"]}
    return data, links


def _create_tournament(client, group_key, name="Main Tournament"):
    """新仕様：グループ共有キーをURLに含める"""
    return client.post(
        f"/api/groups/{group_key}/tournaments",
        json={"name": name},
    )


@pytest.mark.api
class TestTournamentEndpoints:
    def test_create_tournament_requires_group_edit(self, client, db_session):
        group_data, links = _create_group(client)

        # ✅ group_keyをURLに利用（edit権限）
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        assert res.status_code == 201
        tournament = res.get_json()
        assert tournament["group_id"] == group_data["id"]

        # ✅ tournament_links に変更
        levels = {link["access_level"] for link in tournament["tournament_links"]}
        assert levels == {AccessLevel.EDIT.value, AccessLevel.VIEW.value}

    def test_create_tournament_with_view_link_forbidden(self, client, db_session):
        group_data, links = _create_group(client)
        # VIEW権限では作成不可
        res = _create_tournament(client, links[AccessLevel.VIEW.value])
        assert res.status_code == 403

    def test_get_tournament_requires_view(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        tournament = res.get_json()

        # ✅ tournament_links を使って取得
        t_links = {
            link["access_level"]: link["short_key"] for link in tournament["tournament_links"]
        }

        ok = client.get(f"/api/tournaments/{t_links[AccessLevel.VIEW.value]}")
        assert ok.status_code == 200

        forbidden = client.get(f"/api/tournaments/{links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403

    def test_update_tournament_requires_edit(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        tournament = res.get_json()
        t_links = {
            link["access_level"]: link["short_key"] for link in tournament["tournament_links"]
        }

        # VIEW権限では更新不可
        forbidden = client.put(
            f"/api/tournaments/{t_links[AccessLevel.VIEW.value]}",
            json={"name": "Forbidden"},
        )
        assert forbidden.status_code == 403

        # EDIT権限で更新OK
        allowed = client.put(
            f"/api/tournaments/{t_links[AccessLevel.EDIT.value]}",
            json={"name": "Updated"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Tournament, tournament["id"])
        assert updated.name == "Updated"

    def test_delete_tournament_requires_group_edit(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        tournament = res.get_json()
        t_links = {
            link["access_level"]: link["short_key"] for link in tournament["tournament_links"]
        }

        # VIEW権限で削除不可
        forbidden = client.delete(f"/api/tournaments/{t_links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403

        # EDIT権限で削除OK
        allowed = client.delete(f"/api/tournaments/{t_links[AccessLevel.EDIT.value]}")
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Tournament deleted"
        assert db_session.get(Tournament, tournament["id"]) is None
