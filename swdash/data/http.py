"""Small HTTP helper with sane defaults and a friendly error type."""
from __future__ import annotations

import requests

from swdash.config import HTTP_TIMEOUT

USER_AGENT = "sw-dashboard/1.0 (+https://github.com/mohamednedal/sw-dashboard)"


class DataUnavailable(RuntimeError):
    """Raised when a remote source cannot be reached or returns junk."""


def get_json(url: str, params: dict | None = None, timeout: int = HTTP_TIMEOUT):
    """GET a URL and decode JSON, raising :class:`DataUnavailable` on failure."""
    try:
        resp = requests.get(
            url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT}
        )
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:  # ValueError = bad JSON
        raise DataUnavailable(f"Could not fetch JSON from {url}: {exc}") from exc


def get_text(url: str, timeout: int = HTTP_TIMEOUT) -> str:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        raise DataUnavailable(f"Could not fetch text from {url}: {exc}") from exc


def get_bytes(url: str, params: dict | None = None, timeout: int = HTTP_TIMEOUT) -> bytes:
    try:
        resp = requests.get(
            url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT}
        )
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as exc:
        raise DataUnavailable(f"Could not fetch bytes from {url}: {exc}") from exc
