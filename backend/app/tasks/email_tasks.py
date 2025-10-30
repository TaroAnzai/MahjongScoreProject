from celery import shared_task
from flask import current_app
from app.mailer.send_mail import MailMessage, send_email, MailSendError

@shared_task
def send_group_creation_email_task(email: str, url: str):
    """Celeryジョブ: グループ作成メール送信"""

    subject = "グループ作成リンク"
    body = f"以下のリンクからグループ作成を完了してください（30分以内にアクセスしてください）:\n\n{url}"
    html = body

    to_list = [email]
    mail_message =MailMessage(to=to_list, subject=subject, text=body, html=html)
    send_email(mail_message)
