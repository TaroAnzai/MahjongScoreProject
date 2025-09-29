# app/api/tournament_api.py

import secrets
from flask import Blueprint, request, jsonify
from flask_login import login_required
import datetime
from dateutil import parser
from app.models import db, Tournament, Group, TournamentPlayer, Player, Table, TablePlayer
from decimal import Decimal


tournament_bp = Blueprint('tournament', __name__, url_prefix='/api/tournaments')


@tournament_bp.route('/<tournament_key>', methods=['GET'])
def get_tournament_by_key(tournament_key):
    """tournament_key を使って大会情報を取得"""
    tournament = Tournament.query.filter_by(tournament_key=tournament_key).first()
    if not tournament:
        return jsonify({'error': 'Tournament not found'}), 404
    return jsonify(tournament.to_dict())

@tournament_bp.route('/by-id/<int:tournament_id>', methods=['GET'])
def get_tournament_by_id(tournament_id):
    """tournament_id を使って大会情報を取得（開発・内部用）"""
    tournament = Tournament.query.get_or_404(tournament_id)
    return jsonify(tournament.to_dict())


@tournament_bp.route('', methods=['POST'])
@login_required
def create_tournament():
    """大会を新規作成（edit_key, tournament_key 自動発行）"""
    import secrets
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    group_id = data.get('group_id')

    if not name or not group_id:
        return jsonify({'error': 'name and group_id are required'}), 400

    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'group not found'}), 404

    # ① まずトーナメントを作成し、commitでIDを確定
    tournament = Tournament(
        name=name,
        description=description,
        group_id=group_id,
        tournament_key=secrets.token_urlsafe(12),
        edit_key=secrets.token_urlsafe(12),
        rate=50.0,
        started_at=datetime.datetime.now(),
    )
    db.session.add(tournament)
    db.session.commit()  # ← tournament.id を確定

    # ② チップ用テーブルを大会ID付きで作成
    table_key = secrets.token_urlsafe(8)
    edit_key = secrets.token_urlsafe(8)

    chip_table = Table(
        name='チップ',
        tournament_id=tournament.id,
        type='chip',
        table_key=table_key,
        edit_key=edit_key
    )
    db.session.add(chip_table)
    db.session.commit()

    return jsonify({
        'id': tournament.id,
        'name': tournament.name,
        'description': tournament.description,
        'group_id': tournament.group_id,
        'tournament_key': tournament.tournament_key,
        'edit_key': tournament.edit_key
    }), 201



