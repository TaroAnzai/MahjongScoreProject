# app/resources/tournament_resource.py
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_login import login_required

from app.schemas.tournament_schema import TournamentSchema, TournamentCreateSchema
from app.services import tournament_service

tournament_bp = Blueprint("Tournaments", "tournaments", url_prefix="/api/tournaments",
                description="Tournament related operations")


@tournament_bp.route("/")
class TournamentListResource(MethodView):

    @login_required
    @tournament_bp.response(200, TournamentSchema(many=True))
    def get(self):
        """Get all tournaments"""
        return tournament_service.get_all_tournaments()

    @login_required
    @tournament_bp.arguments(TournamentCreateSchema)
    @tournament_bp.response(201, TournamentSchema)
    def post(self, new_data):
        """Create a new tournament"""
        return tournament_service.create_tournament(new_data)


@tournament_bp.route("/<int:tournament_id>")
class TournamentResource(MethodView):

    @login_required
    @tournament_bp.response(200, TournamentSchema)
    def get(self, tournament_id):
        """Get tournament by ID"""
        return tournament_service.get_tournament_by_id(tournament_id)

    @login_required
    @tournament_bp.response(204)
    def delete(self, tournament_id):
        """Delete tournament"""
        tournament_service.delete_tournament(tournament_id)
        return None
