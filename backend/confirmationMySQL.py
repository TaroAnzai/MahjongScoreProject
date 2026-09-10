"""Read-only connection check using the same DATABASE_URL as the application."""
from sqlalchemy import create_engine, text

from config import Config

if __name__ == "__main__":
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    with engine.connect() as connection:
        print("接続成功：", connection.execute(text("SELECT DATABASE()")).scalar())
