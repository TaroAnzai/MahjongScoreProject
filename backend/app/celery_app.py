from celery import Celery
import os

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery = Celery("mahjongscore", broker=broker_url, backend=backend_url)
celery.conf.task_default_queue = "mahjong_tasks"

@celery.task
def send_group_mail(email, url):
    print(f"Sending mail to {email} with link: {url}")
    # 実際のメール送信ロジックは MailService で実装
    return True
