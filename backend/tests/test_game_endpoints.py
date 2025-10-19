import pytest
from app.models import AccessLevel, Game



@pytest.mark.api
class TestGameEndpoints:
    def test_create_game_requires_table_edit(self, client, db_session,setup_full_tournament):
        data = setup_full_tournament(client)
        players = data["players"]
        table_links = data["table_links"]
        table_key_edit = table_links[AccessLevel.EDIT.value]
        scores = [
                {"player_id": players[0]["id"], "score": 25000},
                {"player_id": players[1]["id"], "score": -8000},
                {"player_id": players[2]["id"], "score": -8000},
                {"player_id": players[3]["id"], "score": -9000},
            ]
        memo = "Test Game Creation"
        res = client.post(
            f"/api/tables/{table_key_edit}/games",
            json={"memo": memo, "scores": scores},
        )
        assert res.status_code == 201
        game = res.get_json()
        assert game["memo"] == memo
        assert len(game["scores"]) == 4




    def test_create_game_with_view_link_forbidden(self, client, db_session,setup_full_tournament,create_game):
        data = setup_full_tournament(client)
        table_links = data["table_links"]
        table_key_view = table_links[AccessLevel.VIEW.value]
        players = data["players"]
        scores = [
                {"player_id": players[0]["id"], "score": 25000},
                {"player_id": players[1]["id"], "score": -8000},
                {"player_id": players[2]["id"], "score": -8000},
                {"player_id": players[3]["id"], "score": -9000},
            ]
        res = client.post(
            f"/api/tables/{table_key_view}/games",
            json={"memo": "Should Fail", "scores": scores},
        )
        assert res.status_code == 403

    def test_get_game_requires_view(self, client, db_session,setup_full_tournament):
        data = setup_full_tournament(client)
        table_links = data["table_links"]
        game_data = data["game"]

        ok = client.get(f"/api/tables/{table_links[AccessLevel.EDIT.value]}/games/{game_data['id']}")
        assert ok.status_code == 200

        forbidden = client.get(f"/api/tables/xxxx/games/{game_data['id']}")
        assert forbidden.status_code == 404

    def test_update_game_requires_edit(self, client, db_session,setup_full_tournament):
        data = setup_full_tournament(client)
        table_links = data["table_links"]
        players = data["players"]
        game_data = data["game"]
        update_scores = [
                {"player_id": players[0]["id"], "score": 24000},
                {"player_id": players[1]["id"], "score": -8000},
                {"player_id": players[2]["id"], "score": -8000},
                {"player_id": players[3]["id"], "score": -8000},
            ]
        payload ={"memo": "Updated Memo", "scores": update_scores}
        forbidden = client.put(
            f"/api/tables/{table_links[AccessLevel.VIEW.value]}/games/{game_data['id']}",
            json=payload,
        )
        assert forbidden.status_code == 403

        allowed = client.put(
            f"/api/tables/{table_links[AccessLevel.EDIT.value]}/games/{game_data['id']}",
            json=payload,
        )
        updated = allowed.get_json()
        assert allowed.status_code == 200
        assert updated["memo"] == "Updated Memo"

    def test_delete_game_requires_table_edit(self, client, db_session, setup_full_tournament):
        data = setup_full_tournament(client)
        game = data["game"]
        table_links = data["table_links"]

        forbidden = client.delete(f"/api/tables/{table_links[AccessLevel.VIEW.value]}/games/{game['id']}")
        assert forbidden.status_code == 403

        allowed = client.delete(f"/api/tables/{table_links[AccessLevel.EDIT.value]}/games/{game['id']}")
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Game deleted"
        assert db_session.get(Game, game["id"]) is None
