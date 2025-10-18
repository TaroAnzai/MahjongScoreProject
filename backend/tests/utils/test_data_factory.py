"""
| fixture名                           | 役割                 | スコープ     |
| ---------------------------------- | ------------------ | -------- |
| `create_group`                     | グループ作成             | function |
| `create_players`                   | グループ内プレイヤー作成       | function |
| `create_tournament`                | 大会作成               | function |
| `register_tournament_participants` | 大会への参加者登録          | function |
| `create_table`                     | 卓作成                | function |
| `register_table_players`           | 卓へのプレイヤー登録         | function |
| `create_game`                      | 対局登録（スコア付き）        | function |
| `setup_full_tournament`            | 上記すべてをまとめた完全データセット | function | """


import pytest
from app.models import AccessLevel


# ---------------------------------------------
# グループ作成
# ---------------------------------------------
@pytest.fixture(scope="function")
def create_group(client):
    def _create_group(name="Export Group"):
        res = client.post("/api/groups", json={"name": name})
        assert res.status_code == 201
        data = res.get_json()
        links = {l["access_level"]: l["short_key"] for l in data["group_links"]}
        return data, links
    return _create_group


# ---------------------------------------------
# プレイヤー4名登録
# ---------------------------------------------
@pytest.fixture(scope="function")
def create_players(client):
    def _create_players(group_key, names=None):
        if names is None:
            names = ["Aさん", "Bさん", "Cさん", "Dさん"]
        players = []
        for n in names:
            res = client.post(f"/api/groups/{group_key}/players", json={"name": n})
            assert res.status_code == 201
            players.append(res.get_json())
        return players
    return _create_players


# ---------------------------------------------
# トーナメント作成
# ---------------------------------------------
@pytest.fixture(scope="function")
def create_tournament(client):
    def _create_tournament(group_key, name="Export Tournament"):
        res = client.post(f"/api/groups/{group_key}/tournaments", json={"name": name})
        assert res.status_code == 201
        data = res.get_json()
        links = {l["access_level"]: l["short_key"] for l in data["tournament_links"]}
        return data, links
    return _create_tournament


# ---------------------------------------------
# トーナメント参加者登録
# ---------------------------------------------
@pytest.fixture(scope="function")
def register_tournament_participants(client):
    def _register_tournament_participants(tournament_key, players):
        for p in players:
            res = client.post(
                f"/api/tournaments/{tournament_key}/participants",
                json={"player_id": p["id"]},
            )
            assert res.status_code == 201
    return _register_tournament_participants


# ---------------------------------------------
# テーブル作成
# ---------------------------------------------
@pytest.fixture(scope="function")
def create_table(client):
    def _create_table(tournament_key, name="Export Table"):
        res = client.post(f"/api/tournaments/{tournament_key}/tables", json={"name": name})
        assert res.status_code == 201
        data = res.get_json()
        links = {l["access_level"]: l["short_key"] for l in data["table_links"]}
        return data, links
    return _create_table


# ---------------------------------------------
# テーブル参加者登録
# ---------------------------------------------
@pytest.fixture(scope="function")
def register_table_players(client):
    def _register_table_players(table_key, players):
        for p in players:
            res = client.post(
                f"/api/tables/{table_key}/players",
                json={"player_id": p["id"]},
            )
            assert res.status_code == 201
    return _register_table_players


# ---------------------------------------------
# 対局（ゲーム）登録（scores付き）
# ---------------------------------------------
@pytest.fixture(scope="function")
def create_game(client):
    def _create_game(table_key, players, memo="Test Game", scores=None):
        """
        players: create_players() で作成したプレイヤーリスト
        scores: 明示的に渡さない場合はデフォルト点数で自動生成
        """
        if scores is None:
            # デフォルト: 1位 +25000, 残りは合計0に調整
            scores = [
                {"player_id": players[0]["id"], "score": 25000},
                {"player_id": players[1]["id"], "score": -8000},
                {"player_id": players[2]["id"], "score": -8000},
                {"player_id": players[3]["id"], "score": -9000},
            ]
            total = sum(s["score"] for s in scores)
            scores[-1]["score"] -= total  # 念のため合計0補正

        res = client.post(
            f"/api/tables/{table_key}/games",
            json={"memo": memo, "scores": scores},
        )
        assert res.status_code == 201
        return res.get_json()
    return _create_game


# ---------------------------------------------
# フルセット（グループ→プレイヤー→大会→卓→ゲーム）
# ---------------------------------------------
@pytest.fixture(scope="function")
def setup_full_tournament(
    create_group,
    create_players,
    create_tournament,
    register_tournament_participants,
    create_table,
    register_table_players,
    create_game,
):
    def _setup_full_tournament(client):
        # 1️⃣ グループ作成
        group_data, group_links = create_group()

        # 2️⃣ プレイヤー登録
        players = create_players(group_links[AccessLevel.EDIT.value])

        # 3️⃣ トーナメント作成
        tournament_data, tournament_links = create_tournament(group_links[AccessLevel.EDIT.value])

        # 4️⃣ トーナメント参加者登録
        register_tournament_participants(tournament_links[AccessLevel.EDIT.value], players)

        # 5️⃣ テーブル作成
        table_data, table_links = create_table(tournament_links[AccessLevel.EDIT.value])

        # 6️⃣ テーブル参加者登録
        register_table_players(table_links[AccessLevel.EDIT.value], players)

        # 7️⃣ ゲーム登録（スコア付き）
        game_data = create_game(table_links[AccessLevel.EDIT.value], players)

        return {
            "group_links": group_links,
            "tournament_links": tournament_links,
            "table_links": table_links,
            "players": players,
            "game": game_data,
        }

    return _setup_full_tournament
