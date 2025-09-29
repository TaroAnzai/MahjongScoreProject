from flask import Blueprint, request, jsonify
from app.models import db, Table, Player, TablePlayer
from flask_login import login_required
import secrets

table_bp = Blueprint('table', __name__, url_prefix='/api/tables')

@table_bp.route('', methods=['POST'])
@login_required
def create_table():
    """卓を作成し、参加者を割り当てる"""
    data = request.json
    name = data.get('name')
    tournament_id = data.get('tournament_id')
    player_ids = data.get('player_ids', [])  # プレイヤーIDのリスト

    if not name or not tournament_id:
        return jsonify({'error': '卓名、トーナメントID'}), 400
    
    table_key = secrets.token_urlsafe(8)
    edit_key = secrets.token_urlsafe(8)

    table = Table(
        name=name,
        tournament_id=tournament_id,
        type='nomal',
        table_key=table_key,
        edit_key=edit_key
    )
    db.session.add(table)
    db.session.flush()  # table.id を取得するため

    for pid in player_ids:
        player = Player.query.get(pid)
        if player:
            table_player = TablePlayer(table_id=table.id, player_id=player.id)
            db.session.add(table_player)

    db.session.commit()
    return jsonify(table.to_dict()), 201



@table_bp.route('/<string:table_key>', methods=['GET'])
def get_table_by_key(table_key):
    """テーブルキーで卓を取得（参加者含む）"""
    table = Table.query.filter_by(table_key=table_key).first_or_404()

    players = (
        db.session.query(Player)
        .join(TablePlayer, Player.id == TablePlayer.player_id)
        .filter(TablePlayer.table_id == table.id)
        .all()
    )

    return jsonify({
        'table': table.to_dict(),
        'players': [p.to_dict() for p in players]
    })

@table_bp.route('/by-id/<int:table_id>', methods=['GET'])
@login_required
def get_table_by_id(table_id):
    """テーブルIDで取得"""
    table = Table.query.get_or_404(table_id)

    players = (
        db.session.query(Player)
        .join(TablePlayer, Player.id == TablePlayer.player_id)
        .filter(TablePlayer.table_id == table.id)
        .all()
    )

    return jsonify({
        'table': table.to_dict(),
        'players': [p.to_dict() for p in players]
    })

@table_bp.route('', methods=['GET'])
def get_tables_by_tournament():
    tournament_id = request.args.get('tournament_id')
    if not tournament_id:
        return jsonify({'error': 'tournament_id is required'}), 400

    tables = Table.query.filter_by(tournament_id=tournament_id).all()
    return jsonify([t.to_dict() for t in tables])


@table_bp.route('/<int:table_id>/players', methods=['GET'])
@login_required
def get_players_by_table(table_id):
    """
    指定された卓に参加しているプレイヤーを取得する
    レスポンス: { "players": [ {id, name, nickname, ...}, ... ] }
    """
    table_players = (
        db.session.query(Player)
        .join(TablePlayer, Player.id == TablePlayer.player_id)
        .filter(TablePlayer.table_id == table_id)
        .all()
    )

    players = [p.to_dict() for p in table_players]
    return jsonify({'players': players}), 200
@table_bp.route('/<int:table_id>/players', methods=['POST'])
@login_required
def add_players_to_table(table_id):
    """
    卓に参加者を追加する（重複しない場合のみ）
    リクエスト: { "player_ids": [1, 2, 3] }
    """
    data = request.json
    new_player_ids = data.get('player_ids', [])

    if not isinstance(new_player_ids, list):
        return jsonify({'error': 'player_ids must be a list'}), 400

    table = Table.query.get_or_404(table_id)

    existing_ids = {
        tp.player_id for tp in TablePlayer.query.filter_by(table_id=table.id).all()
    }

    added = 0
    for pid in new_player_ids:
        if pid not in existing_ids:
            db.session.add(TablePlayer(table_id=table.id, player_id=pid))
            added += 1

    db.session.commit()
    return jsonify({'message': f'{added} player(s) added'}), 200

from app.models import db, TablePlayer, Score

@table_bp.route('/<int:table_id>/players/<int:player_id>', methods=['DELETE'])
@login_required
def remove_player_from_table(table_id, player_id):
    """
    卓からプレイヤーを削除する。
    - スコアが一つでも0以外なら削除できない。
    - スコアがすべて0なら削除可能、スコアも一緒に削除。
    """
    # 対象の参加情報の確認
    table_player = TablePlayer.query.filter_by(table_id=table_id, player_id=player_id).first()
    if not table_player:
        return jsonify({'error': '指定されたプレイヤーはこの卓に存在しません'}), 404

    # 対象テーブルの全ゲームID取得
    from app.models import Game
    game_ids = db.session.query(Game.id).filter_by(table_id=table_id).subquery()

    # 対象プレイヤーのスコア取得（この卓に関連するゲームのみ）
    scores = Score.query.filter(Score.game_id.in_(game_ids), Score.player_id == player_id).all()

    if scores:
        if any(s.score != 0 for s in scores):
            return jsonify({'error': 'スコアが登録されており、削除できません'}), 400

        # すべて0ならScoreも削除
        for score in scores:
            db.session.delete(score)

    db.session.delete(table_player)
    db.session.commit()
    return jsonify({'message': 'プレイヤーを削除しました'}), 200

@table_bp.route('/<int:table_id>', methods=['DELETE'])
@login_required
def delete_table(table_id):
    """
    卓を削除する。
    - Game が存在する場合は削除不可。
    - TablePlayer が存在する場合は先に削除して問題なし。
    """
    from app.models import Game, TablePlayer

    table = Table.query.get_or_404(table_id)

    # Game が存在していれば削除不可
    has_games = Game.query.filter_by(table_id=table.id).first() is not None
    if has_games:
        return jsonify({'error': '対局データが存在するため、削除できません'}), 400

    # TablePlayer を削除（参加者だけの場合は削除してOK）
    TablePlayer.query.filter_by(table_id=table.id).delete()

    # Table を削除
    db.session.delete(table)
    db.session.commit()

    return jsonify({'message': '卓を削除しました'}), 200

@table_bp.route('/<int:table_id>', methods=['PUT'])
@login_required
def update_table(table_id):
    """
    テーブル情報を更新する。
    リクエスト: 任意のテーブル属性を含むJSON（name, type など）
    """
    data = request.json
    if not data:
        return jsonify({'error': '更新データが空です'}), 400

    table = Table.query.get_or_404(table_id)

    # 更新可能なフィールドのみを許可
    allowed_fields = {'name', 'type', 'description'}
    updated = False
    for key in allowed_fields:
        if key in data:
            setattr(table, key, data[key])
            updated = True

    if not updated:
        return jsonify({'error': '更新可能なフィールドが含まれていません'}), 400

    db.session.commit()
    return jsonify({'message': 'テーブル情報を更新しました', 'table': table.to_dict()}), 200
