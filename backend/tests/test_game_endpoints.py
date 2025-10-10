import pytest
from app.models import AccessLevel, Game


def _create_group(client):
    res = client.post("/api/groups", json={"name": "Game Group"})
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["group_links"]}
    return data, links


def _create_tournament(client, group_key, name="Game Tournament"):
    res = client.post(
        f"/api/groups/{group_key}/tournaments",
        json={"name": name},
    )
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["tournament_links"]}
    return data, links


def _create_table(client, tournament_key, name="Game Table"):
    res = client.post(
        f"/api/tournaments/{tournament_key}/tables",
        json={"name": name},
    )
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["table_links"]}
    return data, links


def _create_game(client, table_key, memo="Round 1"):
    """新仕様：卓キーをURLに含める"""
    return client.post(
        f"/api/tables/{table_key}/games",
        json={"game_index": 1, "memo": memo},
    )


@pytest.mark.api
class TestGameEndpoints:
    def test_create_game_requires_table_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value]
        )

        res = _create_game(client, table_links[AccessLevel.EDIT.value])
        assert res.status_code == 201
        game = res.get_json()

        # ✅ game_links に変更
        levels = {l["access_level"] for l in game["game_links"]}
        assert levels == {AccessLevel.EDIT.value, AccessLevel.VIEW.value}

    def test_create_game_with_view_link_forbidden(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value]
        )

        res = _create_game(client, table_links[AccessLevel.VIEW.value])
        assert res.status_code == 403

    def test_get_game_requires_view(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value]
        )
        game_res = _create_game(client, table_links[AccessLevel.EDIT.value])
        game = game_res.get_json()
        game_links = {l["access_level"]: l["short_key"] for l in game["game_links"]}

        ok = client.get(f"/api/games/{game_links[AccessLevel.VIEW.value]}")
        assert ok.status_code == 200

        forbidden = client.get(f"/api/games/{table_links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403

    def test_update_game_requires_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value]
        )
        game_res = _create_game(client, table_links[AccessLevel.EDIT.value])
        game = game_res.get_json()
        game_links = {l["access_level"]: l["short_key"] for l in game["game_links"]}

        forbidden = client.put(
            f"/api/games/{game_links[AccessLevel.VIEW.value]}",
            json={"memo": "Forbidden"},
        )
        assert forbidden.status_code == 403

        allowed = client.put(
            f"/api/games/{game_links[AccessLevel.EDIT.value]}",
            json={"memo": "Updated Memo"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Game, game["id"])
        assert updated.memo == "Updated Memo"

    def test_delete_game_requires_table_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(
            client, tournament_links[AccessLevel.EDIT.value]
        )
        game_res = _create_game(client, table_links[AccessLevel.EDIT.value])
        game = game_res.get_json()
        game_links = {l["access_level"]: l["short_key"] for l in game["game_links"]}

        forbidden = client.delete(f"/api/games/{game_links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403

        allowed = client.delete(f"/api/games/{game_links[AccessLevel.EDIT.value]}")
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Game deleted"
        assert db_session.get(Game, game["id"]) is None
