# app/services/group_service.py
import secrets
from datetime import datetime, timezone
from app.models import db, Group


def get_all_groups():
    return Group.query.all()


def get_group(group_id: int):
    return Group.query.get_or_404(group_id)


def create_group(data: dict):
    group = Group(
        name=data["name"],
        description=data.get("description", ""),
        group_key=secrets.token_urlsafe(12),
        edit_key=secrets.token_urlsafe(12),
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(group)
    db.session.commit()
    return group


def update_group(group_id: int, data: dict):
    group = get_group(group_id)
    if "name" in data:
        group.name = data["name"]
    if "description" in data:
        group.description = data["description"]
    db.session.commit()
    return group


def delete_group(group_id: int):
    group = get_group(group_id)
    db.session.delete(group)
    db.session.commit()
    return True
