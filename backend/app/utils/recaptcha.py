import os

import requests


def verify_recaptcha(token: str, action: str = "create_group") -> bool:
    secret = os.getenv("RECAPTCHA_SECRET_KEY")
    if not secret:
        raise RuntimeError("RECAPTCHA_SECRET_KEY is not set")

    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret, "response": token},
        timeout=5,
    ).json()

    # success でない → bot
    if not response.get("success"):
        return False

    # action mismatch → bot
    if response.get("action") != action:
        return False

    # スコアが低い → bot
    return response.get("score", 0) >= 0.7
