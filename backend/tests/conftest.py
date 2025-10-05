import os
import tempfile
import pytest
from app import create_app, db
from app.models import Group, Tournament, Table, Game, Player, ShareLink, AccessLevel


@pytest.fixture(scope="session")
def test_app():
    """
    Flaskアプリ全体のテスト用インスタンスを作成。
    実際のDBとは別のSQLiteメモリDBを使用する。
    """
    # 一時ディレクトリ
    db_fd, db_path = tempfile.mkstemp()

    # 環境変数をテストモードに設定
    os.environ["FLASK_ENV"] = "testing"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    # Flaskアプリ作成
    app = create_app("testing")

    # DB初期化
    with app.app_context():
        db.create_all()

    yield app

    # クリーンアップ
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(test_app):
    """
    Flaskのテストクライアントを返すfixture。
    APIエンドポイントができたらこれを使ってrequest送信を行う。
    """
    return test_app.test_client()


@pytest.fixture()
def app_context(test_app):
    """
    app_contextを提供するfixture。
    サービス層やDB操作関数の単体テストで使用。
    """
    with test_app.app_context():
        yield


@pytest.fixture()
def db_session(app_context):
    """
    テスト用のDBセッションを提供。
    各テスト後にロールバックしてクリーン状態に戻す。
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


# =========================================================
# テストデータ生成用ユーティリティ
# =========================================================

@pytest.fixture()
def sample_group(db_session):
    """Groupを1件作成"""
    group = Group(name="Test Group", created_by="uuid-test")
    db_session.add(group)
    db_session.commit()
    return group


@pytest.fixture()
def sample_tournament(db_session, sample_group):
    """Tournamentを1件作成"""
    tournament = Tournament(
        name="Test Tournament",
        group_id=sample_group.id,
        created_by="uuid-test",
    )
    db_session.add(tournament)
    db_session.commit()
    return tournament


@pytest.fixture()
def sample_sharelink(db_session, sample_group):
    """ShareLinkを1件作成（OWNERアクセス）"""
    link = ShareLink(
        short_key="ABCDEFG1234",
        resource_type="group",
        resource_id=sample_group.id,
        access_level=AccessLevel.OWNER,
        created_by="uuid-test",
    )
    db_session.add(link)
    db_session.commit()
    return link
