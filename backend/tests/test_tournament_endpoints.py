import pytest

from app.models import AccessLevel, Tournament


def _create_group(client, name="Parent Group"):
    response = client.post("/api/groups", json={"name": name})
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["share_links"]}
    return data, links


def _create_tournament(client, group_id, short_key, name="Main Tournament"):
    return client.post(
        f"/api/tournaments?short_key={short_key}",
        json={"group_id": group_id, "name": name},
    )


@pytest.mark.api
class TestTournamentEndpoints:
    def test_create_tournament_requires_group_edit(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, group_data["id"], links[AccessLevel.EDIT.value])
        assert res.status_code == 201
        tournament = res.get_json()
        assert tournament["group_id"] == group_data["id"]
        levels = {link["access_level"] for link in tournament["share_links"]}
        assert levels == {AccessLevel.EDIT.value, AccessLevel.VIEW.value}

    def test_create_tournament_with_view_link_forbidden(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, group_data["id"], links[AccessLevel.VIEW.value])
        assert res.status_code == 403

    def test_get_tournament_requires_view(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, group_data["id"], links[AccessLevel.EDIT.value])
        tournament = res.get_json()
        tournament_id = tournament["id"]
        tournament_links = {link["access_level"]: link["short_key"] for link in tournament["share_links"]}

        ok = client.get(
            f"/api/tournaments/{tournament_id}?short_key={tournament_links[AccessLevel.VIEW.value]}"
        )
        assert ok.status_code == 200

        forbidden = client.get(
            f"/api/tournaments/{tournament_id}?short_key={links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

    def test_update_tournament_requires_edit(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, group_data["id"], links[AccessLevel.EDIT.value])
        tournament = res.get_json()
        tournament_id = tournament["id"]
        tournament_links = {link["access_level"]: link["short_key"] for link in tournament["share_links"]}

        forbidden = client.put(
            f"/api/tournaments/{tournament_id}?short_key={tournament_links[AccessLevel.VIEW.value]}",
            json={"name": "Forbidden"},
        )
        assert forbidden.status_code == 403

        allowed = client.put(
            f"/api/tournaments/{tournament_id}?short_key={tournament_links[AccessLevel.EDIT.value]}",
            json={"name": "Updated"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Tournament, tournament_id)
        assert updated.name == "Updated"

    def test_delete_tournament_requires_group_edit(self, client, db_session):
        group_data, links = _create_group(client)
        res = _create_tournament(client, group_data["id"], links[AccessLevel.EDIT.value])
        tournament_id = res.get_json()["id"]

        forbidden = client.delete(
            f"/api/tournaments/{tournament_id}?short_key={links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

        allowed = client.delete(
            f"/api/tournaments/{tournament_id}?short_key={links[AccessLevel.EDIT.value]}"
        )
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Tournament deleted"
        assert db_session.get(Tournament, tournament_id) is None
