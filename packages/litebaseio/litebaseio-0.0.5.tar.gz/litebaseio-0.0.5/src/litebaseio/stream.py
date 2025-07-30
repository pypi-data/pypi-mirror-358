import threading
from typing import Any, Callable, Dict, List, Optional

import httpx

from .models import StreamCommitResponse, StreamEvent, StreamPushResponse


class Stream:
    """Litebase Stream client providing publish, subscribe, and query APIs."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client
        self._handlers: Dict[str, List[Callable[[StreamEvent], None]]] = {}

    # ───────────────────────
    # Sending Events
    # ───────────────────────

    def send(self, stream: str, data: Any) -> StreamPushResponse:
        """Send a single event to a stream. Format is inferred from type."""
        event: Dict[str, Any] = {"stream": stream}

        if isinstance(data, dict):
            event["data"] = data
        elif isinstance(data, str):
            event["data"] = {"text": data}
        elif isinstance(data, bytes):
            event["data"] = {"binary": data.decode("latin1")}
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        return self.push([event])

    def push(self, events: List[Dict[str, Any]]) -> StreamPushResponse:
        """Push multiple events to one or more streams."""
        resp = self._client.post("/v4/stream", json=events)
        resp.raise_for_status()
        return StreamPushResponse.model_validate(resp.json())

    def commit(self, stream: str, payload: bytes) -> StreamCommitResponse:
        """Manually commit a pre-encoded batch of events to the stream."""
        resp = self._client.post(f"/v4/stream/{stream}", content=payload)
        resp.raise_for_status()
        return StreamCommitResponse.model_validate(resp.json())

    # ───────────────────────
    # Receiving Events
    # ───────────────────────

    def on(self, stream: str) -> Callable[[Callable[[StreamEvent], None]], Callable[[StreamEvent], None]]:
        """Register a handler for incoming events on a stream."""

        def decorator(func: Callable[[StreamEvent], None]) -> Callable[[StreamEvent], None]:
            self._handlers.setdefault(stream, []).append(func)
            return func

        return decorator

    def subscribe(self, stream: str, start_tx: Optional[int] = None) -> None:
        """Subscribe to a stream and dispatch incoming events to registered handlers."""
        params: Dict[str, Any] = {}
        if start_tx is not None:
            params["start_tx"] = start_tx

        def _listen() -> None:
            with self._client.stream("GET", f"/v4/stream/{stream}", params=params, timeout=None) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line and line.startswith("data:"):
                        payload = line[5:].strip()
                        event = StreamEvent.model_validate_json(payload)
                        self._dispatch(stream, event)

        threading.Thread(target=_listen, daemon=True).start()

    def _dispatch(self, stream: str, event: StreamEvent) -> None:
        """Internal dispatcher to call registered handlers for a stream."""
        for handler in self._handlers.get(stream, []):
            try:
                handler(event)
            except Exception:
                pass  # Optional: log or capture exception

    # ───────────────────────
    # Querying Events
    # ───────────────────────

    def get_event(self, stream: str, tx: int) -> Dict[str, Any]:
        """Fetch a specific event payload by transaction ID."""
        resp = self._client.get(f"/v4/stream/{stream}/{tx}")
        resp.raise_for_status()
        return resp.json()

    def list_events(
        self,
        stream: str,
        start_tx: Optional[int] = None,
        end_tx: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[StreamEvent]:
        """List committed events from a stream."""
        params: Dict[str, Any] = {}
        if start_tx is not None:
            params["start_tx"] = start_tx
        if end_tx is not None:
            params["end_tx"] = end_tx
        if limit is not None:
            params["limit"] = limit

        resp = self._client.get(f"/v4/stream/{stream}/events", params=params)
        resp.raise_for_status()
        return [StreamEvent.model_validate(e) for e in resp.json() or []]
