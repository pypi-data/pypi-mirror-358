"""Convenient shortcuts for interacting with Litebase APIs."""

from .client import Client

# Create a global default client instance so that ``litebaseio.stream`` and
# ``litebaseio.storage`` can be used without manual client management.
_client = Client()

# Public API shortcuts
stream = _client.stream


def storage(name: str):
    """Return a :class:`Storage` interface for the given namespace."""

    return _client.storage(name)


# If users want, they can still manually import ``Client`` class
__all__ = ["Client", "stream", "storage"]
