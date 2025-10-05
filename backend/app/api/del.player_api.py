from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.models import db, Player

player_bp = Blueprint('player', __name__, url_prefix='/api/players')

@player_bp.route('', methods=['POST'])
@login_required
def add_player():
    """グループにプレイヤーを追加する"""
    data = request.json
    group_id = data.get('group_id')
    name = data.get('name')

    if not group_id or not name:
        return jsonify({'error': 'group_idとnameは必須です'}), 400

    player = Player(group_id=group_id, name=name)
    db.session.add(player)
    db.session.commit()

    return jsonify({'id': player.id, 'name': player.name}), 201

@player_bp.route('', methods=['GET'])
def get_players_by_group():
    """指定されたグループのプレイヤー一覧を返す"""
    group_id = request.args.get('group_id')
    if not group_id:
        return jsonify({'error': 'group_id is required'}), 400

    players = Player.query.filter_by(group_id=group_id).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in players])

@player_bp.route('/<int:player_id>', methods=['GET'])
def get_player(player_id):
    """プレイヤー情報を1件取得"""
    player = Player.query.get_or_404(player_id)
    return jsonify({
        'id': player.id,
        'name': player.name,
        'group_id': player.group_id
    })
@player_bp.route('/<int:player_id>', methods=['DELETE'])
@login_required
def delete_player(player_id):
    """プレイヤーを削除（ただし大会参加中なら削除不可）"""
    player = Player.query.get_or_404(player_id)

    # そのプレイヤーが参加している大会があれば削除不可
    if player.tournament_participations:
        return jsonify({'error': 'このプレイヤーは大会に参加しているため削除できません'}), 400

    # プレイヤーを削除
    db.session.delete(player)
    db.session.commit()

    return jsonify({'message': 'プレイヤーを削除しました'}), 200