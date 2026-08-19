# backend/app/celery_app.py
import os
from datetime import timedelta

from celery import Celery
from dotenv import load_dotenv

env_name = os.getenv("FLASK_ENV", "development")
print("env_name:", env_name)

if env_name == "production":
    load_dotenv(".env.production")
elif env_name == "test":
    load_dotenv(".env.test")
else:
    load_dotenv(".env.development")  # 開発用


def make_celery():
    """Flaskに依存しないCeleryインスタンスを作成"""
    celery = Celery(__name__)
    # .envから直接取得
    celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    celery.conf.result_backend = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
    )
    celery.conf.task_serializer = "json"
    celery.conf.result_serializer = "json"
    celery.conf.accept_content = ["json"]
    celery.conf.timezone = os.getenv("CELERY_TIMEZONE", "Asia/Tokyo")
    celery.conf.enable_utc = False
    celery.conf.broker_connection_retry_on_startup = True

    # ---- 明示的にインポート（確実に登録させる） ----
    celery.conf.imports = (
        "app.tasks.email_tasks",
        "app.tasks.maintenance_task",
    )
    # 🔸 Celery Beat スケジュール定義
    celery.conf.beat_schedule = {
        "delete-expired-group-tokens-every-5-mins": {
            "task": "app.tasks.maintenance_task.delete_expired_group_tokens",
            "schedule": timedelta(minutes=5),
        },
        "nightly-summary-at-midnight": {
            "task": "app.tasks.maintenance_task.generate_daily_summary",
            "schedule": timedelta(hours=24),
            "options": {"expires": 30},  # 古いジョブの無効化時間
        },
    }

    return celery


# Celeryインスタンス作成
celery = make_celery()
