import importlib.util
import json
import sys
import types
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace


mitmproxy_module = types.ModuleType("mitmproxy")
mitmproxy_module.http = SimpleNamespace(
    HTTPFlow=object,
    Response=SimpleNamespace(make=lambda status, body, headers: SimpleNamespace(
        status_code=status, raw_content=body, headers=headers
    )),
)
sys.modules.setdefault("mitmproxy", mitmproxy_module)

spec = importlib.util.spec_from_file_location(
    "network_fault", Path(__file__).with_name("network_fault.py")
)
network_fault = importlib.util.module_from_spec(spec)
spec.loader.exec_module(network_fault)


class FakeResponse:
    def __init__(self, body, status_code=200):
        self.raw_content = json.dumps(body).encode()
        self.status_code = status_code
        self.headers = {"Content-Type": "application/json", "X-Test": "kept"}

    @property
    def content(self):
        return self.raw_content

    @content.setter
    def content(self, value):
        self.raw_content = value
        self.headers["Content-Length"] = str(len(value))


def make_flow(request_body, response_body, path=None):
    request_content = json.dumps(request_body).encode()
    return SimpleNamespace(
        request=SimpleNamespace(
            method="POST",
            path=path or network_fault.PENDING_STATUS_BATCH_PATH,
            raw_content=request_content,
            content=request_content,
        ),
        response=FakeResponse(response_body),
        killed=False,
        kill=lambda: None,
    )


def result_body(flow):
    return json.loads(flow.response.raw_content)


def test_token_override_changes_only_target_and_removes_owner_link():
    addon = network_fault.NetworkFaultAddon()
    addon.add_expired(token="token-b", client_id=None)
    flow = make_flow(
        {"items": [
            {"client_id": "0", "token": "token-a"},
            {"client_id": "1", "token": "token-b"},
            {"client_id": "2", "token": "token-c"},
        ]},
        {"results": [
            {"client_id": "0", "status": "pending"},
            {"client_id": "1", "status": "ready", "owner_link": "owner"},
            {"client_id": "2", "status": "ready", "owner_link": "unchanged"},
        ]},
    )

    addon.response(flow)

    assert result_body(flow) == {"results": [
        {"client_id": "0", "status": "pending"},
        {"client_id": "1", "status": "expired"},
        {"client_id": "2", "status": "ready", "owner_link": "unchanged"},
    ]}
    assert flow.response.headers["Content-Type"] == "application/json"
    assert flow.response.headers["X-Test"] == "kept"


def test_client_id_override_and_reset():
    addon = network_fault.NetworkFaultAddon()
    addon.add_expired(token=None, client_id="1")
    request = {"items": [{"client_id": "1", "token": "token-b"}]}
    response = {"results": [{"client_id": "1", "status": "pending"}]}
    flow = make_flow(request, response)
    addon.response(flow)
    assert result_body(flow)["results"][0]["status"] == "expired"

    addon.reset_expired()
    flow = make_flow(request, response)
    original = flow.response.raw_content
    addon.response(flow)
    assert flow.response.raw_content == original


def test_override_is_skipped_for_other_modes_and_paths():
    for mode in ("offline", "500"):
        addon = network_fault.NetworkFaultAddon()
        addon.add_expired(token=None, client_id="1")
        addon.set_mode(mode)
        flow = make_flow(
            {"items": [{"client_id": "1", "token": "token"}]},
            {"results": [{"client_id": "1", "status": "pending"}]},
        )
        original = flow.response.raw_content
        addon.response(flow)
        assert flow.response.raw_content == original

    addon = network_fault.NetworkFaultAddon()
    addon.add_expired(token=None, client_id="1")
    flow = make_flow(
        {"items": [{"client_id": "1", "token": "token"}]},
        {"results": [{"client_id": "1", "status": "pending"}]},
        path="/api/v2/groups:batch-get",
    )
    original = flow.response.raw_content
    addon.response(flow)
    assert flow.response.raw_content == original


def test_invalid_json_does_not_raise_or_change_response():
    addon = network_fault.NetworkFaultAddon()
    addon.add_expired(token=None, client_id="1")
    flow = make_flow({}, {"results": []})
    flow.request.raw_content = b"not-json"
    flow.request.content = b"not-json"
    original = flow.response.raw_content
    addon.response(flow)
    assert flow.response.raw_content == original

    flow = make_flow({"items": []}, {})
    flow.response.raw_content = b"not-json"
    addon.response(flow)
    assert flow.response.raw_content == b"not-json"


def request_json(url, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def test_control_api_and_existing_modes(monkeypatch):
    monkeypatch.setattr(network_fault, "CONTROL_HOST", "127.0.0.1")
    monkeypatch.setattr(network_fault, "CONTROL_PORT", 0)
    addon = network_fault.NetworkFaultAddon()
    addon.running()
    base = f"http://127.0.0.1:{addon._server.server_address[1]}"
    try:
        assert request_json(base + "/pending-status") == (
            200, {"expiredTokens": [], "expiredClientIds": []}
        )
        assert request_json(
            base + "/pending-status/expired", "POST", {"client_id": "1"}
        ) == (200, {"status": "ok"})
        assert request_json(base + "/pending-status")[1]["expiredClientIds"] == ["1"]

        invalid_bodies = ({}, {"token": ""}, {"token": "a", "client_id": "1"})
        for body in invalid_bodies:
            assert request_json(base + "/pending-status/expired", "POST", body)[0] == 400

        assert request_json(base + "/pending-status/reset", "POST", {}) == (
            200, {"status": "ok"}
        )
        assert request_json(base + "/pending-status")[1]["expiredClientIds"] == []

        assert request_json(base + "/mode") == (200, {"mode": "normal"})
        for mode in ("offline", "500", "normal"):
            assert request_json(base + f"/mode/{mode}", "POST", {}) == (
                200, {"mode": mode}
            )
    finally:
        addon.done()


def test_existing_request_modes(monkeypatch):
    addon = network_fault.NetworkFaultAddon()
    normal = make_flow({}, {})
    addon.request(normal)
    assert normal.response.status_code == 200

    offline = make_flow({}, {})
    monkeypatch.setattr(offline, "kill", lambda: setattr(offline, "killed", True))
    addon.set_mode("offline")
    addon.request(offline)
    assert offline.killed

    server_error = make_flow({}, {})
    addon.set_mode("500")
    addon.request(server_error)
    assert server_error.response.status_code == 500
