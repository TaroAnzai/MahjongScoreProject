"""Transactional and aggregate services for the V2 mobile API."""

import hashlib
import json
from datetime import datetime, timezone

from app import db
from app.models import (
    AccessLevel,
    Game,
    Group,
    GroupCreationToken,
    IdempotencyRecord,
    Player,
    Score,
    ShareLink,
    Table,
    TablePlayer,
    TableTypeEnum,
    Tournament,
    TournamentPlayer,
)
from app.utils.share_link_utils import create_unique_share_link, get_share_link_by_key

ACCESS_PRIORITY = {AccessLevel.VIEW: 1, AccessLevel.EDIT: 2, AccessLevel.OWNER: 3}


class V2Error(Exception):
    def __init__(self, status, code, message, details=None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def _require(key, resource_type, model, access=AccessLevel.VIEW):
    link = get_share_link_by_key(key)
    if not link or link.resource_type != resource_type:
        raise V2Error(404, "RESOURCE_NOT_FOUND", "Resource was not found")
    if ACCESS_PRIORITY[link.access_level] < ACCESS_PRIORITY[access]:
        raise V2Error(403, "FORBIDDEN", "Insufficient access")
    resource = db.session.get(model, link.resource_id)
    if not resource:
        raise V2Error(404, "RESOURCE_NOT_FOUND", "Resource was not found")
    return link, resource


def _links(resource_type, resource_id, created_by):
    result = {}
    for level in (AccessLevel.OWNER, AccessLevel.EDIT, AccessLevel.VIEW):
        result[level.value.lower() + "_link"] = create_unique_share_link(
            resource_type, resource_id, created_by, level
        ).short_key
    return result


def _resource_links(resource_type, resource_id, access_level=None):
    links = (
        ShareLink.query.filter_by(resource_type=resource_type, resource_id=resource_id)
        .order_by(ShareLink.id)
        .all()
    )
    if access_level is not None:
        links = [
            link
            for link in links
            if (ACCESS_PRIORITY[link.access_level] <= ACCESS_PRIORITY[access_level])
        ]
    return [
        {"short_key": link.short_key, "access_level": link.access_level.value}
        for link in links
    ]


def _player(player):
    return {"id": player.id, "group_id": player.group_id, "name": player.name}


def _rfc3339(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _table(table, access_level):
    return {
        "id": table.id,
        "tournament_id": table.tournament_id,
        "name": table.name,
        "type": table.type.value,
        "created_at": table.created_at.isoformat() if table.created_at else None,
        "table_links": _resource_links("table", table.id, access_level),
    }


def _tournament(tournament, access_level):
    return {
        "id": tournament.id,
        "group_id": tournament.group_id,
        "name": tournament.name,
        "description": tournament.description,
        "rate": tournament.rate,
        "started_at": tournament.started_at.isoformat()
        if tournament.started_at
        else None,
        "created_at": tournament.created_at.isoformat()
        if tournament.created_at
        else None,
        "tournament_links": _resource_links("tournament", tournament.id, access_level),
    }


def _group(group, access_level):
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": _rfc3339(group.created_at),
        "group_links": _resource_links("group", group.id, access_level),
    }


def _hash(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _replay(scope, key, payload):
    if key and len(key) > 255:
        raise V2Error(
            400, "VALIDATION_ERROR", "Idempotency-Key must be at most 255 characters"
        )
    if not key:
        return None
    record = IdempotencyRecord.query.filter_by(scope=scope, idempotency_key=key).first()
    if not record:
        return None
    if record.request_hash != _hash(payload):
        raise V2Error(
            409,
            "IDEMPOTENCY_KEY_REUSED",
            "Idempotency-Key was used with a different request",
        )
    return record.response_body, record.status_code


def _remember(scope, key, payload, body, status):
    if key and len(key) > 255:
        raise V2Error(
            400, "VALIDATION_ERROR", "Idempotency-Key must be at most 255 characters"
        )
    if key:
        db.session.add(
            IdempotencyRecord(
                scope=scope,
                idempotency_key=key,
                request_hash=_hash(payload),
                response_body=body,
                status_code=status,
            )
        )


def create_tournament_with_tables(group_key, payload, idempotency_key=None):
    scope = f"create-tournament:{group_key}"
    replay = _replay(scope, idempotency_key, payload)
    if replay:
        return replay
    link, group = _require(group_key, "group", Group, AccessLevel.EDIT)
    if not payload.get("name"):
        raise V2Error(400, "VALIDATION_ERROR", "name is required")
    initial_tables = payload.get("initial_tables", [])
    client_ids = [item.get("client_id") for item in initial_tables]
    if any(not item.get("name") for item in initial_tables) or len(client_ids) != len(
        set(client_ids)
    ):
        raise V2Error(
            400,
            "VALIDATION_ERROR",
            "Initial table names and unique client_id values are required",
        )
    try:
        tournament = Tournament(
            group_id=group.id,
            name=payload["name"],
            description=payload.get("description"),
            rate=payload.get("rate", 1.0),
            created_by=group.created_by,
            started_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(tournament)
        db.session.flush()
        _links("tournament", tournament.id, tournament.created_by)
        created = []
        for item in initial_tables:
            try:
                table_type = TableTypeEnum(item.get("type", "NORMAL"))
            except ValueError as exc:
                raise V2Error(
                    400, "VALIDATION_ERROR", "type must be NORMAL or CHIP"
                ) from exc
            table = Table(
                tournament_id=tournament.id,
                name=item["name"],
                type=table_type,
                created_by=tournament.created_by,
                created_at=datetime.now(timezone.utc),
            )
            db.session.add(table)
            db.session.flush()
            _links("table", table.id, table.created_by)
            db.session.flush()
            created.append(
                {
                    "client_id": item["client_id"],
                    "table": _table(table, link.access_level),
                }
            )
        db.session.flush()
        body = {
            "tournament": _tournament(tournament, link.access_level),
            "created_tables": created,
        }
        _remember(scope, idempotency_key, payload, body, 201)
        db.session.commit()
        return body, 201
    except Exception:
        db.session.rollback()
        raise


def batch_add_participants(tournament_key, payload, idempotency_key=None):
    scope = f"batch-add-participants:{tournament_key}"
    replay = _replay(scope, idempotency_key, payload)
    if replay:
        return replay
    _, tournament = _require(tournament_key, "tournament", Tournament, AccessLevel.EDIT)
    items = payload.get("participants", [])
    ids = [item.get("player_id") for item in items]
    if not ids or None in ids or len(ids) != len(set(ids)):
        raise V2Error(
            400, "VALIDATION_ERROR", "participants must contain unique player_id values"
        )
    players = Player.query.filter(Player.id.in_(ids)).all()
    if len(players) != len(ids) or any(
        p.group_id != tournament.group_id for p in players
    ):
        raise V2Error(
            400, "INVALID_PLAYER", "All players must belong to the tournament group"
        )
    existing = {
        row.player_id
        for row in TournamentPlayer.query.filter_by(tournament_id=tournament.id).all()
    }
    added_ids = set(ids) - existing
    try:
        for player_id in added_ids:
            db.session.add(
                TournamentPlayer(tournament_id=tournament.id, player_id=player_id)
            )
        propagated = []
        tables = Table.query.filter_by(tournament_id=tournament.id).all()
        for table in tables:
            if table.type != TableTypeEnum.CHIP:
                continue
            registered = {
                row.player_id
                for row in TablePlayer.query.filter_by(table_id=table.id).all()
            }
            table_added = set(ids) - registered
            for player_id in table_added:
                db.session.add(TablePlayer(table_id=table.id, player_id=player_id))
            propagated.append(
                {
                    "table_id": table.id,
                    "type": table.type.value,
                    "added_count": len(table_added),
                }
            )
        body = {
            "tournament_id": tournament.id,
            "participants": [
                _player(next(p for p in players if p.id == pid)) for pid in ids
            ],
            "added_count": len(added_ids),
            "already_registered_count": len(existing.intersection(ids)),
            "propagated_tables": propagated,
        }
        _remember(scope, idempotency_key, payload, body, 200)
        db.session.commit()
        return body, 200
    except Exception:
        db.session.rollback()
        raise


def delete_participant(tournament_key, player_id, idempotency_key=None):
    payload = {"player_id": player_id}
    scope = f"delete-participant:{tournament_key}:{player_id}"
    replay = _replay(scope, idempotency_key, payload)
    if replay:
        return replay
    _, tournament = _require(tournament_key, "tournament", Tournament, AccessLevel.EDIT)
    participant = TournamentPlayer.query.filter_by(
        tournament_id=tournament.id, player_id=player_id
    ).first()
    if not participant:
        raise V2Error(404, "PARTICIPANT_NOT_FOUND", "Participant was not found")
    tables = Table.query.filter_by(tournament_id=tournament.id).all()
    target_tables = [t for t in tables if t.type == TableTypeEnum.CHIP]
    table_ids = [t.id for t in target_tables]
    scored = []
    if table_ids:
        scored = [
            row[0]
            for row in db.session.query(Game.table_id)
            .join(Score)
            .filter(Game.table_id.in_(table_ids), Score.player_id == player_id)
            .distinct()
            .all()
        ]
    if scored:
        raise V2Error(
            409,
            "PARTICIPANT_HAS_SCORES",
            "Participant has scores in one or more chip tables",
            {"table_ids": scored},
        )
    try:
        if table_ids:
            TablePlayer.query.filter(
                TablePlayer.table_id.in_(table_ids), TablePlayer.player_id == player_id
            ).delete(synchronize_session=False)
        db.session.delete(participant)
        body = {
            "deleted": {
                "tournament_id": tournament.id,
                "player_id": player_id,
                "propagated_table_ids": table_ids,
            }
        }
        _remember(scope, idempotency_key, payload, body, 200)
        db.session.commit()
        return body, 200
    except Exception:
        db.session.rollback()
        raise


def cascade_delete_table(table_key, idempotency_key=None):
    payload = {}
    scope = f"delete-table:{table_key}"
    replay = _replay(scope, idempotency_key, payload)
    if replay:
        return replay
    _, table = _require(table_key, "table", Table, AccessLevel.EDIT)
    game_ids = [
        row[0] for row in db.session.query(Game.id).filter_by(table_id=table.id).all()
    ]
    score_count = (
        Score.query.filter(Score.game_id.in_(game_ids)).count() if game_ids else 0
    )
    game_count = len(game_ids)
    participant_count = TablePlayer.query.filter_by(table_id=table.id).count()
    table_id = table.id
    try:
        if game_ids:
            Score.query.filter(Score.game_id.in_(game_ids)).delete(
                synchronize_session=False
            )
        Game.query.filter_by(table_id=table.id).delete(synchronize_session=False)
        TablePlayer.query.filter_by(table_id=table.id).delete(synchronize_session=False)
        ShareLink.query.filter_by(resource_type="table", resource_id=table.id).delete(
            synchronize_session=False
        )
        db.session.delete(table)
        body = {
            "deleted": {
                "table_id": table_id,
                "game_count": game_count,
                "score_count": score_count,
                "participant_count": participant_count,
            }
        }
        _remember(scope, idempotency_key, payload, body, 200)
        db.session.commit()
        return body, 200
    except Exception:
        db.session.rollback()
        raise


def batch_get_groups(payload):
    items = payload.get("items", [])
    if not isinstance(items, list) or len(items) > 50:
        raise V2Error(400, "VALIDATION_ERROR", "items must contain at most 50 entries")
    keys = [item.get("group_key") for item in items]
    if None in keys or len(keys) != len(set(keys)):
        raise V2Error(
            400, "VALIDATION_ERROR", "group_key values must be present and unique"
        )
    links = {
        link.short_key: link
        for link in ShareLink.query.filter(ShareLink.short_key.in_(keys)).all()
    }
    results = []
    for item in items:
        link = links.get(item["group_key"])
        result = {"client_id": item.get("client_id")}
        if (
            not link
            or link.resource_type != "group"
            or not db.session.get(Group, link.resource_id)
        ):
            result["status"] = "not_found"
        else:
            result.update(
                status="ok",
                group=_group(
                    db.session.get(Group, link.resource_id), link.access_level
                ),
            )
        results.append(result)
    return {"results": results}


def group_dashboard(group_key):
    link, group = _require(group_key, "group", Group)
    tournaments = (
        Tournament.query.filter_by(group_id=group.id)
        .order_by(Tournament.created_at.desc())
        .all()
    )
    return {
        "group": _group(group, link.access_level),
        "tournaments": [_tournament(t, link.access_level) for t in tournaments],
        "players": [
            _player(p) for p in Player.query.filter_by(group_id=group.id).all()
        ],
    }


def _score_map(tournament, access_level):
    tables = Table.query.filter_by(tournament_id=tournament.id).all()
    participants = [
        row.player
        for row in TournamentPlayer.query.filter_by(tournament_id=tournament.id).all()
    ]
    values = {
        p.id: {
            "id": p.id,
            "name": p.name,
            "scores": {},
            "total": 0,
            "converted_total": 0,
        }
        for p in participants
    }
    for table in tables:
        for game in Game.query.filter_by(table_id=table.id).all():
            for score in Score.query.filter_by(game_id=game.id).all():
                if score.player_id in values:
                    scores = values[score.player_id]["scores"]
                    scores[str(table.id)] = scores.get(str(table.id), 0) + score.score
    rate = tournament.rate if tournament.rate is not None else 0.001
    for value in values.values():
        value["total"] = sum(value["scores"].values())
        value["converted_total"] = round(value["total"] * rate, 2)
    return {
        "tournament_id": tournament.id,
        "tables": [_table(t, access_level) for t in tables],
        "players": list(values.values()),
        "rate": rate,
    }


def tournament_dashboard(tournament_key):
    link, tournament = _require(tournament_key, "tournament", Tournament)
    group = db.session.get(Group, tournament.group_id)
    participants = [
        row.player
        for row in TournamentPlayer.query.filter_by(tournament_id=tournament.id).all()
    ]
    participant_ids = {p.id for p in participants}
    available = (
        Player.query.filter(
            Player.group_id == tournament.group_id, ~Player.id.in_(participant_ids)
        ).all()
        if participant_ids
        else Player.query.filter_by(group_id=tournament.group_id).all()
    )
    value = _tournament(tournament, link.access_level)
    return {
        "parent": {"group": {"id": group.id, "name": group.name}},
        "tournament": value,
        "participants": [_player(p) for p in participants],
        "available_group_players": [_player(p) for p in available],
        "tables": [
            _table(t, link.access_level)
            for t in Table.query.filter_by(tournament_id=tournament.id).all()
        ],
        "score_map": _score_map(tournament, link.access_level),
    }


def table_dashboard(table_key):
    link, table = _require(table_key, "table", Table)
    tournament = db.session.get(Tournament, table.tournament_id)
    group = db.session.get(Group, tournament.group_id)
    seated = [
        row.player for row in TablePlayer.query.filter_by(table_id=table.id).all()
    ]
    seated_ids = {p.id for p in seated}
    participant_ids = [
        row.player_id
        for row in TournamentPlayer.query.filter_by(
            tournament_id=table.tournament_id
        ).all()
    ]
    available_ids = [pid for pid in participant_ids if pid not in seated_ids]
    available = (
        Player.query.filter(Player.id.in_(available_ids)).all() if available_ids else []
    )
    games = []
    for game in Game.query.filter_by(table_id=table.id).order_by(Game.game_index).all():
        games.append(
            {
                "id": game.id,
                "table_id": table.id,
                "game_index": game.game_index,
                "memo": game.memo,
                "played_at": game.played_at.isoformat() if game.played_at else None,
                "scores": [
                    {"player_id": s.player_id, "score": s.score}
                    for s in Score.query.filter_by(game_id=game.id).all()
                ],
            }
        )
    return {
        "parent": {
            "tournament": {"id": tournament.id, "name": tournament.name},
            "group": {"id": group.id, "name": group.name},
        },
        "table": _table(table, link.access_level),
        "table_players": [_player(p) for p in seated],
        "available_tournament_players": [_player(p) for p in available],
        "games": games,
    }


def batch_group_status(payload):
    items = payload.get("items", [])
    if not isinstance(items, list) or len(items) > 50:
        raise V2Error(400, "VALIDATION_ERROR", "items must contain at most 50 entries")
    tokens = [item.get("token") for item in items]
    if None in tokens or len(tokens) != len(set(tokens)):
        raise V2Error(
            400, "VALIDATION_ERROR", "token values must be present and unique"
        )
    records = {
        record.token: record
        for record in GroupCreationToken.query.filter(
            GroupCreationToken.token.in_(tokens)
        ).all()
    }
    now = datetime.now(timezone.utc)
    results = []
    for item in items:
        result = {"client_id": item.get("client_id")}
        record = records.get(item["token"])
        if not record:
            result["status"] = "invalid_token"
        else:
            expires = (
                record.expires_at.replace(tzinfo=timezone.utc)
                if record.expires_at.tzinfo is None
                else record.expires_at
            )
            if expires < now:
                result["status"] = "expired"
            elif not record.is_used:
                result["status"] = "pending"
            else:
                owner = ShareLink.query.filter_by(
                    resource_type="group",
                    resource_id=record.group_id,
                    access_level=AccessLevel.OWNER,
                ).first()
                if owner:
                    result.update(status="ready", owner_link=owner.short_key)
                else:
                    result["status"] = "invalid_token"
        results.append(result)
    return {"results": results}
