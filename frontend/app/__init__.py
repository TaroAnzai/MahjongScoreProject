# app/__init__.py

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth_api.login_by_key'

def create_app(config_override=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    # ✅ テストなど外部から渡された設定で上書き
    if config_override:
        app.config.update(config_override)
    CORS(app,
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
        origins=app.config.get("CORS_ORIGINS", []))

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # モデルと認証ユーザーの読み込み
    from app import models
    from app.auth import PseudoUser

    @login_manager.user_loader
    def load_user(user_id):
        return PseudoUser(user_id, edit_key=None)

    from app.api import register_blueprints
    register_blueprints(app)

    return app

@login_manager.unauthorized_handler
def unauthorized_callback():
    return jsonify({'error': 'Unauthorized'}), 401
