import pytest
from app.models import AccessLevel


def _create_group(client, name="Export Group"):
    res = client.post("/api/groups", json={"name": name})
    data = res.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["group_links"]}
    return data, links


def _create_tournament(client, group_key, name="Export Tournament"):
    res = client.post(f"/api/groups/{group_key}/tournaments", json={"name": name})
    data = res.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["tournament_links"]}
    return data, links


def _create_table(client, tournament_key, name="Export Table"):
    res = client.post(f"/api/tournaments/{tournament_key}/tables", json={"name": name})
    data = res.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["table_links"]}
    return data, links


def _create_game(client, table_key, game_index=1, memo="Test Game"):
    return client.post(
        f"/api/tables/{table_key}/games",
        json={"game_index": game_index, "memo": memo},
    )


@pytest.mark.api
class TestExportEndpoints:
    """export_resource.py のエンドポイントを検証"""

    def test_export_tournament_results(self, client, db_session):
        """GET: /api/tournaments/<tournament_key>/export"""
        # --- 前提データ作成 ---
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(client, tournament_links[AccessLevel.EDIT.value])

        # 対局データを2件登録
        for i in range(1, 3):
            res_game = _create_game(client, table_links[AccessLevel.EDIT.value], i)
            assert res_game.status_code == 201

        # --- 実行 ---
        res = client.get(f"/api/tournaments/{tournament_links[AccessLevel.VIEW.value]}/export")
        print(res.get_json())
        assert res.status_code == 200

        data = res.get_json()
        assert "tournament" in data
        assert "players" in data
        assert isinstance(data["players"], list)

        # --- 存在しないキーで404 ---
        res_404 = client.get("/api/tournaments/xxxxxx/export")
        assert res_404.status_code == 404

    def test_export_group_summary(self, client, db_session):
        """GET: /api/groups/<group_key>/summary"""
        # --- グループと大会を複数作成 ---
        group_data, group_links = _create_group(client)
        t1_data, t1_links = _create_tournament(client, group_links[AccessLevel.EDIT.value], name="Spring Cup")
        t2_data, t2_links = _create_tournament(client, group_links[AccessLevel.EDIT.value], name="Summer Cup")

        # 卓・対局データを追加
        table1, table1_links = _create_table(client, t1_links[AccessLevel.EDIT.value])
        _create_game(client, table1_links[AccessLevel.EDIT.value], 1)

        table2, table2_links = _create_table(client, t2_links[AccessLevel.EDIT.value])
        _create_game(client, table2_links[AccessLevel.EDIT.value], 1)

        # --- 実行 ---
        res = client.get(f"/api/groups/{group_links[AccessLevel.VIEW.value]}/summary")
        assert res.status_code == 200

        data = res.get_json()
        assert "group" in data
        assert "tournaments" in data
        assert len(data["tournaments"]) >= 2

        # --- 存在しないキーで404 ---
        res_404 = client.get("/api/groups/xxxxxx/summary")
        assert res_404.status_code == 404
