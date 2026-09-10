"""Load only the repository root .env for local commands.

Containers receive their configuration from Compose; the file is never baked in.
Existing process environment always takes precedence.
"""
from pathlib import Path

from dotenv import load_dotenv


def load_environment():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
