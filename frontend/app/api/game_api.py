from flask import Blueprint, request, jsonify
from app.models import db, Game, Score, Table, Player
from flask_login import login_required
game_bp = Blueprint('game', __name__, url_prefix='/api/games')


@game_bp.route('/<int:table_id>/games', methods=['POST'])
@login_required
def add_game(table_id):
    """
    卓に半荘結果（スコア）を追加
    例: { "scores": [ { "player_id": 1, "score": 25000 }, ... ] }
    """
    table = Table.query.get_or_404(table_id)
    data = request.json
    scores = data.get('scores', [])
    memo = data.get('memo')

    if not scores or not isinstance(scores, list):
        return jsonify({'error': 'scores はリスト形式で必須です'}), 400

    total = sum([s.get('score') or 0 for s in scores])
    if total != 0:
        return jsonify({'error': 'スコアの合計は0でなければなりません'}), 400
    
    # game_index を自動で決定（同卓内での連番）
    max_index = db.session.query(db.func.max(Game.game_index)).filter_by(table_id=table_id).scalar()
    next_index = (max_index or 0) + 1

    game = Game(table_id=table_id, game_index=next_index, memo=memo)
    db.session.add(game)
    db.session.flush()  # game.idを得る

    for s in scores:
        player_id = s.get('player_id')
        score = s.get('score')
        if player_id is None or score is None:
            continue
        db.session.add(Score(game_id=game.id, player_id=player_id, score=score))

    db.session.commit()
    return jsonify({'game_id': game.id}), 201


@game_bp.route('/<int:table_id>/games', methods=['GET'])
def get_games(table_id):
    """指定卓の全ゲームスコアを返す"""
    table = Table.query.get_or_404(table_id)
    games = Game.query.filter_by(table_id=table.id).order_by(Game.id.asc()).all()
    result = []

    for g in games:
        scores = Score.query.filter_by(game_id=g.id).all()
        result.append({
            'game_id': g.id,
            'scores': [{'player_id': s.player_id, 'score': s.score} for s in scores]
        })

    return jsonify(result)

@game_bp.route('', methods=['GET'])
def get_games_by_table():
    table_id = request.args.get('table_id')
    if not table_id:
        return jsonify({'error': 'table_id is required'}), 400

    games = Game.query.filter_by(table_id=table_id).order_by(Game.id).all()
    result = []
    for game in games:
        scores = Score.query.filter_by(game_id=game.id).all()
        result.append({
            'game_id': game.id,
            'scores': [
                {'player_id': s.player_id, 'score': s.score}
                for s in scores
            ]
        })

    return jsonify(result)

from datetime import datetime
from app.models import db, Game, Score

@game_bp.route('/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    """
    ゲーム情報（memo, played_at, scores）を更新
    """
    game = Game.query.get_or_404(game_id)
    data = request.json

    # memo更新
    memo = data.get('memo')
    if memo is not None:
        game.memo = memo

    # played_at更新
    played_at = data.get('played_at')
    if played_at is not None:
        try:
            game.played_at = datetime.fromisoformat(played_at)
        except ValueError:
            return jsonify({'error': 'played_at の形式が不正です'}), 400

    # scores更新（あれば）
    new_scores = data.get('scores')
    if new_scores:
        if not isinstance(new_scores, list):
            return jsonify({'error': 'scores はリスト形式である必要があります'}), 400

        total = sum(s.get('score', 0) for s in new_scores)
        if total != 0:
            return jsonify({'error': 'スコアの合計は0である必要があります'}), 400

        # 既存スコア削除
        Score.query.filter_by(game_id=game.id).delete()

        # 新規スコア追加
        for s in new_scores:
            player_id = s.get('player_id')
            score_val = s.get('score')
            if player_id is None or score_val is None:
                continue
            new_score = Score(game_id=game.id, player_id=player_id, score=score_val)
            db.session.add(new_score)

    db.session.commit()
    return jsonify({'message': 'Game updated'})

@game_bp.route('/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    """
    ゲームを削除（スコアも削除）
    """
    game = Game.query.get_or_404(game_id)

    db.session.delete(game)
    db.session.commit()
    return jsonify({'message': 'Game deleted'})
