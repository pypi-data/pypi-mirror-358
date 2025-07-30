import json
from typing import Any, Dict, List, Optional

import httpx

from .models import StorageReadResponse, StorageWriteResponse


class Storage:
    """Litebase Storage client with clean, type-safe DX (sync version).

    Automatically infers format on ``set()``:
      - ``dict``, ``list``, ``int``, ``float``, ``bool``, ``None`` → JSON
      - ``str`` → UTF-8 text
      - ``bytes`` → raw binary

    Always returns ``bytes`` on ``get()``, with decoding helpers:
      - ``as_json(bytes)`` → Python object
      - ``as_text(bytes)`` → str
      - ``as_binary(bytes)`` → bytes
    """

    def __init__(self, client: httpx.Client, namespace: str) -> None:
        self._client = client
        self._namespace = namespace

    def set(self, key: str, value: Any) -> StorageWriteResponse:
        """Store a value at the given key. Format is inferred from type."""
        if isinstance(value, bytes):
            content = value
            content_type = "application/octet-stream"
        elif isinstance(value, str):
            content = value.encode("utf-8")
            content_type = "text/plain"
        elif isinstance(value, (dict, list, int, float, bool)) or value is None:
            content = json.dumps(value).encode("utf-8")
            content_type = "application/json"
        else:
            raise TypeError(f"Unsupported type: {type(value)}")

        resp = self._client.post(
            f"/v4/storage/{self._namespace}/key",
            params={"key": key},
            content=content,
            headers={"Content-Type": content_type},
        )
        resp.raise_for_status()
        return StorageWriteResponse.model_validate(resp.json())

    def get(self, key: str, tx: Optional[int] = None) -> bytes:
        """Retrieve raw bytes stored at the given key."""
        params = {"key": key}
        if tx is not None:
            params["tx"] = tx

        resp = self._client.get(f"/v4/storage/{self._namespace}/key", params=params)
        resp.raise_for_status()
        return resp.content

    def head(self, key: str, tx: Optional[int] = None) -> bool:
        """Check if a key exists."""
        params = {"key": key}
        if tx is not None:
            params["tx"] = tx

        resp = self._client.head(f"/v4/storage/{self._namespace}/key", params=params)
        return resp.status_code == 200

    def delete(self, key: str) -> StorageWriteResponse:
        """Delete a key."""
        resp = self._client.delete(f"/v4/storage/{self._namespace}/key", params={"key": key})
        resp.raise_for_status()
        return StorageWriteResponse.model_validate(resp.json())

    def read(self, keys: List[str], tx: Optional[int] = None) -> StorageReadResponse:
        """Batch-read values for multiple keys. Returns ``StorageReadResponse``."""
        payload: Dict[str, Any] = {"keys": keys}
        if tx is not None:
            payload["tx"] = tx

        resp = self._client.post(f"/v4/storage/{self._namespace}/read", json=payload)
        resp.raise_for_status()
        return StorageReadResponse.model_validate(resp.json())

    def write(self, records: List[Dict[str, Any]]) -> StorageWriteResponse:
        """Batch-write multiple records, each a dict with ``key`` and ``value``."""
        encoded_records = []
        for record in records:
            key = record["key"]
            value = record["value"]
            if isinstance(value, bytes):
                value_str = value.decode("latin1")  # safe binary pass-through
            elif isinstance(value, str):
                value_str = value
            elif isinstance(value, (dict, list, int, float, bool)) or value is None:
                value_str = json.dumps(value)
            else:
                raise TypeError(f"Unsupported value type: {type(value)}")
            encoded_records.append({"key": key, "value": value_str})

        resp = self._client.post(f"/v4/storage/{self._namespace}/write", json=encoded_records)
        resp.raise_for_status()
        return StorageWriteResponse.model_validate(resp.json())

    # ───────────────────────
    # Decoding Helpers
    # ───────────────────────

    def as_json(self, raw: bytes) -> Any:
        """Decode raw bytes as JSON (utf-8) and return the parsed Python object."""
        return json.loads(raw.decode("utf-8"))

    def as_text(self, raw: bytes) -> str:
        """Decode raw bytes as UTF-8 text."""
        return raw.decode("utf-8")

    def as_binary(self, raw: bytes) -> bytes:
        """Return raw bytes unchanged."""
        return raw
