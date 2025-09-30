# app/resources/tournament_resource.py
from flask_smorest import Blueprint, abort
from flask_login import login_required

from app.schemas.tournament_schema import TournamentSchema, TournamentCreateSchema
from app.services import tournament_service

blp = Blueprint("Tournaments", "tournaments", url_prefix="/api/tournaments",
                description="Tournament related operations")


@blp.route("/")
class TournamentListResource:

    @login_required
    @blp.response(200, TournamentSchema(many=True))
    def get(self):
        """Get all tournaments"""
        return tournament_service.get_all_tournaments()

    @login_required
    @blp.arguments(TournamentCreateSchema)
    @blp.response(201, TournamentSchema)
    def post(self, new_data):
        """Create a new tournament"""
        return tournament_service.create_tournament(new_data)


@blp.route("/<int:tournament_id>")
class TournamentResource:

    @login_required
    @blp.response(200, TournamentSchema)
    def get(self, tournament_id):
        """Get tournament by ID"""
        return tournament_service.get_tournament_by_id(tournament_id)

    @login_required
    @blp.response(204)
    def delete(self, tournament_id):
        """Delete tournament"""
        tournament_service.delete_tournament(tournament_id)
        return None
