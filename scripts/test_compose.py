"""Validate merged Compose security boundaries without starting any containers."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def config(production):
    command = ['docker', 'compose', '--env-file', '.env.example', '-f', 'compose.yaml']
    command += ['-f', 'compose.production.yaml' if production else 'compose.override.yaml']
    environment = {**os.environ, 'BACKEND_PORT': '15080'}
    if production:
        environment['DATABASE_URL'] = 'mysql+pymysql://user:password@common-mysql:3306/mahjongscore'
    result = subprocess.run(command + ['config', '--format', 'json'], cwd=ROOT,
                            env=environment,
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_production_boundaries():
    model = config(True)
    services = model['services']
    assert set(services) == {'api', 'redis', 'celery_worker', 'celery_beat'}
    assert 'db_data' not in model.get('volumes', {})
    for service in services.values():
        assert service['restart'] == 'unless-stopped'
        assert not any(v['type'] == 'bind' for v in service.get('volumes', []))
    for name in ('redis', 'celery_worker', 'celery_beat'):
        assert not services[name].get('ports')
    assert all(p['host_ip'] == '127.0.0.1' for p in services['api']['ports'])
    for name in ('api', 'celery_worker', 'celery_beat'):
        assert '@common-mysql:3306/' in services[name]['environment']['DATABASE_URL']
        assert 'common-db-network' in services[name]['networks']
        assert 'db' not in services[name].get('depends_on', {})
        assert services[name]['depends_on']['redis']['condition'] == 'service_healthy'


def test_development_services():
    model = config(False)
    services = model['services']
    assert {'mitmproxy', 'mailhog'} <= services.keys()
    assert 'db' in services
    assert 'db_data' in model['volumes']
    assert services['db']['volumes'][0]['source'] == 'db_data'
    assert '--reload' in services['api']['command']
    assert 'frontend' not in services
    for name in ('api', 'celery_worker', 'celery_beat'):
        assert '@db:3306/' in services[name]['environment']['DATABASE_URL']
        assert services[name]['depends_on']['db']['condition'] == 'service_healthy'