@tournament_bp.route('/<int:tournament_id>', methods=['PUT'])
@login_required
def update_tournament(tournament_id):
    """大会情報を編集（edit_key によるログイン必須）"""
    tournament = Tournament.query.get_or_404(tournament_id)
    data = request.json

    tournament.name = data.get('name', tournament.name)
    tournament.description = data.get('description', tournament.description)

    if 'rate' in data:
        try:
            tournament.rate = float(data['rate'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid rate format'}), 400
        
    if 'started_at' in data:
        try:
            tournament.started_at = parser.isoparse(data['started_at'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid started_at format'}), 400

    db.session.commit()
    return jsonify(tournament.to_dict())

@tournament_bp.route('', methods=['GET'])
def get_tournaments():
    group_id = request.args.get('group_id')
    key = request.args.get('tournament_key')

    if group_id:
        # グループIDから大会一覧を取得
        tournaments = Tournament.query.filter_by(group_id=group_id).all()
        return jsonify([t.to_dict() for t in tournaments])

    elif key:
        # tournament_key から大会情報を取得
        tournament = Tournament.query.filter_by(tournament_key=key).first()
        if not tournament:
            return jsonify({'error': 'Tournament not found'}), 404
        return jsonify(tournament.to_dict())

    else:
        # fallback: 全大会を返す（通常は不要・制限ありにしてもよい）
        return jsonify({'error': 'Missing required query parameter'}), 400



@tournament_bp.route('/<int:tournament_id>/players', methods=['GET'])
def get_tournament_players(tournament_id):
    """
    指定大会に参加しているプレイヤー一覧を取得
    レスポンス: [{id, name, nickname, ...}]
    """
    players = (
        db.session.query(Player)
        .join(TournamentPlayer, Player.id == TournamentPlayer.player_id)
        .filter(TournamentPlayer.tournament_id == tournament_id)
        .all()
    )

    return jsonify([p.to_dict() for p in players])


@tournament_bp.route('/<int:tournament_id>/players', methods=['POST'])
@login_required
def register_tournament_players(tournament_id):
    """
    指定大会にプレイヤーを登録する
    リクエストJSON: { "player_ids": [1, 2, 3] }
    レスポンス: { "message": "registered", "count": 登録数 }
    """
    data = request.get_json()
    player_ids = data.get('player_ids', [])

    if not player_ids or not isinstance(player_ids, list):
        return jsonify({'error': 'player_idsのリストが必要です'}), 400

    # 重複防止のため既存チェック
    existing = {
        tp.player_id
        for tp in TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()
    }
    chip_table = (
        Table.query
        .filter_by(tournament_id=tournament_id, type='chip')
        .first()
    )
    new_players = []
    chip_players = []

    for pid in player_ids:
        if pid not in existing:
            new_players.append(TournamentPlayer(tournament_id=tournament_id, player_id=pid))
            if chip_table:
                chip_players.append(TablePlayer(table_id=chip_table.id, player_id=pid))

    db.session.add_all(new_players + chip_players)
    db.session.commit()

    return jsonify({'message': 'registered', 'count': len(new_players)}), 201

@tournament_bp.route('/<int:tournament_id>/player_scores', methods=['GET'])
def get_player_total_scores(tournament_id):
    """
    各プレイヤーの合計スコアと換算点を返す
    レスポンス: { player_id: { raw: 合計点, converted: 換算点 } }
    """
    from sqlalchemy import func
    from app.models import Score, Game, Table, Player, TournamentPlayer

    tournament = Tournament.query.get_or_404(tournament_id)
    rate = Decimal(str(tournament.rate or 1.0))  # ★ ここでDecimalに変換

    normal_subq = (
        db.session.query(
            Score.player_id,
            func.sum(Score.score).label('score')
        )
        .join(Game, Score.game_id == Game.id)
        .join(Table, Game.table_id == Table.id)
        .filter(
            Table.tournament_id == tournament_id,
            Table.type != 'chip'
        )
        .group_by(Score.player_id)
        .subquery()
    )

    chip_subq = (
        db.session.query(
            Score.player_id,
            func.sum(Score.score).label('chip_score')
        )
        .join(Game, Score.game_id == Game.id)
        .join(Table, Game.table_id == Table.id)
        .filter(
            Table.tournament_id == tournament_id,
            Table.type == 'chip'
        )
        .group_by(Score.player_id)
        .subquery()
    )

    results = (
        db.session.query(
            Player.id,
            (func.coalesce(normal_subq.c.score, 0) + func.coalesce(chip_subq.c.chip_score, 0)).label("total")
        )
        .outerjoin(normal_subq, Player.id == normal_subq.c.player_id)
        .outerjoin(chip_subq, Player.id == chip_subq.c.player_id)
        .join(TournamentPlayer, TournamentPlayer.player_id == Player.id)
        .filter(TournamentPlayer.tournament_id == tournament_id)
        .all()
    )

    return jsonify({
        pid: {
            "raw": float(total),  # 表示用にfloatにしておくと無難（特にJSとの通信では）
            "converted": float(round(total * rate, 1))
        } for pid, total in results
    })

@tournament_bp.route('/<int:tournament_id>/players/<int:player_id>', methods=['DELETE'])
@login_required
def remove_player_from_tournament(tournament_id, player_id):
    """
    指定大会から参加者を削除する。
    条件：
    - 通常卓に参加していない
    - チップ卓にいる場合は、スコアがすべて0なら削除可能
    """
    from app.models import Table, TablePlayer, Game, Score, TournamentPlayer

    # 該当エントリの存在確認
    tp_entry = TournamentPlayer.query.filter_by(tournament_id=tournament_id, player_id=player_id).first()
    if not tp_entry:
        return jsonify({'error': '指定されたプレイヤーはこの大会に登録されていません'}), 404

    # 通常卓に参加していないか確認
    normal_tables = Table.query.filter_by(tournament_id=tournament_id).filter(Table.type != 'chip').all()
    normal_table_ids = [t.id for t in normal_tables]
    if TablePlayer.query.filter(TablePlayer.table_id.in_(normal_table_ids), TablePlayer.player_id == player_id).first():
        return jsonify({'error': '通常卓に参加しているため削除できません'}), 400

    # チップ卓の処理
    chip_table = Table.query.filter_by(tournament_id=tournament_id, type='chip').first()
    if chip_table:
        chip_tp = TablePlayer.query.filter_by(table_id=chip_table.id, player_id=player_id).first()
        if chip_tp:
            # チップスコア確認
            game_ids = db.session.query(Game.id).filter_by(table_id=chip_table.id).subquery()
            scores = Score.query.filter(Score.game_id.in_(game_ids), Score.player_id == player_id).all()

            if any(s.score != 0 for s in scores):
                return jsonify({'error': 'チップ卓でスコアが記録されており削除できません'}), 400

            # スコアがすべて0なら削除
            for score in scores:
                db.session.delete(score)
            db.session.delete(chip_tp)

    # 最後に大会参加記録を削除
    db.session.delete(tp_entry)
    db.session.commit()

    return jsonify({'message': 'プレイヤーを大会から削除しました'}), 200
