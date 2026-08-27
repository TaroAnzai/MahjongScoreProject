import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from mitmproxy import http

CONTROL_HOST = "0.0.0.0"
CONTROL_PORT = 9099

VALID_MODES = {
    "normal",
    "offline",
    "500",
}

PENDING_STATUS_BATCH_PATH = "/api/v2/groups/request-link/status:batch"


def override_pending_status_response(
    request_body: bytes,
    response_body: bytes,
    expired_tokens: set[str],
    expired_client_ids: set[str],
) -> bytes | None:
    """Return an updated response body, or None when it must be left untouched."""
    try:
        request_json = json.loads(request_body)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        logging.warning("Pending status batch request body is not valid JSON")
        return None

    try:
        response_json = json.loads(response_body)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        logging.warning("Pending status batch response body is not valid JSON")
        return None

    if not isinstance(request_json, dict) or not isinstance(
        request_json.get("items"), list
    ):
        logging.warning("Pending status batch request has no valid items list")
        return None
    if not isinstance(response_json, dict) or not isinstance(
        response_json.get("results"), list
    ):
        logging.warning("Pending status batch response has no valid results list")
        return None

    token_client_ids = set()
    for item in request_json["items"]:
        if not isinstance(item, dict):
            logging.warning("Pending status batch request item has an invalid schema")
            return None
        client_id = item.get("client_id")
        token = item.get("token")
        if not isinstance(client_id, str) or not isinstance(token, str):
            logging.warning("Pending status batch request item has an invalid schema")
            return None
        if token in expired_tokens:
            token_client_ids.add(client_id)

    target_client_ids = expired_client_ids | token_client_ids
    updated = False
    for result in response_json["results"]:
        if not isinstance(result, dict) or not isinstance(
            result.get("client_id"), str
        ) or not isinstance(result.get("status"), str):
            logging.warning("Pending status batch result has an invalid schema")
            return None
        if result["client_id"] in target_client_ids:
            result["status"] = "expired"
            result.pop("owner_link", None)
            updated = True

    if not updated:
        return None
    return json.dumps(response_json, ensure_ascii=False).encode("utf-8")


class NetworkFaultAddon:
    def __init__(self):
        self._mode = "normal"
        self._expired_tokens: set[str] = set()
        self._expired_client_ids: set[str] = set()
        self._lock = threading.Lock()
        self._server: ThreadingHTTPServer | None = None
        self._server_thread: threading.Thread | None = None

    def get_mode(self) -> str:
        with self._lock:
            return self._mode

    def set_mode(self, mode: str) -> bool:
        if mode not in VALID_MODES:
            return False

        with self._lock:
            self._mode = mode

        logging.info("Network fault mode changed to: %s", mode)
        return True

    def get_pending_status(self) -> tuple[list[str], list[str]]:
        with self._lock:
            return sorted(self._expired_tokens), sorted(self._expired_client_ids)

    def add_expired(self, *, token: str | None, client_id: str | None):
        with self._lock:
            if token is not None:
                self._expired_tokens.add(token)
            if client_id is not None:
                self._expired_client_ids.add(client_id)

    def reset_expired(self):
        with self._lock:
            self._expired_tokens.clear()
            self._expired_client_ids.clear()

    def pending_status_snapshot(self) -> tuple[set[str], set[str]]:
        with self._lock:
            return self._expired_tokens.copy(), self._expired_client_ids.copy()

    def running(self):
        addon = self

        class ControlHandler(BaseHTTPRequestHandler):
            def send_json(self, status: int, body: dict):
                data = json.dumps(body).encode("utf-8")

                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def read_json_object(self) -> dict | None:
                try:
                    content_length = int(self.headers.get("Content-Length", ""))
                    body = self.rfile.read(content_length)
                    value = json.loads(body)
                except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                    return None
                return value if isinstance(value, dict) else None

            def do_GET(self):
                if self.path == "/mode":
                    self.send_json(
                        200,
                        {"mode": addon.get_mode()},
                    )
                    return

                if self.path == "/pending-status":
                    tokens, client_ids = addon.get_pending_status()
                    self.send_json(
                        200,
                        {
                            "expiredTokens": tokens,
                            "expiredClientIds": client_ids,
                        },
                    )
                    return

                self.send_json(
                    404,
                    {"error": "Not Found"},
                )

            def do_POST(self):
                if self.path == "/pending-status/expired":
                    body = self.read_json_object()
                    token = body.get("token") if body is not None else None
                    client_id = body.get("client_id") if body is not None else None
                    supplied = (
                        ["token" in body, "client_id" in body]
                        if body is not None
                        else []
                    )
                    value = token if token is not None else client_id
                    if (
                        body is None
                        or sum(supplied) != 1
                        or not isinstance(value, str)
                        or not value
                    ):
                        self.send_json(
                            400,
                            {
                                "error": (
                                    "Specify exactly one non-empty token or client_id"
                                )
                            },
                        )
                        return
                    addon.add_expired(token=token, client_id=client_id)
                    self.send_json(200, {"status": "ok"})
                    return

                if self.path == "/pending-status/reset":
                    if self.read_json_object() is None:
                        self.send_json(400, {"error": "Invalid JSON body"})
                        return
                    addon.reset_expired()
                    self.send_json(200, {"status": "ok"})
                    return

                prefix = "/mode/"

                if not self.path.startswith(prefix):
                    self.send_json(
                        404,
                        {"error": "Not Found"},
                    )
                    return

                mode = self.path[len(prefix) :]

                if not addon.set_mode(mode):
                    self.send_json(
                        400,
                        {
                            "error": "Invalid mode",
                            "validModes": sorted(VALID_MODES),
                        },
                    )
                    return

                self.send_json(
                    200,
                    {"mode": mode},
                )

            def log_message(self, format, *args):
                logging.info(
                    "Control API: " + format,
                    *args,
                )

        self._server = ThreadingHTTPServer(
            (CONTROL_HOST, CONTROL_PORT),
            ControlHandler,
        )

        self._server_thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
        )

        self._server_thread.start()

        logging.info(
            "Network fault control API started on port %d",
            CONTROL_PORT,
        )

    def done(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()

    def request(self, flow: http.HTTPFlow):
        mode = self.get_mode()

        if mode == "normal":
            return

        if mode == "offline":
            flow.kill()
            return

        if mode == "500":
            flow.response = http.Response.make(
                500,
                b'{"message":"Internal Server Error"}',
                {
                    "Content-Type": "application/json",
                },
            )

    def response(self, flow: http.HTTPFlow):
        if self.get_mode() != "normal":
            return
        if (
            flow.request.method != "POST"
            or flow.request.path.split("?", 1)[0] != PENDING_STATUS_BATCH_PATH
            or flow.response is None
            or flow.response.status_code != 200
        ):
            return

        expired_tokens, expired_client_ids = self.pending_status_snapshot()
        if not expired_tokens and not expired_client_ids:
            return

        try:
            updated_body = override_pending_status_response(
                flow.request.content or b"",
                flow.response.content or b"",
                expired_tokens,
                expired_client_ids,
            )
        except ValueError:
            logging.warning("Pending status batch body could not be decoded")
            return
        if updated_body is not None:
            # mitmproxy's content setter updates Content-Length while preserving
            # unrelated response headers, including Content-Type.
            try:
                flow.response.content = updated_body
            except ValueError:
                logging.warning("Pending status batch response could not be encoded")


addons = [
    NetworkFaultAddon(),
]
