# tests/test_tournament_participant_api.py
import pytest
from app.models import TournamentPlayer

def _create_group(client, name="Table Group", description="for tournament test"):
    res = client.post("/api/groups", json={"name": name, "description": description})
    assert res.status_code == 201
    data = res.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["share_links"]}
    return data, links


def _create_tournament(client, group_id, short_key, name="Table Tournament"):
    res = client.post(
        f"/api/tournaments?short_key={short_key}",
        json={"group_id": group_id, "name": name},
    )
    assert res.status_code == 201
    data = res.get_json()
    links = {link["access_level"]: link["short_key"] for link in data["share_links"]}
    return data, links


def _create_player(client, short_key, group_id, name="Alice"):
    res = client.post(
        f"/api/players?short_key={short_key}",
        json={"group_id": group_id, "name": name},
    )
    assert res.status_code == 201
    return res.get_json()


@pytest.fixture
def setup_group_with_tournament(client):
    """グループ・大会・プレイヤー・共有リンクをセットアップ"""
    group, group_keys = _create_group(client)
    group_link_edit = group_keys["EDIT"]

    # Tournament作成
    tournament, tournament_keys = _create_tournament(client, group_id=group["id"], short_key=group_link_edit)
    tournament_link_edit = tournament_keys["EDIT"]

    # プレイヤーを3人API経由で登録
    players = [
        _create_player(client, group_link_edit, group["id"], "Alice"),
        _create_player(client, group_link_edit, group["id"], "Bob"),
        _create_player(client, group_link_edit, group["id"], "Charlie"),
    ]

    return {
        "group": group,
        "tournament": tournament,
        "players": players,
        "link": group_link_edit,
    }


def test_create_tournament_participant(client, setup_group_with_tournament, db_session):
    """POST /api/tournaments/<id>/participants — プレイヤー登録"""
    data = setup_group_with_tournament
    tournament = data["tournament"]
    players = data["players"]
    link = data["link"]

    url = f"/api/tournaments/{tournament['id']}/participants?short_key={link}"
    res = client.post(url, json={"player_id": players[0]["id"]})
    assert res.status_code == 201

    # ✅ db_sessionで登録確認
    created = db_session.query(TournamentPlayer).filter_by(
        tournament_id=tournament["id"],
        player_id=players[0]["id"]
    ).first()
    assert created is not None


def test_list_tournament_participants(client, setup_group_with_tournament, db_session):
    """GET /api/tournaments/<id>/participants — 参加者一覧取得"""
    data = setup_group_with_tournament
    tournament = data["tournament"]
    players = data["players"]
    link = data["link"]

    # 1人登録
    participant = TournamentPlayer(tournament_id=tournament["id"], player_id=players[0]["id"])
    db_session.add(participant)
    db_session.commit()

    url = f"/api/tournaments/{tournament['id']}/participants?short_key={link}"
    res = client.get(url)
    assert res.status_code == 200

    result = res.get_json()
    assert isinstance(result, list)
    assert any(p["player_id"] == players[0]["id"] for p in result)


def test_delete_tournament_participant(client, setup_group_with_tournament, db_session):
    """DELETE /api/tournaments/<id>/participants/<participant_id> — 削除"""
    data = setup_group_with_tournament
    tournament = data["tournament"]
    players = data["players"]
    link = data["link"]

    # 参加登録（db_session経由）
    participant = TournamentPlayer(tournament_id=tournament["id"], player_id=players[0]["id"])
    db_session.add(participant)
    db_session.commit()

    url = f"/api/tournaments/{tournament['id']}/participants/{participant.id}?short_key={link}"
    res = client.delete(url)
    assert res.status_code == 200
    assert res.get_json()["message"] == "Tournament participant deleted"

    deleted = db_session.get(TournamentPlayer, participant.id)
    assert deleted is None


def test_create_with_invalid_link(client, setup_group_with_tournament):
    """無効な short_key の場合 404"""
    tournament = setup_group_with_tournament["tournament"]
    player = setup_group_with_tournament["players"][0]
    url = f"/api/tournaments/{tournament['id']}/participants?short_key=invalid-key"
    res = client.post(url, json={"player_id": player["id"]})
    assert res.status_code == 404


def test_create_duplicate_participant(client, setup_group_with_tournament, db_session):
    """重複登録は400"""
    data = setup_group_with_tournament
    tournament = data["tournament"]
    player = data["players"][0]
    link = data["link"]

    participant = TournamentPlayer(tournament_id=tournament["id"], player_id=player["id"])
    db_session.add(participant)
    db_session.commit()

    url = f"/api/tournaments/{tournament['id']}/participants?short_key={link}"
    res = client.post(url, json={"player_id": player["id"]})
    assert res.status_code == 400
