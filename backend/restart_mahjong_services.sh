#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f compose.yaml -f compose.production.yaml restart api celery_worker celery_beat
