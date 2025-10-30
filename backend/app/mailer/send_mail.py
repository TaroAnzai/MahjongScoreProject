# app/util/mailer.py
"""
汎用メール送信ユーティリティ（SMTP）
- 依存：標準ライブラリのみ（smtplib, email.*）
- 環境変数：
    SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
    MAIL_FROM, MAIL_REPLY_TO, MAIL_RETURN_PATH
    SMTP_TIMEOUT
- 使い方：
    from app.util.mailer import MailMessage, send_email
    send_email(MailMessage(to=["user@example.com"], subject="Hello", text="Hi"))
"""

from __future__ import annotations

import os
import smtplib
import socket
from dataclasses import dataclass
from typing import List, Optional

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid


class MailSendError(Exception):
    """メール送信に失敗した場合に送出される例外。"""


@dataclass
class MailMessage:
    """
    送信メッセージ定義。

    Attributes:
        to: 宛先（必須）
        subject: 件名（必須）
        text: プレーンテキスト本文
        html: HTML本文（任意）
        reply_to: 返信先（"Name <addr>" または "addr"）
        cc: Cc 宛先
        bcc: Bcc 宛先（ヘッダには含めない）
    """
    def __init__(
        self,
        to: List[str],                 # ✅ list[str] に統一
        subject: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ):
        self.to = to
        self.subject = subject
        self.text = text
        self.html = html
        self.reply_to = reply_to
        self.cc = cc or []
        self.bcc = bcc or []


def _fmt(addr: str) -> str:
    """'表示名 <addr>' または 'addr' をRFC 2047に則って整形。"""
    if "<" in addr and ">" in addr:
        name, email = addr.split("<", 1)
        return formataddr((str(Header(name.strip(), "utf-8")), email.strip(" >")))
    return addr


def _connect() -> smtplib.SMTP:
    """SMTPへ接続して、必要に応じてSTARTTLS/LOGINまで実施して返す。"""
    host = os.getenv("SMTP_HOST")
    if not host:
        raise MailSendError("SMTP_HOST is not configured.")

    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USERNAME")
    pw = os.getenv("SMTP_PASSWORD", "")
    timeout = int(os.getenv("SMTP_TIMEOUT", "30"))
    print(f"Connecting to {host}:{port}... (user={user}) password={pw}")
    try:
        if port == 465:
            smtp = smtplib.SMTP_SSL(host, port, timeout=timeout)
        else:
            smtp = smtplib.SMTP(host, port, timeout=timeout)
            smtp.ehlo()
            if smtp.has_extn("STARTTLS"):
                smtp.starttls()
                smtp.ehlo()

        if user:
            smtp.login(user, pw)

        return smtp
    except (socket.timeout, smtplib.SMTPException) as e:
        raise MailSendError(f"SMTP connect/login failed: {e}") from e


def send_email(msg: MailMessage) -> str:
    """
    メールを送信する。
    戻り値: provider_message_id（SMTPでは固定 'smtp:ok'）

    例外:
        MailSendError: 接続/送信/設定不備などの失敗時
    """
    if not msg.to:
        raise MailSendError("No recipients: 'to' is empty.")

    mail_from = os.getenv("MAIL_FROM") or os.getenv("SMTP_USERNAME")
    if not mail_from:
        raise MailSendError("MAIL_FROM or SMTP_USERNAME must be configured.")
    reply_to = msg.reply_to or os.getenv("MAIL_REPLY_TO")
    return_path = os.getenv("MAIL_RETURN_PATH") or mail_from

    # メッセージ構築（alternative: text + html）
    m = MIMEMultipart("alternative")
    m["Subject"] = str(Header(msg.subject, "utf-8"))
    m["From"] = _fmt(mail_from)
    m["To"] = ", ".join(_fmt(a) for a in msg.to)
    if msg.cc:
        m["Cc"] = ", ".join(_fmt(a) for a in msg.cc)
    if reply_to:
        m["Reply-To"] = _fmt(reply_to)
    m["Message-ID"] = make_msgid()

    # 本文
    m.attach(MIMEText(msg.text or "", "plain", "utf-8"))
    if msg.html:
        m.attach(MIMEText(msg.html, "html", "utf-8"))

    # 実際に送る宛先（Bcc含む）
    rcpt = list(msg.to) + (msg.cc or []) + (msg.bcc or [])

    try:
        smtp = _connect()
        smtp.sendmail(return_path, rcpt, m.as_string())
        smtp.quit()
        return "smtp:ok"
    except Exception as e:
        raise MailSendError(f"Failed to send email to {rcpt}: {e}") from e
