import pytest
from app.models import TablePlayer


@pytest.fixture
def setup_table_with_participants(client):
    """グループ→大会→卓→プレイヤー→大会参加者までを登録"""
    # --- グループ作成 ---
    group_res = client.post("/api/groups", json={"name": "GroupA"})
    assert group_res.status_code == 201
    group = group_res.get_json()
    group_key = next(
        l["short_key"]
        for l in group["group_links"]
        if l["access_level"] == "EDIT"
    )

    # --- 大会作成 ---
    tournament_res = client.post(
        f"/api/groups/{group_key}/tournaments",
        json={"name": "T1"},
    )
    assert tournament_res.status_code == 201
    tournament = tournament_res.get_json()
    tournament_key = next(
        l["short_key"]
        for l in tournament["tournament_links"]
        if l["access_level"] == "EDIT"
    )

    # --- プレイヤー作成 ---
    player_res = client.post(
        f"/api/groups/{group_key}/players",
        json={"name": "Alice"},
    )
    assert player_res.status_code == 201
    player = player_res.get_json()

    # --- 大会参加者登録 ---
    participant_res = client.post(
        f"/api/tournaments/{tournament_key}/participants",
        json={'participants':[{"player_id": player["id"]}]},
    )
    assert participant_res.status_code == 201
    participants = participant_res.get_json()

    # --- 卓作成 ---
    table_res = client.post(
        f"/api/tournaments/{tournament_key}/tables",
        json={"name": "Table1"},
    )
    assert table_res.status_code == 201
    table = table_res.get_json()
    table_key = next(
        l["short_key"]
        for l in table["table_links"]
        if l["access_level"] == "EDIT"
    )

    return {
        "group": group,
        "group_key": group_key,
        "tournament": tournament,
        "tournament_key": tournament_key,
        "table": table,
        "table_key": table_key,
        "participants": participants['participants'],
    }


# ---------------- テストケース ----------------

def test_create_table_player(client, db_session, setup_table_with_participants):
    """POST /api/tables/<table_key>/players — 卓参加者登録"""
    data = setup_table_with_participants
    table_key = data["table_key"]
    participant = data["participants"][0]

    url = f"/api/tables/{table_key}/players"
    res = client.post(
        url,
        json={"player_id": participant["player_id"], "seat_position": 1},
    )
    print("participant:", participant)
    print(res.get_json())
    assert res.status_code == 201

    created = db_session.query(TablePlayer).filter_by(
        table_id=data["table"]["id"], player_id=participant["player_id"]
    ).first()
    assert created is not None


def test_list_table_players(client, db_session, setup_table_with_participants):
    """GET /api/tables/<table_key>/players — 卓参加者一覧"""
    data = setup_table_with_participants
    table_key = data["table_key"]
    participant = data["participants"][0]

    db_session.add(
        TablePlayer(
            table_id=data["table"]["id"],
            player_id=participant["player_id"],
            seat_position=2,
        )
    )
    db_session.commit()

    url = f"/api/tables/{table_key}/players"
    res = client.get(url)
    assert res.status_code == 200

    result = res.get_json()
    assert isinstance(result, list)
    assert any(p["player_id"] == participant["player_id"] for p in result)


def test_delete_table_player(client, db_session, setup_table_with_participants):
    """DELETE /api/tables/<table_key>/players/<player_id> — 卓参加者削除"""
    data = setup_table_with_participants
    table_key = data["table_key"]
    participant = data["participants"][0]

    table_player = TablePlayer(
        table_id=data["table"]["id"], player_id=participant["player_id"]
    )
    db_session.add(table_player)
    db_session.commit()

    url = f"/api/tables/{table_key}/players/{table_player.player_id}"
    res = client.delete(url)
    assert res.status_code == 200
    assert res.get_json()["message"] == "Table player deleted"

    deleted = db_session.get(TablePlayer, table_player.id)
    assert deleted is None
