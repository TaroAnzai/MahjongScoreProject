from email import message_from_string
from email.header import decode_header, make_header
from email.utils import parseaddr

from app.mailer import send_mail


class DummySMTP:
    def __init__(self):
        self.sent = None
        self.quit_called = False

    def sendmail(self, sender, recipients, message):
        self.sent = (sender, recipients, message)

    def quit(self):
        self.quit_called = True


def test_send_email_sets_sender_display_name(monkeypatch):
    smtp = DummySMTP()
    monkeypatch.setenv("MAIL_FROM", "noreply@example.com")
    monkeypatch.setattr(send_mail, "_connect", lambda: smtp)

    result = send_mail.send_email(send_mail.MailMessage(
        to=["user@example.com"],
        subject="Test",
        sender_name="麻雀スコア",
        text="body",
    ))

    message = message_from_string(smtp.sent[2])
    sender_name, sender_address = parseaddr(message["From"])
    assert str(make_header(decode_header(sender_name))) == "麻雀スコア"
    assert sender_address == "noreply@example.com"
    assert result == "smtp:ok"
    assert smtp.quit_called is True
