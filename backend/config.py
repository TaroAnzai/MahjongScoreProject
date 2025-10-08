# config.py

import os
from dotenv import load_dotenv
import secrets


# FLASK_ENV の値に応じて .env を読み込む
env_name = os.getenv("FLASK_ENV", "development")
print("env_name:", env_name)

if env_name == "production":
    load_dotenv(".env.production")
elif env_name == "test":
    load_dotenv(".env.test")
else:
    load_dotenv(".env") #開発用

print("CORS_ORIGINS:", os.getenv("CORS_ORIGINS"))
print("SESSION_COOKIE_NAME:", os.getenv("SESSION_COOKIE_NAME"))

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

    # CORS
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
    CORS_SUPPORTS_CREDENTIALS = True

    # Session / Cookie
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "None")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1")
    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "session")

    # Debug / Testing flags
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
    TESTING = os.getenv("TESTING", "False").lower() in ("true", "1")

    # OpenAPI / Swagger
    API_TITLE = os.getenv("API_TITLE", "Mahjong Score API")
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    OPENAPI_VERSION = os.getenv("OPENAPI_VERSION", "3.0.3")
    OPENAPI_URL_PREFIX = os.getenv("OPENAPI_URL_PREFIX", "/")
    OPENAPI_JSON_PATH = os.getenv("OPENAPI_JSON_PATH", "openapi.json")
    OPENAPI_REDOC_PATH = os.getenv("OPENAPI_REDOC_PATH", "/redoc")
    OPENAPI_REDOC_URL = os.getenv(
        "OPENAPI_REDOC_URL",
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH = os.getenv("OPENAPI_SWAGGER_UI_PATH", "/swagger-ui")
    OPENAPI_SWAGGER_UI_URL = os.getenv(
        "OPENAPI_SWAGGER_UI_URL",
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
