# app/api/__init__.py

from app.api.resources.tournament_resource import tournament_bp
from app.api.resources.group_resource import group_bp
from app.api.resources.player_resource import player_bp
from app.api.resources.table_resource import table_bp
from app.api.resources.game_resource import game_bp
from app.api.resources.tournament_participant_resource import tournament_participant_bp
from app.api.resources.table_player_resource import table_player_bp
from app.api.resources.export_resource import export_bp
from app.api.resources.admin_resource import admin_group_bp
from app.api.resources.admin_auth_route import admin_auth_bp

def register_blueprints(api):
    api.register_blueprint(tournament_bp)
    api.register_blueprint(group_bp)
    api.register_blueprint(player_bp)
    api.register_blueprint(table_bp)
    api.register_blueprint(game_bp)
    api.register_blueprint(tournament_participant_bp)
    api.register_blueprint(table_player_bp)
    api.register_blueprint(export_bp)
    api.register_blueprint(admin_group_bp)
    api.register_blueprint(admin_auth_bp)
