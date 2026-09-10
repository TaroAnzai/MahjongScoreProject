"""Validate merged Compose security boundaries without starting any containers."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def config(production):
    command = ['docker', 'compose', '--env-file', '.env.example', '-f', 'compose.yaml']
    command += ['-f', 'compose.production.yaml' if production else 'compose.override.yaml']
    result = subprocess.run(command + ['config', '--format', 'json'], cwd=ROOT,
                            env={**os.environ, 'BACKEND_PORT': '15080'},
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_production_boundaries():
    services = config(True)['services']
    assert set(services) == {'api', 'db', 'redis', 'celery_worker', 'celery_beat'}
    for service in services.values():
        assert service['restart'] == 'unless-stopped'
        assert not any(v['type'] == 'bind' for v in service.get('volumes', []))
    for name in ('db', 'redis', 'celery_worker', 'celery_beat'):
        assert not services[name].get('ports')
    assert all(p['host_ip'] == '127.0.0.1' for p in services['api']['ports'])
    for name in ('api', 'celery_worker', 'celery_beat'):
        assert '@db:3306/' in services[name]['environment']['DATABASE_URL']
        for dependency in ('db', 'redis'):
            assert services[name]['depends_on'][dependency]['condition'] == 'service_healthy'


def test_development_services():
    services = config(False)['services']
    assert {'mitmproxy', 'mailhog'} <= services.keys()
    assert '--reload' in services['api']['command']
    assert 'frontend' not in services
