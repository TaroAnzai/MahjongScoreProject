# app/auth.py

from flask_login import UserMixin

class PseudoUser(UserMixin):
    def __init__(self, id, edit_key):
        self.id = id
        self.edit_key = edit_key
