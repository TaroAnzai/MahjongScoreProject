# app/api/auth_api.py

from flask import Blueprint, request, jsonify
from flask_login import login_user
from app.models import Group, Tournament
from app.auth import PseudoUser

auth_api = Blueprint('auth_api', __name__, url_prefix='/api')


@auth_api.route('/login/by-key', methods=['POST'])
def login_by_key():
    data = request.json
    edit_key = data.get('edit_key')
    target = data.get('type')  # "group" または "tournament"

    if target == "group":
        obj = Group.query.filter_by(edit_key=edit_key).first()
    elif target == "tournament":
        obj = Tournament.query.filter_by(edit_key=edit_key).first()
    else:
        return jsonify({'error': 'Invalid type'}), 400

    if not obj:
        return jsonify({'error': 'Invalid edit_key'}), 403

    user = PseudoUser(id=f"{target}:{obj.id}", edit_key=edit_key)
    login_user(user)
    return jsonify({'message': 'Login successful'})

@auth_api.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message':'Pong'})

@auth_api.route('/debug-session')
def debug_session():
    from flask import request
    return jsonify({
        "session_cookie": request.cookies.get('mahjong_session'),
        "headers": dict(request.headers)
    })
