# app/__init__.py

from flask import Flask, jsonify

from flask_cors import CORS
from app.extensions import db, login_manager, migrate, api


def create_app(config_name=None, config_override=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    print(f"Loading config OPENAPI_URL_PREFIX: {app.config.get('OPENAPI_URL_PREFIX')}")

    # ✅ テストなどでconfig_nameが指定された場合に対応
    if config_name == "testing":
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
    if config_override:
        app.config.update(config_override)

    CORS(app,
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
        origins=app.config.get("CORS_ORIGINS", []))

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    api.init_app(app)

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
