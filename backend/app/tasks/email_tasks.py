from celery import shared_task

from app.mailer.send_mail import MailMessage, MailSendError, send_email
from app.tasks.render_mail import render_mail_template


@shared_task
def send_group_creation_email_task(
    email: str, url: str, group_name: str, expires_at: str
):
    print("send_group_creation_email_task")
    """Celeryジョブ: グループ作成メール送信"""
    context = {
        "email": email,
        "url": url,
        "group_name": group_name,
        "expires_at": expires_at,
    }
    subject = f"Group Creation Link / グループ作成リンク({group_name})"
    text_body, html_body = render_mail_template("group_creation", **context)

    to_list = [email]
    mail_message = MailMessage(
        to=to_list,
        subject=subject,
        sender_name="麻雀集計ScoreBoard",
        text=text_body,
        html=html_body,
    )
    try:
        mid = send_email(mail_message)
        print("OK:", mid)
    except MailSendError as e:
        print("ERROR:", e)
        raise SystemExit(1)
