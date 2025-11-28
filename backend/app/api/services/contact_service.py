# app/services/contact_service.py

from app import db
from app.models import Contact, ContactStatus
from sqlalchemy.exc import SQLAlchemyError
from app.service_errors import ServiceNotFoundError, ServicePermissionError
from app.utils.recaptcha import verify_recaptcha

class ContactService:
    """Contact（問い合わせ）に関するビジネスロジック"""

    @staticmethod
    def create_contact(data, ip_address=None, user_agent=None):
        """
        問い合わせ作成（POST）
        """
            # 🟩 reCAPTCHA（最初にチェック）
        recaptcha = data.get("recaptcha_token")
        if not recaptcha or not verify_recaptcha(recaptcha, "create_contact"):
          raise ServicePermissionError("不正なアクセスが検出されました。（reCAPTCHA）")
        data.pop("recaptcha_token", None)
        try:
            contact = Contact(
                name=data["name"],
                email=data["email"],
                subject=data["subject"],
                message=data["message"],
                status=ContactStatus.RECEIVED,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.session.add(contact)
            db.session.commit()
            return contact
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_contact(contact_id):
        """
        1件取得（GET /contact/<id>）
        """
        contact = Contact.query.get(contact_id)
        if not contact:
            return None
        return contact

    @staticmethod
    def list_contacts():
        """
        全件取得（GET /contact）
        """
        return Contact.query.order_by(Contact.created_at.desc()).all()

    @staticmethod
    def update_contact(contact_id, data):
        """
        任意の項目を部分更新（PATCH）
        - name / email / subject / message / status
        """
        contact = Contact.query.get(contact_id)
        if not contact:
            raise ServiceNotFoundError(f"Contact not found with id: {contact_id}")

        try:
            # 文字列項目の更新
            for field in ["name", "email", "subject", "message"]:
                if field in data and data[field] is not None:
                    setattr(contact, field, data[field])

            # ステータスの更新（EnumField がバリデーション済み）
            if "status" in data and data["status"] is not None:
                contact.status = data["status"]

            db.session.commit()
            return contact

        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_contact(contact_id):
        """
        削除（DELETE /contact/<id>）
        """
        contact = Contact.query.get(contact_id)
        if not contact:
            raise ServiceNotFoundError(f"Contact not found with id: {contact_id}")

        db.session.delete(contact)
        db.session.commit()
        return True
