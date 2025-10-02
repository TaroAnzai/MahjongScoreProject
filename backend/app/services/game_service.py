# app/services/game_service.py
from datetime import datetime
from app.models import db, Game, Score, Table

class GameService:




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
