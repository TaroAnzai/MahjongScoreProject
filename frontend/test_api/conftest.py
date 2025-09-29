# test_api/conftest.py

import pytest
from app import create_app, db

@pytest.fixture(scope='session')
def test_app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # ✅ テスト専用の一時DB
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'LOGIN_DISABLED': True  # 認証を無効化する場合
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope="session")
def test_data():
    return {}
