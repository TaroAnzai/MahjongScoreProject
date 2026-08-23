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


class NetworkFaultAddon:
    def __init__(self):
        self._mode = "normal"
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

            def do_GET(self):
                if self.path == "/mode":
                    self.send_json(
                        200,
                        {"mode": addon.get_mode()},
                    )
                    return

                self.send_json(
                    404,
                    {"error": "Not Found"},
                )

            def do_POST(self):
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


addons = [
    NetworkFaultAddon(),
]
