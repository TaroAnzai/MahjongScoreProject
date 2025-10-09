# app/api/__init__.py
from app.extensions import api
from app.resources.tournament_resource import tournament_bp
from app.resources.group_resource import group_bp
from app.resources.player_resource import player_bp
from app.resources.table_resource import table_bp
from app.resources.game_resource import game_bp
from app.resources.tournament_participant_resource import tournament_participant_bp
from app.resources.table_player_resource import table_player_bp

def register_blueprints(app):
    api.register_blueprint(tournament_bp)
    api.register_blueprint(group_bp)
    api.register_blueprint(player_bp)
    api.register_blueprint(table_bp)
    api.register_blueprint(game_bp)
    api.register_blueprint(tournament_participant_bp)
    api.register_blueprint(table_player_bp)
