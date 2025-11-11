import pytest
from datetime import datetime, timedelta
from app.models import Tournament

@pytest.mark.usefixtures("client")
class TestGroupPlayerStatsAPI:
    """グループプレイヤー統計API (/api/groups/<key>/player_stats) のテスト"""

    def test_get_all_period_stats(self, client, db_session, setup_full_tournament):
        """期間指定なし（全期間）の統計が取得できる"""
        data = setup_full_tournament(client)
        group_key = data["group_links"]["VIEW"]  # groupリンクキー

        # API呼び出し（期間指定なし）
        res = client.get(f"/api/groups/{group_key}/player_stats")
        assert res.status_code == 200, res.data

        json_data = res.get_json()
        assert "group" in json_data
        assert "players" in json_data
        assert isinstance(json_data["players"], list)
        assert len(json_data["players"]) == 4  # 4プレイヤー登録済み

        # 各プレイヤー統計の必須項目確認
        for p in json_data["players"]:
            assert "player_name" in p
            assert "game_count" in p
            assert "tournament_count" in p
            assert "total_score" in p
            assert "average_rank" in p

    def test_get_period_filtered_stats(self, client, db_session, setup_full_tournament):
        """期間指定ありで、Tournament.started_atに基づくフィルタが動作する"""
        data = setup_full_tournament(client)
        group_key = data["group_links"]["VIEW"]

        # --- 大会の日付を操作 ---
        tournaments = db_session.query(Tournament).all()
        assert len(tournaments) >= 1
        t = tournaments[0]
        t.started_at = datetime(2025, 5, 1)
        db_session.commit()

        # --- フィルタ範囲内（ヒットする） ---
        res = client.get(
            f"/api/groups/{group_key}/player_stats?start_date=2025-04-01&end_date=2025-06-01"
        )
        assert res.status_code == 200, res.data
        players = res.get_json()["players"]
        assert len(players) == 4  # 全員が含まれる

        # --- フィルタ範囲外（ヒットしない） ---
        res2 = client.get(
            f"/api/groups/{group_key}/player_stats?start_date=2025-06-02&end_date=2025-06-30"
        )
        assert res2.status_code == 200, res2.data
        players2 = res2.get_json()["players"]
        assert len(players2) == 0  # 該当なし

    def test_invalid_date_format(self, client, setup_full_tournament):
        """不正な日付フォーマットを渡した場合に400エラーが返る"""
        data = setup_full_tournament(client)
        group_key = data["group_links"]["VIEW"]

        res = client.get(
            f"/api/groups/{group_key}/player_stats?start_date=invalid-date"
        )
        # サービス内でServiceNotFoundErrorがraiseされ、JSONエラーレスポンスとなる想定
        assert res.status_code == 422
