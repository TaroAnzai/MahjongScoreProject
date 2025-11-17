import pytest
from werkzeug.security import generate_password_hash
import os

TEST_PASSWORD="testpassword"
# ------------------------------------------------------
# 1. ログイン成功テスト
# ------------------------------------------------------
def test_admin_login_success(client, monkeypatch):

    # --- 実行 ---
    response = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": TEST_PASSWORD},
    )

    assert response.status_code == 200
    assert response.json["message"] == "ok"

    # セッションCookieが返ってくるか？
    assert "session=" in response.headers.get("Set-Cookie", "")


# ------------------------------------------------------
# 2. ログイン失敗（パスワード誤り）
# ------------------------------------------------------
def test_admin_login_wrong_password(client, monkeypatch):

    response = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401


# ------------------------------------------------------
# 3. ログイン失敗（ユーザー名誤り）
# ------------------------------------------------------
def test_admin_login_wrong_username(client, monkeypatch):

    response = client.post(
        "/api/admin/login",
        json={"username": "root", "password": TEST_PASSWORD},
    )

    assert response.status_code == 401


# ------------------------------------------------------
# 4. ログイン後の /admin/me
# ------------------------------------------------------
def test_admin_me_after_login(client, monkeypatch):

    # ログイン
    client.post(
        "/api/admin/login",
        json={"username": "admin", "password": TEST_PASSWORD},
    )

    # me を確認
    response = client.get("/api/admin/me")

    assert response.status_code == 200
    assert response.json["is_admin"] is True


# ------------------------------------------------------
# 5. ログアウト成功
# ------------------------------------------------------
def test_admin_logout_success(client, monkeypatch):

    # ログイン
    client.post(
        "/api/admin/login",
        json={"username": "admin", "password": TEST_PASSWORD},
    )

    # ログアウト
    response = client.post("/api/admin/logout")

    assert response.status_code == 200
    assert response.json["message"] == "logged_out"


# ------------------------------------------------------
# 6. ログアウト後の /admin/me
# ------------------------------------------------------
def test_admin_me_after_logout(client, monkeypatch):

    # ログイン
    client.post(
        "/api/admin/login",
        json={"username": "admin", "password": TEST_PASSWORD},
    )

    # ログアウト
    client.post("/api/admin/logout")

    # me が False を返す
    response = client.get("/api/admin/me")
    assert response.status_code == 200
    assert response.json["is_admin"] is False
