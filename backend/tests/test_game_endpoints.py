import pytest

from app.models import AccessLevel, Game


def _create_group(client):
    response = client.post("/api/groups", json={"name": "Game Group"})
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["group_links"]}
    return data, links


def _create_tournament(client, group_id, short_key):
    response = client.post(
        f"/api/tournaments?short_key={short_key}",
        json={"group_id": group_id, "name": "Game Tournament"},
    )
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["group_links"]}
    return data, links


def _create_table(client, short_key, tournament_id):
    response = client.post(
        f"/api/tables?short_key={short_key}",
        json={"tournament_id": tournament_id, "name": "Game Table"},
    )
    data = response.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["share_links"]}
    return data, links


def _create_game(client, short_key, table_id, memo="Round 1"):
    return client.post(
        f"/api/games?short_key={short_key}",
        json={"table_id": table_id, "game_index": 1, "memo": memo},
    )


@pytest.mark.api
class TestGameEndpoints:
    def test_create_game_requires_table_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )

        res = _create_game(client, table_links[AccessLevel.EDIT.value], table_data["id"])
        assert res.status_code == 201
        game = res.get_json()
        levels = {link["access_level"] for link in game["share_links"]}
        assert levels == {AccessLevel.EDIT.value, AccessLevel.VIEW.value}

    def test_create_game_with_view_link_forbidden(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )

        res = _create_game(client, table_links[AccessLevel.VIEW.value], table_data["id"])
        assert res.status_code == 403

    def test_get_game_requires_view(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )
        game_response = _create_game(
            client, table_links[AccessLevel.EDIT.value], table_data["id"]
        )
        game = game_response.get_json()
        game_links = {link["access_level"]: link["short_key"] for link in game["share_links"]}

        ok = client.get(f"/api/games/{game['id']}?short_key={game_links[AccessLevel.VIEW.value]}")
        assert ok.status_code == 200

        forbidden = client.get(
            f"/api/games/{game['id']}?short_key={table_links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

    def test_update_game_requires_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )
        game_response = _create_game(
            client, table_links[AccessLevel.EDIT.value], table_data["id"]
        )
        game = game_response.get_json()
        game_links = {link["access_level"]: link["short_key"] for link in game["share_links"]}

        forbidden = client.put(
            f"/api/games/{game['id']}?short_key={game_links[AccessLevel.VIEW.value]}",
            json={"memo": "Forbidden"},
        )
        assert forbidden.status_code == 403

        allowed = client.put(
            f"/api/games/{game['id']}?short_key={game_links[AccessLevel.EDIT.value]}",
            json={"memo": "Updated Memo"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Game, game["id"])
        assert updated.memo == "Updated Memo"

    def test_delete_game_requires_table_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_data["id"], group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value], tournament_data["id"]
        )
        game_response = _create_game(
            client, table_links[AccessLevel.EDIT.value], table_data["id"]
        )
        game_id = game_response.get_json()["id"]

        forbidden = client.delete(
            f"/api/games/{game_id}?short_key={table_links[AccessLevel.VIEW.value]}"
        )
        assert forbidden.status_code == 403

        allowed = client.delete(
            f"/api/games/{game_id}?short_key={table_links[AccessLevel.EDIT.value]}"
        )
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Game deleted"
        assert db_session.get(Game, game_id) is None
