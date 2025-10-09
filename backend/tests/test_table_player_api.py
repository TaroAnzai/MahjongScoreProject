# tests/test_table_player_api.py
import pytest
from app.models import TablePlayer


@pytest.fixture
def setup_table_with_participants(client):
    """グループ→大会→卓→プレイヤー→大会参加者までを登録"""
    # グループ作成
    group_res = client.post("/api/groups", json={"name": "GroupA"})
    group = group_res.get_json()
    group_key = next(l["short_key"] for l in group["share_links"] if l["access_level"] == "EDIT")

    # 大会作成
    tournament_res = client.post(f"/api/tournaments?short_key={group_key}", json={"group_id": group["id"], "name": "T1"})
    tournament = tournament_res.get_json()
    tournament_key = next(l["short_key"] for l in tournament["share_links"] if l["access_level"] == "EDIT")

    # プレイヤー作成
    player_res = client.post(f"/api/players?short_key={group_key}", json={"group_id": group["id"], "name": "Alice"})
    player = player_res.get_json()

    # 大会参加者登録
    participant_res = client.post(f"/api/tournaments/{tournament['id']}/participants?short_key={tournament_key}", json={"player_id": player["id"]})
    participant = participant_res.get_json()

    # 卓作成
    table_res = client.post(f"/api/tables?short_key={tournament_key}", json={"tournament_id": tournament["id"], "name": "Table1"})
    table = table_res.get_json()
    table_key = next(l["short_key"] for l in table["share_links"] if l["access_level"] == "EDIT")

    return {
        "group": group,
        "group_key": group_key,
        "tournament": tournament,
        "tournament_key": tournament_key,
        "table": table,
        "table_key": table_key,
        "participant": participant,
    }


def test_create_table_player(client, db_session, setup_table_with_participants):
    """POST /api/tables/<id>/players — 卓参加者登録"""
    data = setup_table_with_participants
    table = data["table"]
    table_key = data["table_key"]
    participant = data["participant"]

    url = f"/api/tables/{table['id']}/players?short_key={table_key}"
    res = client.post(url, json={"player_id": participant["id"], "seat_position": 1})
    print(res.get_json())
    assert res.status_code == 201

    created = db_session.query(TablePlayer).filter_by(table_id=table["id"]).first()
    assert created is not None


def test_list_table_players(client, db_session, setup_table_with_participants):
    """GET /api/tables/<id>/players — 卓参加者一覧"""
    data = setup_table_with_participants
    table = data["table"]
    table_key = data["table_key"]
    participant = data["participant"]

    db_session.add(TablePlayer(table_id=table["id"], player_id=participant["id"]))
    db_session.commit()

    url = f"/api/tables/{table['id']}/players?short_key={table_key}"
    res = client.get(url)
    assert res.status_code == 200

    result = res.get_json()
    assert isinstance(result, list)
    assert any(p["player_id"] == participant["id"] for p in result)


def test_delete_table_player(client, db_session, setup_table_with_participants):
    """DELETE /api/tables/<id>/players/<id> — 卓参加者削除"""
    data = setup_table_with_participants
    table = data["table"]
    table_key = data["table_key"]
    participant = data["participant"]

    table_player = TablePlayer(table_id=table["id"], player_id=participant["id"])
    db_session.add(table_player)
    db_session.commit()

    url = f"/api/tables/{table['id']}/players/{table_player.id}?short_key={table_key}"
    res = client.delete(url)
    assert res.status_code == 200
    assert res.get_json()["message"] == "Table player deleted"

    deleted = db_session.get(TablePlayer, table_player.id)
    assert deleted is None
