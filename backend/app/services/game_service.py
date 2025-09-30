# app/services/game_service.py
from datetime import datetime
from app.models import db, Game, Score, Table

class GameService:
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

    @staticmethod
    def update_game(game_id: int, data: dict):
        game = Game.query.get_or_404(game_id)

        if "memo" in data:
            game.memo = data["memo"]

        if "played_at" in data and data["played_at"] is not None:
            try:
                game.played_at = datetime.fromisoformat(data["played_at"])
            except ValueError:
                return {"error": "played_at の形式が不正です"}, 400

        if "scores" in data and data["scores"]:
            scores = data["scores"]
            if not isinstance(scores, list):
                return {"error": "scores はリスト形式である必要があります"}, 400

            total = sum(s.get("score", 0) for s in scores)
            if total != 0:
                return {"error": "スコアの合計は0である必要があります"}, 400

            Score.query.filter_by(game_id=game.id).delete()
            for s in scores:
                db.session.add(Score(game_id=game.id, player_id=s["player_id"], score=s["score"]))

        db.session.commit()
        return {"message": "Game updated"}, 200

    @staticmethod
    def delete_game(game_id: int):
        game = Game.query.get_or_404(game_id)
        db.session.delete(game)
        db.session.commit()
        return {"message": "Game deleted"}, 200
