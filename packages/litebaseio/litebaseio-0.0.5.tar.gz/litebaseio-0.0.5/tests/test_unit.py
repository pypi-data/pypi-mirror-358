import httpx
import pytest

from litebaseio import Client
from litebaseio.storage import Storage
from litebaseio.stream import Stream


def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("LITE_API_KEY", raising=False)
    with pytest.raises(ValueError):
        Client()


def test_client_uses_env_key(monkeypatch):
    monkeypatch.setenv("LITE_API_KEY", "dummy-key")
    c = Client()
    try:
        assert c._api_key == "dummy-key"
    finally:
        c.close()


def test_storage_head():
    def handler(request):
        assert request.url.path == "/v4/storage/test/key"
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="https://api.test")
    store = Storage(client, "test")
    assert store.head("key") is True


def test_stream_commit():
    def handler(request):
        assert request.method == "POST"
        assert request.url.path == "/v4/stream/test"
        return httpx.Response(200, json={"tx": 1, "duration": "1ms"})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="https://api.test")
    stream = Stream(client)

    resp = stream.commit("test", b"payload")
    assert resp.tx == 1
