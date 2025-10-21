import pytest
from app.models import TournamentPlayer, AccessLevel


# ---------- ヘルパー関数群 ----------

def _create_group(client, name="Tournament Group"):
    res = client.post("/api/groups", json={"name": name})
    assert res.status_code == 201
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["group_links"]}
    return data, links


def _create_tournament(client, group_key, name="Main Tournament"):
    res = client.post(
        f"/api/groups/{group_key}/tournaments",
        json={"name": name},
    )
    assert res.status_code == 201
    data = res.get_json()
    links = {l["access_level"]: l["short_key"] for l in data["tournament_links"]}
    return data, links


def _create_player(client, group_key, name="Alice"):
    res = client.post(
        f"/api/groups/{group_key}/players",
        json={"name": name},
    )
    assert res.status_code == 201
    return res.get_json()


@pytest.fixture
def setup_group_with_tournament(client):
    """グループ・大会・プレイヤーを作成"""
    group, group_links = _create_group(client)
    g_edit_key = group_links[AccessLevel.EDIT.value]

    # Tournament作成
    tournament, tournament_links = _create_tournament(client, g_edit_key)
    t_edit_key = tournament_links[AccessLevel.EDIT.value]

    # プレイヤー3名登録
    players = [
        _create_player(client, g_edit_key, "Alice"),
        _create_player(client, g_edit_key, "Bob"),
        _create_player(client, g_edit_key, "Charlie"),
    ]

    return {
        "group": group,
        "tournament": tournament,
        "players": players,
        "group_key": g_edit_key,
        "tournament_key": t_edit_key,
    }


# ---------- テストケース ----------

def test_create_tournament_participant(client, setup_group_with_tournament, db_session):
    """POST /api/tournaments/<tournament_key>/participants — プレイヤー登録"""
    d = setup_group_with_tournament
    url = f"/api/tournaments/{d['tournament_key']}/participants"

    res = client.post(url, json={'participants':[{"player_id": d["players"][0]["id"]}]})
    assert res.status_code == 201

    created = db_session.query(TournamentPlayer).filter_by(
        tournament_id=d["tournament"]["id"],
        player_id=d["players"][0]["id"]
    ).first()
    assert created is not None


def test_list_tournament_participants(client, setup_group_with_tournament, db_session):
    """GET /api/tournaments/<tournament_key>/participants — 参加者一覧取得"""
    d = setup_group_with_tournament
    participant = TournamentPlayer(
        tournament_id=d["tournament"]["id"],
        player_id=d["players"][0]["id"]
    )
    db_session.add(participant)
    db_session.commit()

    url = f"/api/tournaments/{d['tournament_key']}/participants"
    res = client.get(url)
    assert res.status_code == 200
    result = res.get_json()['participants']
    assert isinstance(result, list)
    assert any(p["player_id"] == d["players"][0]["id"] for p in result)


def test_delete_tournament_participant(client, setup_group_with_tournament, db_session):
    """DELETE /api/tournaments/<tournament_key>/participants/<participant_id> — 削除"""
    d = setup_group_with_tournament
    url = f"/api/tournaments/{d['tournament_key']}/participants"

    res = client.post(url, json={"participants":[{"player_id": d["players"][0]["id"]}]})
    assert res.status_code == 201
    participant = res.get_json()['participants'][0]
    url = f"/api/tournaments/{d['tournament_key']}/participants/{participant['player_id']}"
    res = client.delete(url)
    assert res.status_code == 200
    assert res.get_json()["message"] == "Tournament participant deleted"

    deleted = db_session.get(TournamentPlayer, participant["player_id"])
    assert deleted is None


def test_create_with_invalid_key(client, setup_group_with_tournament):
    """無効な tournament_key の場合 404"""
    d = setup_group_with_tournament
    player = d["players"][0]
    url = f"/api/tournaments/invalid-key/participants"
    res = client.post(url, json={'participants':[{"player_id": player["id"]}]})
    assert res.status_code == 404


def test_create_duplicate_participant(client, setup_group_with_tournament, db_session):
    """重複登録は400"""
    d = setup_group_with_tournament
    p = d["players"][0]
    participant = TournamentPlayer(
        tournament_id=d["tournament"]["id"], player_id=p["id"]
    )

    db_session.add(participant)
    db_session.commit()
    url = f"/api/tournaments/{d['tournament_key']}/participants"
    res = client.post(url, json={'participants':[{"player_id": p["id"]}]})
    print("Response:", res.get_json())
    assert res.status_code == 201
    assert res.get_json()["added_count"] == 0
    assert len(res.get_json()["errors"]) == 1
    assert "すでに登録されています" in res.get_json()["errors"][0]['error']
