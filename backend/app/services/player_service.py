# app/services/player_service.py
from app.models import db, Player

class PlayerService:
    @staticmethod
    def add_player(data: dict):
        group_id = data.get("group_id")
        name = data.get("name")

        player = Player(group_id=group_id, name=name)
        db.session.add(player)
        db.session.commit()
        return player

    @staticmethod
    def get_players_by_group(group_id: int):
        return Player.query.filter_by(group_id=group_id).all()

    @staticmethod
    def get_player(player_id: int):
        return Player.query.get_or_404(player_id)

    @staticmethod
    def delete_player(player_id: int):
        player = Player.query.get_or_404(player_id)

        if player.tournament_participations:
            return {"error": "このプレイヤーは大会に参加しているため削除できません"}, 400

        db.session.delete(player)
        db.session.commit()
        return {"message": "プレイヤーを削除しました"}, 200
