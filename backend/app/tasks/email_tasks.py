from celery import shared_task
from flask import current_app
from app.mailer.send_mail import MailMessage, send_email, MailSendError

@shared_task
def send_group_creation_email_task(email: str, token: str):
    """Celeryジョブ: グループ作成メール送信"""
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    link = f"{frontend_url}/groups/create/{token}"

    subject = "グループ作成リンク"
    body = f"以下のリンクからグループ作成を完了してください（30分以内にアクセスしてください）:\n\n{link}"
    html = body

    to_list = [email]
    mail_message =MailMessage(to=to_list, subject=subject, text=body, html=html)
    send_email(mail_message)
