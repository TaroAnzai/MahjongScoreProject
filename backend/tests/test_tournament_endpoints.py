# tests/test_tournament_endpoints.py
import pytest
from app.models import Group, Tournament, ShareLink, AccessLevel


@pytest.mark.api
class TestTournamentEndpoints:

    # ----------------------------
    # 大会追加（成功）
    # ----------------------------
    def test_create_tournament_with_valid_key(self, client, db_session):
        """有効なグループ共有キーで大会を追加できる"""
        group = Group(name="大会グループ", created_by="creatorA")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="TKEY123",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="creatorA",
        )
        db_session.add(link)
        db_session.commit()

        res = client.post(
            f"/api/tournaments?short_key={link.short_key}",
            json={"group_id": group.id, "name": "春季リーグ"},
        )
        assert res.status_code == 201
        data = res.get_json()
        print("response data:", data)
        assert data["name"] == "春季リーグ"

        # DB確認
        tournament = db_session.query(Tournament).first()
        assert tournament.name == "春季リーグ"
        assert tournament.group_id == group.id

    # ----------------------------
    # 大会追加（権限なし）
    # ----------------------------
    def test_create_tournament_invalid_permission(self, client, db_session):
        """他人の共有キーでは大会追加不可"""
        group = Group(name="権限テスト", created_by="ownerA")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="BADT123",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="not_owner",
        )
        db_session.add(link)
        db_session.commit()

        res = client.post(
            f"/api/tournaments?short_key={link.short_key}",
            json={"group_id": group.id, "name": "秋季リーグ"},
        )
        assert res.status_code == 403
        assert "権限" in res.get_json()["message"]

    # ----------------------------
    # 大会一覧取得
    # ----------------------------
    def test_get_tournaments_by_group(self, client, db_session):
        """共有リンクで大会一覧を取得できる"""
        group = Group(name="大会一覧", created_by="creatorB")
        db_session.add(group)
        db_session.commit()

        t1 = Tournament(group_id=group.id, name="リーグ1", created_by="creatorB")
        t2 = Tournament(group_id=group.id, name="リーグ2", created_by="creatorB")
        db_session.add_all([t1, t2])
        db_session.commit()

        link = ShareLink(
            short_key="LISTT123",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="creatorB",
        )
        db_session.add(link)
        db_session.commit()

        res = client.get(f"/api/tournaments?short_key={link.short_key}")
        assert res.status_code == 200
        data = res.get_json()
        names = [t["name"] for t in data]
        assert "リーグ1" in names and "リーグ2" in names

    # ----------------------------
    # 単一大会取得
    # ----------------------------
    def test_get_single_tournament(self, client, db_session):
        """大会をID指定で取得"""
        group = Group(name="単一大会", created_by="creatorC")
        db_session.add(group)
        db_session.commit()

        tournament = Tournament(group_id=group.id, name="夏季大会", created_by="creatorC")
        db_session.add(tournament)
        db_session.commit()

        res = client.get(f"/api/tournaments/{tournament.id}")
        assert res.status_code == 200
        assert res.get_json()["name"] == "夏季大会"

    # ----------------------------
    # 大会削除（成功）
    # ----------------------------
    def test_delete_tournament_with_valid_key(self, client, db_session):
        """有効キーで大会削除成功"""
        group = Group(name="削除テスト", created_by="creatorD")
        db_session.add(group)
        db_session.commit()

        tournament = Tournament(group_id=group.id, name="削除対象大会", created_by="creatorD")
        db_session.add(tournament)
        db_session.commit()

        link = ShareLink(
            short_key="DELTTT",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="creatorD",
        )
        db_session.add(link)
        db_session.commit()

        res = client.delete(f"/api/tournaments/{tournament.id}?short_key={link.short_key}")
        assert res.status_code == 200
        assert "削除しました" in res.get_json()["message"]

        deleted = db_session.get(Tournament, tournament.id)
        assert deleted is None

    # ----------------------------
    # 大会削除（権限なし）
    # ----------------------------
    def test_delete_tournament_invalid_permission(self, client, db_session):
        """他人の共有キーでは大会削除不可"""
        group = Group(name="不正削除グループ", created_by="ownerX")
        db_session.add(group)
        db_session.commit()

        tournament = Tournament(group_id=group.id, name="不正削除対象", created_by="ownerX")
        db_session.add(tournament)
        db_session.commit()

        link = ShareLink(
            short_key="DEL_BAD",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="not_owner",
        )
        db_session.add(link)
        db_session.commit()

        res = client.delete(f"/api/tournaments/{tournament.id}?short_key={link.short_key}")
        assert res.status_code == 403
