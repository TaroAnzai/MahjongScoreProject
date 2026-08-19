# ------------------------------------------------------------
# RateLimit: /api/groups/request-link (3 per hour; 10 per day)
# ------------------------------------------------------------


def test_request_group_creation_rate_limit(client):
    """
    3回までは成功、4回目は 429 Too Many Requests を返す。
    """

    payload = {
        "name": "TestGroup",
        "email": "user@example.com",
        "timezone": "Asia/Tokyo",
        "recaptcha_token": "test-token-ok",  # reCAPTCHA はテストでは mock 推奨
    }

    # --- 1️⃣ 1回目 OK ---
    r1 = client.post("/api/groups/request-link", json=payload)
    assert r1.status_code == 200
    assert "expires_at" in r1.get_json()

    # --- 2️⃣ 2回目 OK ---
    r2 = client.post("/api/groups/request-link", json=payload)
    assert r2.status_code == 200

    # --- 3️⃣ 3回目 OK ---
    r3 = client.post("/api/groups/request-link", json=payload)
    assert r3.status_code == 200

    # --- 4️⃣ 4回目 → RateLimitExceeded (429) ---
    r4 = client.post("/api/groups/request-link", json=payload)

    assert r4.status_code == 429

    data = r4.get_json()

    # あなたの format_error_response に従う
    assert data["code"] == 429
    assert data["status"] == "Too Many Requests"
    assert "errors" in data
    assert "json" in data["errors"]
    assert "message" in data["errors"]["json"]
    assert isinstance(data["errors"]["json"]["message"], list)

    # Retry-After がヘッダに含まれること
    assert "Retry-After" in r4.headers
