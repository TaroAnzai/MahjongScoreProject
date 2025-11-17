# app/services/admin_auth_service.py
import os
from werkzeug.security import check_password_hash
from flask import session

class AdminAuthError(Exception):
    """管理者認証エラー"""
    pass


def admin_login(username: str, password: str):
    """管理者ログイン処理"""

    admin_user_env = os.getenv("ADMIN_USER")
    admin_password_hash_env = os.getenv("ADMIN_PASSWORD_HASH")

    if not admin_user_env or not admin_password_hash_env:
        raise AdminAuthError("管理者認証が正しく設定されていません")

    # --- ユーザー名チェック ---
    if username != admin_user_env:
        raise AdminAuthError("ユーザー名またはパスワードが違います")

    # --- パスワード照合 ---
    if not check_password_hash(admin_password_hash_env, password):
        raise AdminAuthError("ユーザー名またはパスワードが違います")

    # --- セッション保存（ログイン成功） ---
    session["is_admin"] = True

    return {"message": "ok"}


def admin_logout():
    """管理者ログアウト"""
    session.pop("is_admin", None)
    return {"message": "logged_out"}
