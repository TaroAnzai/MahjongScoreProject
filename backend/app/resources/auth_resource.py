# app/resources/auth_resource.py
from flask_smorest import Blueprint
from flask import request, jsonify
from app.schemas.auth_schema import LoginByKeySchema, MessageSchema
from app.services.auth_service import AuthService

blp = Blueprint("Auth", "auth", url_prefix="/api", description="認証関連 API")

@blp.route("/login/by-key")
class LoginByKeyResource:
    @blp.arguments(LoginByKeySchema)
    @blp.response(200, MessageSchema)
    def post(self, data):
        """
        edit_key と type を使って疑似ログインする
        """
        _, response, status = AuthService.login_by_key(
            edit_key=data["edit_key"], target=data["type"]
        )
        return response, status


@blp.route("/ping")
class PingResource:
    @blp.response(200, MessageSchema)
    def get(self):
        return {"message": "Pong"}


@blp.route("/debug-session")
class DebugSessionResource:
    def get(self):
        from flask import request
        return jsonify({
            "session_cookie": request.cookies.get('mahjong_session'),
            "headers": dict(request.headers)
        })
