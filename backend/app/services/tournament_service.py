# app/services/tournament_service.py
from app import db
from app.models import Tournament


def get_all_tournaments():
    return Tournament.query.all()


def get_tournament_by_id(tournament_id: int):
    return Tournament.query.get_or_404(tournament_id)


def create_tournament(data: dict):
    tournament = Tournament(**data)
    db.session.add(tournament)
    db.session.commit()
    return tournament


def delete_tournament(tournament_id: int):
    tournament = Tournament.query.get_or_404(tournament_id)
    db.session.delete(tournament)
    db.session.commit()
    return tournament
