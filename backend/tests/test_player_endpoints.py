# tests/test_player_endpoints.py
import pytest
from app.models import Group, Player, ShareLink, AccessLevel


@pytest.mark.api
class TestPlayerEndpoints:

    # ----------------------------
    # プレイヤー追加
    # ----------------------------
    def test_add_player_with_valid_short_key(self, client, db_session):
        """有効なグループ共有キーでプレイヤーを追加できる"""
        # グループと共有リンクを作成
        group = Group(name="テストグループ", created_by="creatorA")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="GKEY123",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="creatorA",
        )
        db_session.add(link)
        db_session.commit()

        # プレイヤー追加リクエスト
        res = client.post(
            f"/api/players?short_key={link.short_key}",
            json={"group_id": group.id, "name": "太郎"},
        )

        assert res.status_code == 201
        data = res.get_json()
        assert data["name"] == "太郎"

        # DBに登録されていることを確認
        player = db_session.query(Player).first()
        assert player.name == "太郎"
        assert player.group_id == group.id

    # ----------------------------
    # 権限エラー（他人のキーで追加）
    # ----------------------------
    def test_add_player_with_invalid_permission(self, client, db_session):
        """別ユーザーの共有キーではプレイヤー追加不可"""
        group = Group(name="別グループ", created_by="creatorB")
        db_session.add(group)
        db_session.commit()

        link = ShareLink(
            short_key="BADKEY",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="someone_else",
        )
        db_session.add(link)
        db_session.commit()

        res = client.post(
            f"/api/players?short_key={link.short_key}",
            json={"group_id": group.id, "name": "Jiro"},
        )

        assert res.status_code == 403
        data = res.get_json()
        assert "権限" in data["message"]

    # ----------------------------
    # プレイヤー一覧取得
    # ----------------------------
    def test_get_players_by_group(self, client, db_session):
        """共有キーでプレイヤー一覧を取得"""
        group = Group(name="一覧グループ", created_by="creatorC")
        db_session.add(group)
        db_session.commit()

        player1 = Player(group_id=group.id, name="Alice")
        player2 = Player(group_id=group.id, name="Bob")
        db_session.add_all([player1, player2])
        db_session.commit()

        link = ShareLink(
            short_key="LIST123",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="creatorC",
        )
        db_session.add(link)
        db_session.commit()

        res = client.get(f"/api/players?short_key={link.short_key}")
        assert res.status_code == 200
        data = res.get_json()
        names = [p["name"] for p in data]
        assert "Alice" in names and "Bob" in names

    # ----------------------------
    # 単一プレイヤー取得
    # ----------------------------
    def test_get_single_player(self, client, db_session):
        """プレイヤー個別取得"""
        group = Group(name="単一テスト", created_by="creatorD")
        db_session.add(group)
        db_session.commit()

        player = Player(group_id=group.id, name="Charlie")
        db_session.add(player)
        db_session.commit()

        res = client.get(f"/api/players/{player.id}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["name"] == "Charlie"

    # ----------------------------
    # プレイヤー削除（成功）
    # ----------------------------
    def test_delete_player_with_valid_short_key(self, client, db_session):
        """有効キーでプレイヤー削除成功"""
        group = Group(name="削除グループ", created_by="creatorE")
        db_session.add(group)
        db_session.commit()

        player = Player(group_id=group.id, name="DeleteMe")
        db_session.add(player)
        db_session.commit()

        link = ShareLink(
            short_key="DEL123",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="creatorE",
        )
        db_session.add(link)
        db_session.commit()

        res = client.delete(f"/api/players/{player.id}?short_key={link.short_key}")
        assert res.status_code == 200
        data = res.get_json()
        assert "削除しました" in data["message"]

        deleted = db_session.get(Player, player.id)
        assert deleted is None

    # ----------------------------
    # プレイヤー削除（権限なし）
    # ----------------------------
    def test_delete_player_invalid_permission(self, client, db_session):
        """他人のキーでは削除不可"""
        group = Group(name="不正削除", created_by="ownerA")
        db_session.add(group)
        db_session.commit()

        player = Player(group_id=group.id, name="NoPerm")
        db_session.add(player)
        db_session.commit()

        link = ShareLink(
            short_key="NOPERM",
            resource_type="group",
            resource_id=group.id,
            access_level=AccessLevel.OWNER,
            created_by="other_user",
        )
        db_session.add(link)
        db_session.commit()

        res = client.delete(f"/api/players/{player.id}?short_key={link.short_key}")
        assert res.status_code == 403
