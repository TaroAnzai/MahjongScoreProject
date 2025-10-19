import pytest
from app.models import AccessLevel



@pytest.mark.api
class TestTournamentScoreMap:
    """GET /api/tournaments/<tournament_key>/score_map"""

    def test_get_tournament_score_map_success(self, client, db_session, setup_full_tournament):
        """正常系: 大会スコアマップを取得"""
        # --- 前提データ作成 ---
        data = setup_full_tournament(client)
        tournament_links = data["tournament_links"]
        # --- API呼び出し ---
        res = client.get(
            f"/api/tournaments/{tournament_links[AccessLevel.VIEW.value]}/score_map"
        )
        assert res.status_code == 200

        result = res.get_json()
        # --- トップレベル構造確認 ---
        assert "tournament_id" in result
        assert "tables" in result
        assert "players" in result
        assert "rate" in result

        # --- tables 構造確認 ---
        tables = result["tables"]
        assert isinstance(tables, list)
        assert all("id" in t and "name" in t for t in tables)

        # --- players 構造確認 ---
        players = result["players"]
        assert isinstance(players, list)
        assert len(players) > 0

        for p in players:
            assert "id" in p
            assert "name" in p
            assert "scores" in p
            assert isinstance(p["scores"], dict)

            # スコアのキーはtable_id文字列
            for k, v in p["scores"].items():
                assert isinstance(k, str)
                assert isinstance(v, (int, float))

            # 合計と換算合計
            assert "total" in p
            assert "converted_total" in p
            assert isinstance(p["total"], (int, float))
            assert isinstance(p["converted_total"], (int, float))

        # --- rate 値確認 ---
        assert isinstance(result["rate"], (float, int))
        assert result["rate"] > 0

        # --- 表形式整合チェック ---
        # すべてのtable_idが players[].scores のキーと整合すること
        table_ids = {str(t["id"]) for t in tables}
        for p in players:
            for key in p["scores"].keys():
                assert key in table_ids or key.isnumeric()

    def test_get_tournament_score_map_not_found(self, client):
        """異常系: 存在しない大会キー"""
        res = client.get("/api/tournaments/xxxxxx/score_map")
        assert res.status_code == 404
        msg = res.get_json()["message"]
        assert "大会" in msg
