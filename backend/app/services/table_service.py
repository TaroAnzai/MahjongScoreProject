# app/services/table_service.py
import secrets
from app.models import db, Table, Player, TablePlayer, Score, Game

class TableService:
    @staticmethod
    def create_table(data: dict):
        if not data.get("name") or not data.get("tournament_id"):
            return {"error": "卓名、トーナメントIDは必須です"}, 400

        table = Table(
            name=data["name"],
            tournament_id=data["tournament_id"],
            type="normal",
            table_key=secrets.token_urlsafe(8),
            edit_key=secrets.token_urlsafe(8),
        )
        db.session.add(table)
        db.session.flush()

        for pid in data.get("player_ids", []):
            player = Player.query.get(pid)
            if player:
                db.session.add(TablePlayer(table_id=table.id, player_id=player.id))

        db.session.commit()
        return table, 201

    @staticmethod
    def get_table_by_key(table_key: str):
        table = Table.query.filter_by(table_key=table_key).first_or_404()
        players = (
            db.session.query(Player)
            .join(TablePlayer, Player.id == TablePlayer.player_id)
            .filter(TablePlayer.table_id == table.id)
            .all()
        )
        return {"table": table, "players": players}

    @staticmethod
    def get_table_by_id(table_id: int):
        table = Table.query.get_or_404(table_id)
        players = (
            db.session.query(Player)
            .join(TablePlayer, Player.id == TablePlayer.player_id)
            .filter(TablePlayer.table_id == table.id)
            .all()
        )
        return {"table": table, "players": players}

    @staticmethod
    def get_tables_by_tournament(tournament_id: int):
        return Table.query.filter_by(tournament_id=tournament_id).all()

    @staticmethod
    def get_players_by_table(table_id: int):
        return (
            db.session.query(Player)
            .join(TablePlayer, Player.id == TablePlayer.player_id)
            .filter(TablePlayer.table_id == table_id)
            .all()
        )

    @staticmethod
    def add_players_to_table(table_id: int, player_ids: list):
        table = Table.query.get_or_404(table_id)
        existing_ids = {tp.player_id for tp in TablePlayer.query.filter_by(table_id=table.id).all()}
        added = 0
        for pid in player_ids:
            if pid not in existing_ids:
                db.session.add(TablePlayer(table_id=table.id, player_id=pid))
                added += 1
        db.session.commit()
        return {"message": f"{added} player(s) added"}, 200

    @staticmethod
    def remove_player_from_table(table_id: int, player_id: int):
        table_player = TablePlayer.query.filter_by(table_id=table_id, player_id=player_id).first()
        if not table_player:
            return {"error": "指定されたプレイヤーはこの卓に存在しません"}, 404

        game_ids = db.session.query(Game.id).filter_by(table_id=table_id).subquery()
        scores = Score.query.filter(Score.game_id.in_(game_ids), Score.player_id == player_id).all()

        if scores and any(s.score != 0 for s in scores):
            return {"error": "スコアが登録されており、削除できません"}, 400

        for s in scores:
            db.session.delete(s)

        db.session.delete(table_player)
        db.session.commit()
        return {"message": "プレイヤーを削除しました"}, 200

    @staticmethod
    def delete_table(table_id: int):
        table = Table.query.get_or_404(table_id)
        if Game.query.filter_by(table_id=table.id).first():
            return {"error": "対局データが存在するため、削除できません"}, 400

        TablePlayer.query.filter_by(table_id=table.id).delete()
        db.session.delete(table)
        db.session.commit()
        return {"message": "卓を削除しました"}, 200

    @staticmethod
    def update_table(table_id: int, data: dict):
        table = Table.query.get_or_404(table_id)
        allowed_fields = {"name", "type", "description"}
        updated = False
        for key in allowed_fields:
            if key in data:
                setattr(table, key, data[key])
                updated = True
        if not updated:
            return {"error": "更新可能なフィールドが含まれていません"}, 400
        db.session.commit()
        return {"message": "テーブル情報を更新しました", "table": table}, 200
    
    @staticmethod
    def add_game(table_id: int, scores: list, memo: str = None):
        table = Table.query.get_or_404(table_id)

        if not scores or not isinstance(scores, list):
            return {"error": "scores はリスト形式で必須です"}, 400

        total = sum([s.get("score") or 0 for s in scores])
        if total != 0:
            return {"error": "スコアの合計は0でなければなりません"}, 400

        max_index = db.session.query(db.func.max(Game.game_index)).filter_by(table_id=table_id).scalar()
        next_index = (max_index or 0) + 1

        game = Game(table_id=table_id, game_index=next_index, memo=memo)
        db.session.add(game)
        db.session.flush()

        for s in scores:
            db.session.add(Score(game_id=game.id, player_id=s["player_id"], score=s["score"]))

        db.session.commit()
        return {"game_id": game.id}, 201
    
    @staticmethod
    def get_games(table_id: int):
        table = Table.query.get_or_404(table_id)
        games = Game.query.filter_by(table_id=table.id).order_by(Game.id.asc()).all()
        result = []
        for g in games:
            scores = Score.query.filter_by(game_id=g.id).all()
            result.append({
                "game_id": g.id,
                "scores": [{"player_id": s.player_id, "score": s.score} for s in scores]
            })
        return result