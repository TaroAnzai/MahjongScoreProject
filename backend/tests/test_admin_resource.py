import pytest
from werkzeug.security import generate_password_hash
from app.models import Group

# ==== 管理者ログイン情報（グローバル変数） ====
ADMIN_TEST_USER = "admin"
ADMIN_TEST_PASSWORD = "testpassword"


# ============================================================
# すべてのテストで管理者ログイン状態にする共通 fixture
# ============================================================
@pytest.fixture()
def admin_logged_in(client, monkeypatch):
    """
    管理者ログインを行い、Cookie セッション付きの client を返す。
    """
    # --- ログイン ---
    res = client.post(
        "/api/admin/login",
        json={"username": ADMIN_TEST_USER, "password": ADMIN_TEST_PASSWORD},
    )

    assert res.status_code == 200
    return client   # ← ログイン済み client を返す


# -------------------------------------------------
# すべてのグループ取得（GET /api/admin/groups）
# -------------------------------------------------
def test_get_all_groups(admin_logged_in, create_group):
    client = admin_logged_in

    # --- テストデータ準備 ---
    group_data, _ = create_group(name="管理者テストグループ")

    # --- API呼び出し ---
    res = client.get("/api/admin/groups")
    assert res.status_code == 200

    data = res.get_json()
    assert isinstance(data, list)
    assert any(g["name"] == "管理者テストグループ" for g in data)


# -------------------------------------------------
# 認証エラー（ログインなし）
# -------------------------------------------------
def test_get_all_groups_without_login(client, create_group):
    create_group(name="未ログイングループ")

    # ログインしていない client で呼ぶ
    res = client.get("/api/admin/groups")
    assert res.status_code in (401, 403)


# -------------------------------------------------
# グループ削除（DELETE /api/admin/groups/<group_key>）
# -------------------------------------------------
def test_delete_group(admin_logged_in, setup_full_tournament, db_session):
    client = admin_logged_in

    # --- 前提データ作成 ---
    data = setup_full_tournament(client)
    group_key = data["group_links"]["OWNER"]
    group_id = data["group_data"]["id"]

    # --- 削除実行 ---
    res = client.delete(f"/api/admin/groups/{group_key}")
    assert res.status_code == 200
    assert "削除しました" in res.get_json()["message"]

    #--- DBから確認 ---
    deleted = Group.query.filter_by(id=group_id).first()
    assert deleted is None


# -------------------------------------------------
# 存在しないグループ削除
# -------------------------------------------------
def test_delete_group_not_found(admin_logged_in):
    client = admin_logged_in

    res = client.delete("/api/admin/groups/XXXXXXX")
    assert res.status_code == 404
    body = res.get_json()
    assert "共有リンクが無効です。" in body["errors"]["json"]["message"]
