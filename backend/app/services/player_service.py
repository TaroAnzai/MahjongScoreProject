# app/services/player_service.py
from app import db
from app.models import Player, Group, ShareLink, AccessLevel
from app.utils.share_link_utils import get_share_link_by_key


class PlayerService:
    @staticmethod
    def _verify_group_access(group_id: int, short_key: str, require_edit: bool = False):
        """共有キーによるグループアクセス権限を確認"""
        link = get_share_link_by_key(short_key)
        if not link or link.resource_type != "group":
            raise PermissionError("無効な共有リンクです。")

        group = Group.query.get_or_404(link.resource_id)
        if group.id != group_id:
            raise PermissionError("共有リンクがこのグループに対応していません。")

        # 編集権限チェック
        if require_edit and link.created_by != group.created_by:
            raise PermissionError("このグループを編集する権限がありません。")

        return group

    # -------------------------------
    # CRUD
    # -------------------------------

    @staticmethod
    def add_player(data: dict, short_key: str):
        """プレイヤー追加（要グループ編集権限）"""
        group_id = data.get("group_id")
        PlayerService._verify_group_access(group_id, short_key, require_edit=True)

        player = Player(group_id=group_id, name=data["name"])
        db.session.add(player)
        db.session.commit()
        return player

    @staticmethod
    def get_players_by_group(short_key: str):
        """共有リンクでグループのプレイヤー一覧を取得"""
        link = get_share_link_by_key(short_key)
        if not link or link.resource_type != "group":
            raise PermissionError("無効な共有リンクです。")

        group = Group.query.get_or_404(link.resource_id)
        return Player.query.filter_by(group_id=group.id).all()

    @staticmethod
    def get_player(player_id: int):
        """単一プレイヤー取得"""
        return Player.query.get_or_404(player_id)

    @staticmethod
    def delete_player(player_id: int, short_key: str):
        """プレイヤー削除（要グループ編集権限）"""
        player = Player.query.get_or_404(player_id)
        PlayerService._verify_group_access(player.group_id, short_key, require_edit=True)

        if getattr(player, "tournament_participations", None):
            return {"error": "このプレイヤーは大会に参加しているため削除できません"}, 400

        db.session.delete(player)
        db.session.commit()
        return {"message": "プレイヤーを削除しました"}, 200
