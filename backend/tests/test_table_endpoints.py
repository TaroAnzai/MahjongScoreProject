import pytest
from app.models import AccessLevel, Table


def _create_group(client):
    res = client.post("/api/groups", json={"name": "Table Group"})
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["group_links"]}
    return data, links


def _create_tournament(client, group_key, name="Table Tournament"):
    res = client.post(
        f"/api/groups/{group_key}/tournaments",
        json={"name": name},
    )
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["tournament_links"]}
    return data, links


def _create_table(client, tournament_key, name="Primary Table"):
    """新仕様：大会キーをURLに含めて作成"""
    return client.post(
        f"/api/tournaments/{tournament_key}/tables",
        json={"name": name},
    )


@pytest.mark.api
class TestTableEndpoints:
    def test_create_table_requires_tournament_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )

        res = _create_table(client, tournament_links[AccessLevel.EDIT.value])
        assert res.status_code == 201
        table = res.get_json()

        # ✅ table_links に変更
        levels = {l["access_level"] for l in table["table_links"]}
        assert levels == {AccessLevel.EDIT.value, AccessLevel.VIEW.value}

    def test_create_table_with_view_link_forbidden(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )

        res = _create_table(client, tournament_links[AccessLevel.VIEW.value])
        assert res.status_code == 403

    def test_get_table_requires_view(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_res = _create_table(client, tournament_links[AccessLevel.EDIT.value])
        table = table_res.get_json()
        table_links = {l["access_level"]: l["short_key"] for l in table["table_links"]}

        ok = client.get(f"/api/tables/{table_links[AccessLevel.VIEW.value]}")
        assert ok.status_code == 200
        table_data = ok.get_json()
        print(table_data)
        assert "parent_tournament_link" in table_data
        assert "view_link" in table_data["parent_tournament_link"]

        forbidden = client.get(f"/api/tables/{tournament_links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403

    def test_update_table_requires_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_res = _create_table(client, tournament_links[AccessLevel.EDIT.value])
        table = table_res.get_json()
        table_links = {l["access_level"]: l["short_key"] for l in table["table_links"]}

        forbidden = client.put(
            f"/api/tables/{table_links[AccessLevel.VIEW.value]}",
            json={"name": "Forbidden"},
        )
        assert forbidden.status_code == 403

        allowed = client.put(
            f"/api/tables/{table_links[AccessLevel.EDIT.value]}",
            json={"name": "Updated Table"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Table, table["id"])
        assert updated.name == "Updated Table"

    def test_delete_table_requires_tournament_edit(self, client, db_session):
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_res = _create_table(client, tournament_links[AccessLevel.EDIT.value])
        table = table_res.get_json()
        table_links = {l["access_level"]: l["short_key"] for l in table["table_links"]}

        forbidden = client.delete(f"/api/tables/{table_links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403

        allowed = client.delete(f"/api/tables/{table_links[AccessLevel.EDIT.value]}")
        assert allowed.status_code == 200
        assert allowed.get_json()["message"] == "Table deleted"
        assert db_session.get(Table, table["id"]) is None
    def test_get_games_by_table(self, client, db_session,create_players,register_tournament_participants):
        """GET: /api/tables/<table_key>/games - 卓内対局一覧取得"""
        # --- 前提：グループ・大会・卓を作成 ---
        group_data, group_links = _create_group(client)
        players = create_players(group_links[AccessLevel.EDIT.value])
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        register_tournament_participants(tournament_links[AccessLevel.EDIT.value], players)
        table_res = _create_table(client, tournament_links[AccessLevel.EDIT.value])
        table = table_res.get_json()
        table_links = {l["access_level"]: l["short_key"] for l in table["table_links"]}
        scores = [
                {"player_id": players[0]["id"], "score": 25000},
                {"player_id": players[1]["id"], "score": -8000},
                {"player_id": players[2]["id"], "score": -8000},
                {"player_id": players[3]["id"], "score": -9000},
            ]
        # --- 対局を2件登録 ---
        for i in range(1, 3):
            res = client.post(
                f"/api/tables/{table_links[AccessLevel.EDIT.value]}/games",
                json={"memo": f"Round {i}", "scores": scores},
            )
            assert res.status_code == 201

        # --- GET: 一覧取得 ---
        res_list = client.get(f"/api/tables/{table_links[AccessLevel.VIEW.value]}/games")
        assert res_list.status_code == 200

        data = res_list.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

        Game1 = data[0]
        assert "game_index" in Game1


        # 対局インデックスが昇順で並んでいることを確認
        indexes = [g["game_index"] for g in data]
        assert indexes == sorted(indexes)

        # --- 存在しない table_key で 404 ---
        res_404 = client.get("/api/tables/xxxxxx/games")
        assert res_404.status_code == 404
        json = res_404.get_json()
        assert "table_keyが無効です。" in json['errors']['json']["message"]
