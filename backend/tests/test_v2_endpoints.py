from datetime import datetime, timedelta, timezone

import pytest

from app.models import (
    AccessLevel, Game, Group, GroupCreationToken, Player, Score, ShareLink,
    Table, TablePlayer, TableTypeEnum, Tournament, TournamentPlayer,
)


def add_links(db_session, resource_type, resource_id, prefix):
    links = {}
    for level in (AccessLevel.OWNER, AccessLevel.EDIT, AccessLevel.VIEW):
        link = ShareLink(
            short_key=f"{prefix}-{level.value.lower()}", resource_type=resource_type,
            resource_id=resource_id, access_level=level, created_by="test",
        )
        db_session.add(link)
        links[level.value] = link.short_key
    db_session.commit()
    return links


@pytest.fixture
def v2_group(db_session):
    group = Group(name="麻雀仲間", description=None, created_by="test")
    db_session.add(group)
    db_session.flush()
    links = add_links(db_session, "group", group.id, "group")
    return group, links


def create_tournament(client, group_key, payload=None, headers=None):
    return client.post(
        f"/api/v2/groups/{group_key}/tournaments",
        json=payload or {"name": "大会"}, headers=headers or {},
    )


def test_create_tournament_with_initial_tables_is_atomic_and_idempotent(client, db_session, v2_group):
    group, links = v2_group
    payload = {
        "name": "2026年8月大会", "description": None, "rate": 50,
        "initial_tables": [{"client_id": "chip", "name": "チップ", "type": "CHIP"}],
    }
    headers = {"Idempotency-Key": "create-1"}
    first = create_tournament(client, links["EDIT"], payload, headers)
    second = create_tournament(client, links["EDIT"], payload, headers)

    assert first.status_code == second.status_code == 201
    assert first.get_json() == second.get_json()
    body = first.get_json()
    assert body["created_tables"][0]["client_id"] == "chip"
    assert body["created_tables"][0]["table"]["type"] == "CHIP"
    assert body["tournament"]["owner_link"]
    assert Tournament.query.filter_by(group_id=group.id).count() == 1
    assert Table.query.count() == 1

    conflict = create_tournament(client, links["EDIT"], {"name": "別大会"}, headers)
    assert conflict.status_code == 409
    assert conflict.get_json()["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_create_tournament_rolls_back_everything_on_invalid_table(client, db_session, v2_group):
    _, links = v2_group
    response = create_tournament(client, links["EDIT"], {
        "name": "rollback", "initial_tables": [
            {"client_id": "ok", "name": "卓", "type": "NORMAL"},
            {"client_id": "bad", "name": "不正", "type": "UNKNOWN"},
        ],
    })
    assert response.status_code == 422
    assert Tournament.query.count() == 0
    assert Table.query.count() == 0
    assert ShareLink.query.filter_by(resource_type="tournament").count() == 0


def test_omitting_initial_tables_preserves_single_create_behavior(client, db_session, v2_group):
    _, links = v2_group
    response = create_tournament(client, links["EDIT"], {"name": "従来相当"})
    assert response.status_code == 201
    assert response.get_json()["created_tables"] == []
    assert Tournament.query.count() == 1
    assert Table.query.count() == 0


@pytest.fixture
def v2_tournament(db_session, v2_group):
    group, group_links = v2_group
    players = [Player(group_id=group.id, name=name) for name in ("田中", "鈴木", "佐藤")]
    db_session.add_all(players)
    tournament = Tournament(group_id=group.id, name="大会", rate=50, created_by="test")
    db_session.add(tournament)
    db_session.flush()
    tournament_links = add_links(db_session, "tournament", tournament.id, "tournament")
    chip = Table(tournament_id=tournament.id, name="チップ", type=TableTypeEnum.CHIP, created_by="test")
    normal = Table(tournament_id=tournament.id, name="1卓", type=TableTypeEnum.NORMAL, created_by="test")
    db_session.add_all([chip, normal])
    db_session.flush()
    chip_links = add_links(db_session, "table", chip.id, "chip")
    normal_links = add_links(db_session, "table", normal.id, "normal")
    return group, group_links, tournament, tournament_links, chip, chip_links, normal, normal_links, players


def test_batch_add_is_idempotent_and_propagates_only_to_chip(client, db_session, v2_tournament):
    tournament_links = v2_tournament[3]
    chip, normal = v2_tournament[4], v2_tournament[6]
    players = v2_tournament[-1]
    payload = {
        "participants": [{"player_id": players[0].id}, {"player_id": players[1].id}],
        "propagate_to": {"table_types": ["CHIP"]},
    }
    url = f"/api/v2/tournaments/{tournament_links['EDIT']}/participants:batch-add"
    first = client.post(url, json=payload)
    second = client.post(url, json=payload)
    assert first.status_code == second.status_code == 200
    assert first.get_json()["added_count"] == 2
    assert second.get_json()["added_count"] == 0
    assert second.get_json()["already_registered_count"] == 2
    assert TablePlayer.query.filter_by(table_id=chip.id).count() == 2
    assert TablePlayer.query.filter_by(table_id=normal.id).count() == 0


def test_batch_add_invalid_player_rolls_back(client, db_session, v2_tournament):
    tournament_links = v2_tournament[3]
    player = v2_tournament[-1][0]
    response = client.post(
        f"/api/v2/tournaments/{tournament_links['EDIT']}/participants:batch-add",
        json={"participants": [{"player_id": player.id}, {"player_id": 999999}]},
    )
    assert response.status_code == 400
    assert TournamentPlayer.query.count() == 0
    assert TablePlayer.query.count() == 0


def test_delete_participant_conflicts_when_chip_score_exists(client, db_session, v2_tournament):
    tournament = v2_tournament[2]
    tournament_links = v2_tournament[3]
    chip = v2_tournament[4]
    player = v2_tournament[-1][0]
    db_session.add(TournamentPlayer(tournament_id=tournament.id, player_id=player.id))
    db_session.add(TablePlayer(table_id=chip.id, player_id=player.id))
    game = Game(table_id=chip.id, game_index=1, created_by="test")
    db_session.add(game)
    db_session.flush()
    db_session.add(Score(game_id=game.id, player_id=player.id, score=100))
    db_session.commit()

    response = client.delete(
        f"/api/v2/tournaments/{tournament_links['EDIT']}/participants/{player.id}?propagate_to=CHIP"
    )
    assert response.status_code == 409
    assert response.get_json() == {
        "code": "PARTICIPANT_HAS_SCORES",
        "message": "Participant has scores in one or more chip tables",
        "details": {"table_ids": [chip.id]},
    }
    assert TournamentPlayer.query.count() == 1
    assert TablePlayer.query.count() == 1


def test_cascade_delete_table_reports_and_removes_children(client, db_session, v2_tournament):
    chip, chip_links, player = v2_tournament[4], v2_tournament[5], v2_tournament[-1][0]
    db_session.add(TablePlayer(table_id=chip.id, player_id=player.id))
    game = Game(table_id=chip.id, game_index=1, created_by="test")
    db_session.add(game)
    db_session.flush()
    db_session.add(Score(game_id=game.id, player_id=player.id, score=20))
    db_session.commit()

    response = client.delete(
        f"/api/v2/tables/{chip_links['EDIT']}", headers={"Idempotency-Key": "delete-chip"}
    )
    replay = client.delete(
        f"/api/v2/tables/{chip_links['EDIT']}", headers={"Idempotency-Key": "delete-chip"}
    )
    assert response.status_code == replay.status_code == 200
    assert response.get_json()["deleted"] == {
        "table_id": chip.id, "game_count": 1, "score_count": 1, "participant_count": 1,
    }
    assert db_session.get(Table, chip.id) is None
    assert Game.query.count() == Score.query.count() == TablePlayer.query.count() == 0


def test_batch_get_groups_is_partial_and_does_not_echo_keys(client, v2_group):
    _, links = v2_group
    response = client.post("/api/v2/groups:batch-get", json={"items": [
        {"client_id": "local-0", "group_key": links["VIEW"]},
        {"client_id": "local-1", "group_key": "missing"},
    ]})
    assert response.status_code == 200
    body = response.get_json()
    assert [item["status"] for item in body["results"]] == ["ok", "not_found"]
    assert all("group_key" not in item for item in body["results"])


def test_dashboards_return_available_players_and_games(client, db_session, v2_tournament):
    group_links, tournament, tournament_links = v2_tournament[1], v2_tournament[2], v2_tournament[3]
    normal, normal_links, players = v2_tournament[6], v2_tournament[7], v2_tournament[-1]
    db_session.add_all([
        TournamentPlayer(tournament_id=tournament.id, player_id=players[0].id),
        TournamentPlayer(tournament_id=tournament.id, player_id=players[1].id),
        TablePlayer(table_id=normal.id, player_id=players[0].id),
    ])
    game = Game(table_id=normal.id, game_index=1, created_by="test")
    db_session.add(game)
    db_session.flush()
    db_session.add(Score(game_id=game.id, player_id=players[0].id, score=100))
    db_session.commit()

    group_body = client.get(f"/api/v2/groups/{group_links['VIEW']}/dashboard").get_json()
    tournament_body = client.get(f"/api/v2/tournaments/{tournament_links['VIEW']}/dashboard").get_json()
    table_body = client.get(f"/api/v2/tables/{normal_links['VIEW']}/dashboard").get_json()
    assert len(group_body["tournaments"]) == 1 and len(group_body["players"]) == 3
    assert [p["id"] for p in tournament_body["available_group_players"]] == [players[2].id]
    assert tournament_body["score_map"]["players"][0]["total"] == 100
    assert [p["id"] for p in table_body["available_tournament_players"]] == [players[1].id]
    assert table_body["games"][0]["scores"][0]["score"] == 100


def test_batch_group_creation_status_enum(client, db_session, v2_group):
    group, links = v2_group
    now = datetime.now(timezone.utc)
    records = [
        GroupCreationToken(email="a@x.test", group_name="a", token="pending", expires_at=now + timedelta(hours=1), is_used=False),
        GroupCreationToken(email="b@x.test", group_name="b", token="ready", expires_at=now + timedelta(hours=1), is_used=True, group_id=group.id),
        GroupCreationToken(email="c@x.test", group_name="c", token="expired", expires_at=now - timedelta(hours=1), is_used=False),
    ]
    db_session.add_all(records)
    db_session.commit()
    response = client.post("/api/v2/groups/request-link/status:batch", json={"items": [
        {"client_id": "0", "token": "pending"}, {"client_id": "1", "token": "ready"},
        {"client_id": "2", "token": "expired"}, {"client_id": "3", "token": "unknown"},
    ]})
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert [item["status"] for item in results] == ["pending", "ready", "expired", "invalid_token"]
    assert results[1]["owner_link"] == links["OWNER"]
