import pytest

from app.models import AccessLevel, Group


@pytest.mark.api
class TestGroupEndpoints:
    def test_create_group_returns_owner_edit_view_links(self, client, db_session):
        response = client.post(
            "/api/groups",
            json={"name": "Test Group", "description": "Example"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Test Group"
        assert data["share_links"]

        levels = {link["access_level"] for link in data["share_links"]}
        assert levels == {AccessLevel.OWNER.value, AccessLevel.EDIT.value, AccessLevel.VIEW.value}
        for link in data["share_links"]:
            assert link["short_key"]

    def test_get_group_by_short_key_ok(self, client, db_session):
        response = client.post("/api/groups", json={"name": "View Group"})
        group_data = response.get_json()
        view_key = next(
            link["short_key"]
            for link in group_data["share_links"]
            if link["access_level"] == AccessLevel.VIEW.value
        )

        res = client.get(f"/api/groups/{view_key}")
        assert res.status_code == 200
        fetched = res.get_json()
        assert fetched["id"] == group_data["id"]
        assert fetched["share_links"]

    def test_update_group_requires_owner(self, client, db_session):
        response = client.post("/api/groups", json={"name": "Initial Group"})
        group_data = response.get_json()
        group_id = group_data["id"]
        edit_key = next(
            link["short_key"]
            for link in group_data["share_links"]
            if link["access_level"] == AccessLevel.EDIT.value
        )

        res = client.put(
            f"/api/groups/{group_id}?short_key={edit_key}",
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
            for link in group_data["share_links"]
            if link["access_level"] == AccessLevel.EDIT.value
        )

        res = client.delete(f"/api/groups/{group_id}?short_key={edit_key}")
        assert res.status_code == 403
        assert db_session.get(Group, group_id) is not None
