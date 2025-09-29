# config.py

import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login
    SESSION_COOKIE_NAME = 'mahjong_session'
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True  # HTTPS通信のみでCookieを送信

    # CORS
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ORIGINS = ["https://localhost:5173","http://localhost:5173", "https://anzai-home.com"]
