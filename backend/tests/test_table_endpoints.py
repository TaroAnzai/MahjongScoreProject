import pytest

from app.models import AccessLevel, Table


def _create_group(client):
    response = client.post("/api/groups", json={"name": "Table Group"})
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["share_links"]}
    return data, links


def _create_tournament(client, group_id, short_key):
    response = client.post(
        f"/api/tournaments?short_key={short_key}",
        json={"group_id": group_id, "name": "Table Tournament"},
    )
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["share_links"]}
    return data, links


def _create_table(client, short_key, tournament_id, name="Primary Table"):
    return client.post(
        f"/api/tables?short_key={short_key}",
        json={"tournament_id": tournament_id, "name": name},
    )


@pytest.mark.api
class TestTableEndpoints:
    def test_create_table_requires_tournament_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )

        res = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )
        assert res.status_code == 201
        table = res.get_json()
        levels = {link["access_level"] for link in table["share_links"]}
        assert levels == {AccessLevel.EDIT.value, AccessLevel.VIEW.value}

    def test_create_table_with_view_link_forbidden(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )

        res = _create_table(
            client, tournament_links[AccessLevel.VIEW.value], tournament_data["id"]
        )
        assert res.status_code == 403

    def test_get_table_requires_view(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_response = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )
        table = table_response.get_json()
        table_links = {link["access_level"]: link["short_key"] for link in table["share_links"]}

        ok = client.get(f"/api/tables/{table['id']}?short_key={table_links[AccessLevel.VIEW.value]}")
        assert ok.status_code == 200

        forbidden = client.get(
            f"/api/tables/{table['id']}?short_key={tournament_links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

    def test_update_table_requires_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_response = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )
        table = table_response.get_json()
        table_links = {link["access_level"]: link["short_key"] for link in table["share_links"]}

        forbidden = client.put(
            f"/api/tables/{table['id']}?short_key={table_links[AccessLevel.VIEW.value]}",
            json={"name": "Forbidden"},
        )
        assert forbidden.status_code == 403

        allowed = client.put(
            f"/api/tables/{table['id']}?short_key={table_links[AccessLevel.EDIT.value]}",
            json={"name": "Updated Table"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Table, table["id"])
        assert updated.name == "Updated Table"

    def test_delete_table_requires_tournament_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_response = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )
        table_id = table_response.get_json()["id"]

        forbidden = client.delete(
            f"/api/tables/{table_id}?short_key={tournament_links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

        allowed = client.delete(
            f"/api/tables/{table_id}?short_key={tournament_links[AccessLevel.EDIT.value]}"
        )
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Table deleted"
        assert db_session.get(Table, table_id) is None
