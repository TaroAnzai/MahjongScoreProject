# backend/tests/contacts/test_contact_api.py

from app import db
from app.models import Contact, ContactStatus


# ===============================
# CREATE (POST)
# ===============================
def test_create_contact(client):
    payload = {
        "name": "Taro",
        "email": "taro@example.com",
        "subject": "問い合わせの件",
        "message": "テストメッセージです。",
        "recaptcha_token": "dummy-token"
    }

    res = client.post("/api/contacts/", json=payload)

    assert res.status_code == 201
    data = res.get_json()

    assert data["name"] == "Taro"
    assert data["email"] == "taro@example.com"
    assert data["status"] == ContactStatus.RECEIVED.value


# ===============================
# LIST (GET)
# ===============================
def test_list_contacts(client):
    db.session.add(Contact(
        name="User1",
        email="u1@example.com",
        subject="sub",
        message="msg",
        status=ContactStatus.RECEIVED,
    ))
    db.session.commit()

    res = client.get("/api/contacts/")
    assert res.status_code == 200

    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "User1"


# ===============================
# GET ONE
# ===============================
def test_get_contact(client):
    contact = Contact(
        name="User2",
        email="u2@example.com",
        subject="hello",
        message="content",
        status=ContactStatus.RECEIVED,
    )
    db.session.add(contact)
    db.session.commit()

    res = client.get(f"/api/contacts/{contact.id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["email"] == "u2@example.com"


def test_get_contact_not_found(client):
    res = client.get("/api/contacts/9999")
    assert res.status_code == 404


# ===============================
# UPDATE (PATCH)
# ===============================
def test_update_contact_status(client):
    contact = Contact(
        name="User3",
        email="u3@example.com",
        subject="test",
        message="body",
        status=ContactStatus.RECEIVED,
    )
    db.session.add(contact)
    db.session.commit()

    payload = {"status": "in_progress"}

    res = client.patch(f"/api/contacts/{contact.id}", json=payload)
    print(res.get_json())
    assert res.status_code == 200

    data = res.get_json()
    assert data["status"] == "in_progress"


def test_update_contact_not_found(client):
    res = client.patch("/api/contacts/9999", json={"status": "answered"})
    assert res.status_code == 404


# ===============================
# DELETE
# ===============================
def test_delete_contact(client):
    contact = Contact(
        name="User4",
        email="u4@example.com",
        subject="aaa",
        message="bbb",
        status=ContactStatus.RECEIVED,
    )
    db.session.add(contact)
    db.session.commit()

    res = client.delete(f"/api/contacts/{contact.id}")
    assert res.status_code == 204

    # 削除確認
    res2 = client.get(f"/api/contacts/{contact.id}")
    assert res2.status_code == 404


def test_delete_contact_not_found(client):
    res = client.delete("/api/contacts/9999")
    assert res.status_code == 404
