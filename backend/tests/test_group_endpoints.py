# tests/test_group_endpoints.py
import pytest
from app.models import Group, ShareLink, AccessLevel


@pytest.mark.api
class TestGroupEndpoints:

    def test_create_group(self, client, db_session):
        """
        /api/groups [POST]
        グループ作成 → short_keyが返ることを確認
        """
        res = client.post(
            "/api/groups",
            json={"name": "テストグループ", "description": "APIテスト用"},
        )

        assert res.status_code == 201
        data = res.get_json()
        assert data["name"] == "テストグループ"
        assert "short_key" in data
        assert len(data["short_key"]) > 5

        # DB確認
        group = db_session.query(Group).first()
        assert group is not None
        link = db_session.query(ShareLink).filter_by(resource_id=group.id).first()
        assert link.access_level == AccessLevel.OWNER


    def test_get_group_by_short_key(self, client, db_session):
        """
        /api/groups/<short_key> [GET]
        共有キーで取得できることを確認
        """
        # 事前データ作成
        group = Group(name="取得テスト", created_by="uuid-test")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="XYZ12345",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="uuid-test",
        )
        db_session.add(link)
        db_session.commit()

        res = client.get(f"/api/groups/{link.short_key}")
        assert res.status_code == 200

        data = res.get_json()
        assert data["id"] == group.id
        assert data["short_key"] == "XYZ12345"
        assert data["name"] == "取得テスト"


    def test_update_group_with_valid_key(self, client, db_session):
        """
        /api/groups/<id>?short_key=<key> [PUT]
        有効なキーで更新できることを確認
        """
        group = Group(name="更新前", created_by="uuid-test")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="UPD123",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="uuid-test",
        )
        db_session.add(link)
        db_session.commit()

        res = client.put(
            f"/api/groups/{group.id}?short_key={link.short_key}",
            json={"name": "更新後グループ"},
        )

        assert res.status_code == 200
        data = res.get_json()
        assert data["name"] == "更新後グループ"
        assert data["short_key"] == "UPD123"

        updated = db_session.get(Group, group.id)
        assert updated.name == "更新後グループ"


    def test_update_group_invalid_key(self, client, db_session):
        """
        無効なshort_keyで更新しようとした場合403
        """
        group = Group(name="不正更新", created_by="ownerA")
        db_session.add(group)
        db_session.commit()

        # 所有者が違うShareLink
        wrong_link = ShareLink(
            short_key="BADKEY",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="other_user",
        )
        db_session.add(wrong_link)
        db_session.commit()

        res = client.put(
            f"/api/groups/{group.id}?short_key={wrong_link.short_key}",
            json={"name": "改ざん"},
        )

        assert res.status_code == 403
        data = res.get_json()
        assert "Permission denied" in data["message"]


    def test_delete_group_with_valid_key(self, client, db_session):
        """
        /api/groups/<id>?short_key=<key> [DELETE]
        有効なキーで削除できることを確認
        """
        group = Group(name="削除テスト", created_by="uuid-del")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="DEL999",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="uuid-del",
        )
        db_session.add(link)
        db_session.commit()

        res = client.delete(f"/api/groups/{group.id}?short_key={link.short_key}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["message"] == "Group deleted"

        deleted = db_session.get(Group, group.id)
        assert deleted is None


    def test_delete_group_invalid_key(self, client, db_session):
        """
        無効なキーで削除しようとした場合403
        """
        group = Group(name="不正削除", created_by="uuid-a")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="DELETE_BAD",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="someone_else",
        )
        db_session.add(link)
        db_session.commit()

        res = client.delete(f"/api/groups/{group.id}?short_key={link.short_key}")
        assert res.status_code == 403
