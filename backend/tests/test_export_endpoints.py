import pytest
from app.models import AccessLevel


@pytest.mark.api
class TestExportEndpoints:
    """export_resource.py のエンドポイントを検証"""

    def test_export_tournament_results(self, client, db_session, setup_full_tournament):
        """GET: /api/tournaments/<tournament_key>/export"""
        # --- 前提データ作成 ---
        data = setup_full_tournament(client)
        tournament_links = data["tournament_links"]

        # --- 実行 ---
        res = client.get(f"/api/tournaments/{tournament_links[AccessLevel.VIEW.value]}/export")
        assert res.status_code == 200

        data = res.get_json()
        assert "tournament" in data
        assert "players" in data
        assert isinstance(data["players"], list)

        # --- 存在しないキーで404 ---
        res_404 = client.get("/api/tournaments/xxxxxx/export")
        assert res_404.status_code == 404

    def test_export_group_summary(self, client, db_session, create_group, create_players,
                                  create_tournament,
                                   create_table, create_game,
                                   register_tournament_participants,
                                   register_table_players):
        """GET: /api/groups/<group_key>/summary"""
        # --- グループと大会を複数作成 ---
        group_data, group_links = create_group()
        players = create_players(group_links[AccessLevel.EDIT.value])
        t1_data, t1_links = create_tournament(group_links[AccessLevel.EDIT.value], name="Spring Cup")
        register_tournament_participants(t1_links[AccessLevel.EDIT.value], players)

        t2_data, t2_links = create_tournament(group_links[AccessLevel.EDIT.value], name="Summer Cup")
        register_tournament_participants(t2_links[AccessLevel.EDIT.value], players)
        res = client.get(f"/api/tournaments/{t1_links[AccessLevel.VIEW.value]}/participants")
        # 卓・対局データを追加
        table1, table1_links = create_table(t1_links[AccessLevel.EDIT.value])
        register_table_players(table1_links[AccessLevel.EDIT.value], players)
        create_game(table1_links[AccessLevel.EDIT.value], players)

        table2, table2_links = create_table(t2_links[AccessLevel.EDIT.value])
        register_table_players(table2_links[AccessLevel.EDIT.value], players)
        create_game(table2_links[AccessLevel.EDIT.value], players)

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
