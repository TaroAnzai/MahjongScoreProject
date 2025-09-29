# app/api/__init__.py

from .tournament_api import tournament_bp
from .group_api import group_bp
from .player_api import player_bp
from .table_api import table_bp
from .game_api import game_bp
from .export_api import export_bp
from .auth_api import auth_api  # ★追加

def register_blueprints(app):
    app.register_blueprint(tournament_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(table_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(auth_api)  # ★追加
