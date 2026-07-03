"""Lightweight in-process rate limiter for FastAPI.

Uses a per-IP sliding-window counter stored in an ``OrderedDict``.
No external dependencies (no Redis, no ``slowapi``).

Usage in a router::

    from app.utils.rate_limiter import rate_limit_dependency

    @router.post("", dependencies=[Depends(rate_limit_dependency)])
    async def my_endpoint(...):
        ...

Configuration (via ``.env``):
    RATE_LIMIT_RPM  — max requests per minute per IP (default 10).
"""

from __future__ import annotations

import os
import time
import threading
from collections import OrderedDict

from fastapi import HTTPException, Request, status


# ── Configuration ─────────────────────────────────────────────────────────────

RATE_LIMIT_RPM: int = int(os.getenv("RATE_LIMIT_RPM", "10"))
_WINDOW_SECONDS: float = 60.0


# ── In-memory store ──────────────────────────────────────────────────────────

_lock = threading.Lock()
# key → list of timestamps (most recent first)
_hits: OrderedDict[str, list[float]] = OrderedDict()

# Prevent unbounded memory growth: evict IPs not seen in this many seconds.
_EVICT_AFTER: float = 300.0  # 5 minutes


def _cleanup_old_entries(now: float) -> None:
    """Remove IPs whose newest hit is older than ``_EVICT_AFTER``."""
    while _hits:
        # Peek at the oldest entry (FIFO order of OrderedDict)
        ip, timestamps = next(iter(_hits.items()))
        if timestamps and now - timestamps[0] > _EVICT_AFTER:
            _hits.pop(ip, None)
        else:
            break


def _is_rate_limited(ip: str) -> bool:
    """Return True if *ip* has exceeded the rate limit."""
    now = time.monotonic()

    with _lock:
        _cleanup_old_entries(now)

        window_start = now - _WINDOW_SECONDS
        timestamps = _hits.get(ip, [])

        # Prune timestamps outside the current window
        timestamps = [t for t in timestamps if t > window_start]

        if len(timestamps) >= RATE_LIMIT_RPM:
            _hits[ip] = timestamps
            _hits.move_to_end(ip)
            return True

        timestamps.append(now)
        _hits[ip] = timestamps
        _hits.move_to_end(ip)
        return False


# ── FastAPI dependency ────────────────────────────────────────────────────────

async def rate_limit_dependency(request: Request) -> None:
    """FastAPI dependency that enforces the per-IP rate limit.

    Raises ``429 Too Many Requests`` if the caller has exceeded
    ``RATE_LIMIT_RPM`` requests in the last 60 seconds.
    """
    client_ip = request.client.host if request.client else "unknown"

    if _is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded. Maximum {RATE_LIMIT_RPM} requests "
                f"per minute. Please try again shortly."
            ),
        )
