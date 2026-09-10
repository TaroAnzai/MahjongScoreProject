from unittest.mock import patch


def test_health_checks_database(client):
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}


def test_health_does_not_leak_database_error(client):
    with patch('app.db.session.execute', side_effect=RuntimeError('private credentials')):
        response = client.get('/healthz')
    assert response.status_code == 503
    assert response.json == {'status': 'unavailable'}
    assert b'private credentials' not in response.data
