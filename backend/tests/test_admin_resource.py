import os
import pytest
from app.models import Group

# -------------------------------------------------
# すべてのグループ取得（GET /admin/groups）
# -------------------------------------------------
def test_get_all_groups(client, create_group):
    # --- テストデータ準備 ---
    group_data, _ = create_group(name="管理者テストグループ")

    # --- API呼び出し ---
    res = client.get(
        "/api/admin/groups",
        headers={"X-Admin-Key": "your-very-secret-admin-key"},
    )
    assert res.status_code == 200

    data = res.get_json()
    assert isinstance(data, list)
    assert any(g["name"] == "管理者テストグループ" for g in data)


# -------------------------------------------------
# 認証エラー（不正キー）
# -------------------------------------------------
def test_get_all_groups_invalid_key(client, create_group):
    create_group(name="不正キーグループ")

    res = client.get(
        "/api/admin/groups",
        headers={"X-Admin-Key": "invalid-key"},
    )
    assert res.status_code == 403
    responce = res.get_json()
    assert "管理者キーが無効です。" in responce["errors"]["json"]["message"]


# -------------------------------------------------
# グループ削除（DELETE /admin/groups/<group_key>）
# -------------------------------------------------
def test_delete_group(client, setup_full_tournament, db_session):
    # --- 前提データ作成 ---
    data = setup_full_tournament(client)
    group_key = data["group_links"]["OWNER"]
    group_id = data["group_data"]["id"]

    # --- 削除実行 ---
    res = client.delete(
        f"/api/admin/groups/{group_key}",
        headers={"X-Admin-Key": "your-very-secret-admin-key"},
    )
    assert res.status_code == 200
    assert "削除しました" in res.get_json()["message"]

    #--- DBから確認 ---
    deleted = Group.query.filter_by(id=group_id).first()
    assert deleted is None


# -------------------------------------------------
# 存在しないグループ削除
# -------------------------------------------------
def test_delete_group_not_found(client):
    res = client.delete(
        "/api/admin/groups/XXXXXXX",
        headers={"X-Admin-Key": "your-very-secret-admin-key"},
    )
    assert res.status_code == 404
    body = res.get_json()
    print(body)
    assert "共有リンクが無効です。" in body["errors"]["json"]["message"]
