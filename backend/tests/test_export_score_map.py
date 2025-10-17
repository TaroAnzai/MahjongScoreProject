import pytest
from app.models import AccessLevel


def _create_group(client, name="ScoreMap Group"):
    res = client.post("/api/groups", json={"name": name})
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["group_links"]}
    return data, links


def _create_tournament(client, group_key, name="ScoreMap Tournament"):
    res = client.post(f"/api/groups/{group_key}/tournaments", json={"name": name})
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["tournament_links"]}
    return data, links


def _create_table(client, tournament_key, name="ScoreMap Table"):
    res = client.post(f"/api/tournaments/{tournament_key}/tables", json={"name": name})
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["table_links"]}
    return data, links


def _create_game(client, table_key, game_index=1, memo="Test Game"):
    return client.post(
        f"/api/tables/{table_key}/games",
        json={"game_index": game_index, "memo": memo},
    )


@pytest.mark.api
class TestTournamentScoreMap:
    """GET /api/tournaments/<tournament_key>/score_map"""

    def test_get_tournament_score_map_success(self, client, db_session):
        """正常系: 大会スコアマップを取得"""
        # --- 前提データ作成 ---
        group_data, group_links = _create_group(client)
        tournament_data, tournament_links = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        table_data, table_links = _create_table(client, tournament_links[AccessLevel.EDIT.value])

        # 対局を複数登録
        for i in range(1, 4):
            res_game = _create_game(client, table_links[AccessLevel.EDIT.value], i)
            assert res_game.status_code == 201

        # --- API呼び出し ---
        res = client.get(
            f"/api/tournaments/{tournament_links[AccessLevel.VIEW.value]}/score_map"
        )
        assert res.status_code == 200

        data = res.get_json()
        print(data)
        assert "score_map" in data
        score_map = data["score_map"]

        # --- 構造確認 ---
        assert isinstance(score_map, dict)
        assert all(isinstance(pid, str) for pid in score_map.keys())

        # --- 各プレイヤーの項目確認 ---
        for pid, info in score_map.items():
            assert "total" in info
            assert "games_played" in info
            # 卓キー (table_XX) が存在すること
            assert any(k.startswith("table_") for k in info.keys())

    def test_get_tournament_score_map_not_found(self, client):
        """異常系: 存在しない大会キー"""
        res = client.get("/api/tournaments/xxxxxx/score_map")
        assert res.status_code == 404
        msg = res.get_json()["message"]
        assert "大会" in msg
