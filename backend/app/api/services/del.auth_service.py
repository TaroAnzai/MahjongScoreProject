# app/services/auth_service.py
from flask_login import login_user
from app.models import Group, Tournament
from app.auth import PseudoUser

class AuthService:
    @staticmethod
    def login_by_key(edit_key: str, target: str):
        if target == "group":
            obj = Group.query.filter_by(edit_key=edit_key).first()
        elif target == "tournament":
            obj = Tournament.query.filter_by(edit_key=edit_key).first()
        else:
            return None, {"error": "Invalid type"}, 400

        if not obj:
            return None, {"error": "Invalid edit_key"}, 403

        user = PseudoUser(id=f"{target}:{obj.id}", edit_key=edit_key)
        login_user(user)
        return user, {"message": "Login successful"}, 200

