import pytest

from app.models import AccessLevel, Group
from app.models import ShareLink

@pytest.mark.api
class TestGroupEndpoints:
    def test_create_group_returns_owner_edit_view_links(self, client, db_session):
        response = client.post(
            "/api/groups",
            json={"name": "Test Group", "description": "Example"},
        )
        assert response.status_code == 201
        data = response.get_json()
        links = ShareLink.query.all()
        assert data["name"] == "Test Group"

        # ✅ share_links → group_links に変更
        assert "group_links" in data
        levels = {link["access_level"] for link in data["group_links"]}
        assert levels == {AccessLevel.OWNER.value, AccessLevel.EDIT.value, AccessLevel.VIEW.value}

        for link in data["group_links"]:
            assert link["short_key"]

    def test_get_group_by_short_key_ok(self, client, db_session):
        response = client.post("/api/groups", json={"name": "View Group"})
        group_data = response.get_json()

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

    def test_update_group_requires_owner(self, client, db_session):
        response = client.post("/api/groups", json={"name": "Initial Group"})
        group_data = response.get_json()
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

    def test_delete_group_requires_owner(self, client, db_session):
        response = client.post("/api/groups", json={"name": "Delete Group"})
        group_data = response.get_json()
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
