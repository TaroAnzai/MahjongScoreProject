# app/api/group_api.py

import secrets
from flask import Blueprint, request, jsonify
from app.models import db, Group
from flask_login import login_required

group_bp = Blueprint('group', __name__, url_prefix='/api/groups')


@group_bp.route('', methods=['POST'])
def create_group():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'name is required'}), 400

    group = Group(
        name=name,
        description=description,
        group_key=secrets.token_urlsafe(12),
        edit_key=secrets.token_urlsafe(12)
    )
    db.session.add(group)
    db.session.commit()

    return jsonify({
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'group_key': group.group_key,
        'edit_key': group.edit_key
    }), 201


@group_bp.route('/<int:group_id>', methods=['PUT'])
@login_required
def update_group(group_id):
    group = Group.query.get_or_404(group_id)
    data = request.json
    group.name = data.get('name', group.name)
    group.description = data.get('description', group.description)
    db.session.commit()
    return jsonify(group.to_dict())

# 追加: group_keyでのグループ取得エンドポイント
@group_bp.route('', methods=['GET'])
def get_group_by_key():
    group_key = request.args.get('key')
    if not group_key:
        return jsonify({'error': 'group_key is required'}), 400

    group = Group.query.filter_by(group_key=group_key).first()
    if not group:
        return jsonify({'error': 'Group not found'}), 404

    return jsonify(group.to_dict())
