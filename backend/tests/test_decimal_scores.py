from decimal import Decimal

import pytest
from app.models import AccessLevel, Score, Table, TableTypeEnum
from app.api.schemas.game_schema import ScoreInputSchema
from marshmallow import ValidationError


@pytest.mark.parametrize("value", [1.123456, "1.5", float("nan"), float("inf"), True, 10000000000])
def test_invalid_score_schema(value):
    with pytest.raises(ValidationError):
        ScoreInputSchema().load({"player_id": 1, "score": value})


@pytest.mark.parametrize("values,accepted", [
    ([100, -100, 0, 0], True),
    ([0.1, 0.2, -0.3, 0], True),
    ([12.34567, -12.34567, 0, 0], True),
    ([0.1, 0.2, -0.29999, 0], False),
    ([1.123456, -1.123456, 0, 0], False),
])
@pytest.mark.parametrize("method", ["post", "put"])
def test_decimal_game_contract(client, db_session, setup_full_tournament, values, accepted, method):
    data = setup_full_tournament(client)
    key = data["table_links"][AccessLevel.EDIT.value]
    url = f"/api/tables/{key}/games"
    if method == "put":
        url += f"/{data['game']['id']}"
    scores = [{"player_id": p["id"], "score": v} for p, v in zip(data["players"], values)]
    response = getattr(client, method)(url, json={"scores": scores})
    if not accepted:
        assert response.status_code in (400, 422)
        return
    assert response.status_code == (201 if method == "post" else 200)
    game = response.get_json()
    if method == "put":
        assert game["id"] == data["game"]["id"]
    fetched = client.get(f"/api/tables/{key}/games/{game['id']}").get_json()
    assert {s["player_id"]: s["score"] for s in fetched["scores"]} == {s["player_id"]: s["score"] for s in scores}
    assert all(type(s["score"]) in (int, float) for s in fetched["scores"])
    stored = db_session.query(Score).filter_by(game_id=game["id"]).all()
    assert {s.player_id: s.score for s in stored} == {s["player_id"]: Decimal(str(s["score"])) for s in scores}


def test_chip_decimal_nonzero(client, db_session, setup_full_tournament):
    data = setup_full_tournament(client)
    table = db_session.get(Table, data["game"]["table_id"])
    table.type = TableTypeEnum.CHIP
    db_session.commit()
    key = data["table_links"][AccessLevel.EDIT.value]
    response = client.post(f"/api/tables/{key}/games", json={"scores": [
        {"player_id": data["players"][0]["id"], "score": 0.00001}]})
    assert response.status_code == 201
    assert response.get_json()["scores"][0]["score"] == 0.00001


def test_openapi_score_remains_number(test_app):
    spec = test_app.extensions["flask-smorest"]["apis"][""]["ext_obj"].spec.to_dict()
    assert spec["components"]["schemas"]["ScoreInput"]["properties"]["score"]["type"] == "number"


@pytest.mark.parametrize("method", ["post", "put"])
@pytest.mark.parametrize("token", ["9999999999.000001", "1.00000000000000001", "NaN", "Infinity", "-Infinity"])
def test_raw_json_invalid_score_keeps_existing_data(client, db_session, setup_full_tournament, method, token):
    data = setup_full_tournament(client)
    key = data["table_links"][AccessLevel.EDIT.value]
    game_id = data["game"]["id"]
    url = f"/api/tables/{key}/games"
    if method == "put":
        url += f"/{game_id}"
    before = [(s.id, s.game_id, s.player_id, s.score) for s in db_session.query(Score).order_by(Score.id)]
    pid = data["players"][0]["id"]
    payload = '{"scores":[{"player_id":%d,"score":%s}]}' % (pid, token)
    response = getattr(client, method)(url, data=payload, content_type="application/json")
    assert response.status_code == 422
    db_session.expire_all()
    assert [(s.id, s.game_id, s.player_id, s.score) for s in db_session.query(Score).order_by(Score.id)] == before
