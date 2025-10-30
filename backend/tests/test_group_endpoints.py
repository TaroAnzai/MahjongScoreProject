import pytest

from app.models import AccessLevel, Group
from app.models import ShareLink
from app.models import GroupCreationToken
@pytest.mark.api
class TestGroupEndpoints:
    def test_create_group_returns_owner_edit_view_links(self, client, db_session):
        email = "user@example.com"
        group_name = "TEST GROUP"
        # ------------------------------------------------------------
        # 1️⃣ メール送信リクエスト
        # ------------------------------------------------------------
        res1 = client.post("/api/groups/request-link", json={"name": group_name, "email": email})
        print(res1.get_json())
        assert res1.status_code == 200
        res1_json = res1.get_json()
        assert "expires_at" in res1_json

        # ------------------------------------------------------------
        # 2️⃣ トークンをDBから取得（実際にはメールで届く想定）
        # ------------------------------------------------------------
        token_record = GroupCreationToken.query.filter_by(email=email).order_by(GroupCreationToken.id.desc()).first()
        assert token_record is not None
        token = token_record.token

        # ------------------------------------------------------------
        # 3️⃣ トークンを使ってグループを作成
        # ------------------------------------------------------------
        res = client.post("/api/groups", json={"token": token})
        assert res.status_code == 201
        data = res.get_json()
        links = {l["access_level"]: l["short_key"] for l in data["group_links"]}

        levels = {l["access_level"] for l in data["group_links"]}

        assert data["name"] == group_name
        assert levels == {AccessLevel.OWNER.value, AccessLevel.EDIT.value, AccessLevel.VIEW.value}
        for link in data["group_links"]:
            assert link["short_key"]

    def test_get_group_by_short_key_ok(self, client, db_session, create_group):
        group_data, links = create_group("View Group")
        # ✅ group_links に変更
        view_key = next(
            link["short_key"]
            for link in group_data["group_links"]
            if link["access_level"] == AccessLevel.VIEW.value
        )

        # ✅ VIWE権限のshort_key をURLパスとして使用
        res = client.get(f"/api/groups/{view_key}")
        assert res.status_code == 200
        fetched = res.get_json()
        assert fetched["id"] == group_data["id"]
        assert "view_link" in fetched
        assert "edit_link" not in fetched
        assert "owner_link" not in fetched
        assert "group_links" in fetched

        links = fetched["group_links"]
        assert all(link["access_level"] == "VIEW" for link in links)
        levels = [link["access_level"] for link in links]
        assert "OWNER" not in levels, f"Unexpected OWNER links: {links}"
        assert "EDIT" not in levels, f"Unexpected EDIT links: {links}"

    def test_update_group_requires_owner(self, client, db_session, create_group):
        group_data, links = create_group("Initial Group")
        group_id = group_data["id"]

        edit_key = next(
            link["short_key"]
            for link in group_data["group_links"]
            if link["access_level"] == AccessLevel.EDIT.value
        )

        # ✅ group_idではなくshort_keyをURLに使用
        res = client.put(
            f"/api/groups/{edit_key}",
            json={"name": "Should Fail"},
        )
        assert res.status_code == 403

        stored = db_session.get(Group, group_id)
        assert stored.name == "Initial Group"

    def test_delete_group_requires_owner(self, client, db_session, create_group):
        group_data, links = create_group("Delete Group")
        group_id = group_data["id"]

        edit_key = next(
            link["short_key"]
            for link in group_data["group_links"]
            if link["access_level"] == AccessLevel.EDIT.value
        )

        # ✅ クエリではなくURLパスでshort_keyを指定
        res = client.delete(f"/api/groups/{edit_key}")
        assert res.status_code == 403
        assert db_session.get(Group, group_id) is not None
