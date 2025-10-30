# util/send_test_mail.py
import argparse
from .send_mail import MailMessage, send_email, MailSendError
from dotenv import load_dotenv
load_dotenv()
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True, help="カンマ区切り: a@x,b@y")
    p.add_argument("--subject", default="動作確認メール")
    p.add_argument("--text", default="このメールはテスト送信です。")
    p.add_argument("--html", default=None)
    args = p.parse_args()

    to_list = [s.strip() for s in args.to.split(",") if s.strip()]
    try:
        mid = send_email(MailMessage(to=to_list, subject=args.subject, text=args.text, html=args.html))
        print("OK:", mid)
    except MailSendError as e:
        print("ERROR:", e)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
