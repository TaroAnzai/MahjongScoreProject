# app/__init__.py

from flask import Flask, jsonify
from flask_smorest import Api
from flask_cors import CORS
from app.extensions import db, login_manager, migrate
from app.api import register_blueprints

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

    api=Api(app)

    register_blueprints(api)

    return app
