# app/resources/auth_resource.py
from flask_smorest import Blueprint
from flask import request, jsonify
from flask.views import MethodView
from app.schemas.auth_schema import LoginByKeySchema, MessageSchema
from app.services.auth_service import AuthService

auth_bp = Blueprint("Auth", "auth", url_prefix="/api/auth", description="認証関連 API")

@auth_bp.route("/login/by-key")
class LoginByKeyResource(MethodView):
    @auth_bp.arguments(LoginByKeySchema)
    @auth_bp.response(200, MessageSchema)
    def post(self, data):
        """
        edit_key と type を使って疑似ログインする
        """
        _, response, status = AuthService.login_by_key(
            edit_key=data["edit_key"], target=data["type"]
        )
        return response, status


@auth_bp.route("/ping")
class PingResource(MethodView):
    @auth_bp.response(200, MessageSchema)
    def get(self):
        return {"message": "Pong"}


@auth_bp.route("/debug-session")
class DebugSessionResource(MethodView):
    def get(self):
        from flask import request
        return jsonify({
            "session_cookie": request.cookies.get('mahjong_session'),
            "headers": dict(request.headers)
        })
