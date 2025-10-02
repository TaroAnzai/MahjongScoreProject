# app/api/__init__.py

from app.resources.tournament_resource import tournament_bp
from app.resources.group_resource import group_bp
from app.resources.player_resource import player_bp
from app.resources.table_resource import table_bp
from app.resources.game_resource import game_bp
from app.resources.auth_resource import auth_bp

def register_blueprints(app):
    app.register_blueprint(tournament_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(table_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(auth_bp) 
