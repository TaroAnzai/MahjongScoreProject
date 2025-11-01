# -*- coding: utf-8 -*-
from __future__ import annotations

from celery import shared_task
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, func

from app import create_app
from app.extensions import db
from app.models import GroupCreationToken
import os


@shared_task(
    bind=True,
    name="app.tasks.maintenance_task.delete_expired_group_tokens",
    max_retries=3,
    default_retry_delay=30,  # 秒
)
def delete_expired_group_tokens(self):
    """
    期限切れで未使用のグループ作成トークンを削除する。
    Beat: 5分おき
    """
    app = create_app()
    with app.app_context():
        now = datetime.now(timezone.utc)
        try:
            q = (
                db.session.query(GroupCreationToken)
                .filter(
                    and_(
                        GroupCreationToken.is_used.is_(False),
                        GroupCreationToken.expires_at <= now,
                    )
                )
            )
            to_delete = q.count()
            # まとめてDELETE
            q.delete(synchronize_session=False)
            db.session.commit()

            app.logger.info(
                "[Maintenance] Deleted %s expired group tokens at %s",
                to_delete,
                now.isoformat(),
            )
            return {"deleted": to_delete, "now": now.isoformat()}
        except Exception as e:
            db.session.rollback()
            app.logger.exception(
                "[Maintenance] Failed to delete expired group tokens"
            )
            raise self.retry(exc=e)


@shared_task(
    name="app.tasks.maintenance_task.generate_daily_summary",
)
def generate_daily_summary():
    """
    簡易デイリーサマリー（直近24時間の作成件数など）をログに出す。
    Beat: 24時間おき
    """
    app = create_app()
    with app.app_context():
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=1)

        total_tokens = db.session.query(func.count(GroupCreationToken.id)).scalar() or 0
        new_tokens_24h = (
            db.session.query(func.count(GroupCreationToken.id))
            .filter(GroupCreationToken.created_at >= since)
            .scalar()
            or 0
        )
        expired_24h = (
            db.session.query(func.count(GroupCreationToken.id))
            .filter(
                and_(
                    GroupCreationToken.expires_at >= since,
                    GroupCreationToken.expires_at < now,
                    GroupCreationToken.is_used.is_(False),
                )
            )
            .scalar()
            or 0
        )

        app.logger.info(
            "[DailySummary] %s..%s new_tokens=%d expired_tokens=%d total_tokens=%d",
            since.isoformat(),
            now.isoformat(),
            new_tokens_24h,
            expired_24h,
            total_tokens,
        )

        return {
            "since": since.isoformat(),
            "until": now.isoformat(),
            "new_tokens": int(new_tokens_24h),
            "expired_tokens": int(expired_24h),
            "total_tokens": int(total_tokens),
        }
