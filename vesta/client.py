import logging

import httpx

from config import VESTABOARD_BASE_URL, VESTABOARD_LOCAL_API_KEY, VESTABOARD_LOCAL_IP, VESTABOARD_PORT
import quiet_time

logger = logging.getLogger(__name__)


def _headers() -> dict:
    return {"X-Vestaboard-Local-Api-Key": VESTABOARD_LOCAL_API_KEY}


def status() -> dict:
    """Check board connectivity. Returns a status dict."""
    info = {
        "ip": VESTABOARD_LOCAL_IP,
        "port": VESTABOARD_PORT,
        "base_url": VESTABOARD_BASE_URL,
        "online": False,
        "error": None,
    }
    try:
        with httpx.Client(timeout=5) as c:
            resp = c.get(
                f"{VESTABOARD_BASE_URL}/local-api/message",
                headers=_headers(),
            )
            info["online"] = resp.status_code == 200
            if resp.status_code != 200:
                info["error"] = f"HTTP {resp.status_code}"
    except httpx.ConnectError as e:
        info["error"] = f"Connection failed: {e}"
        logger.warning("Board unreachable at %s: %s", VESTABOARD_BASE_URL, e)
    except httpx.TimeoutException:
        info["error"] = "Connection timed out"
        logger.warning("Board timed out at %s", VESTABOARD_BASE_URL)
    except httpx.HTTPError as e:
        info["error"] = str(e)
        logger.warning("Board HTTP error: %s", e)
    return info


def send(chars: list[list[int]]) -> bool:
    """Send a 6x22 character code array to the board."""
    if quiet_time.is_quiet():
        logger.info("Quiet time active — skipping board send.")
        return False
    try:
        with httpx.Client(timeout=10) as c:
            resp = c.post(
                f"{VESTABOARD_BASE_URL}/local-api/message",
                headers=_headers(),
                json={"message": chars},
            )
            return resp.status_code in (200, 201)
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("Failed to send to board: %s", e)
        return False


def send_animated(
    chars: list[list[int]],
    strategy: str = "column",
    step_interval_ms: int = 100,
    step_size: int = 1,
) -> bool:
    """Send a message with an animation strategy."""
    if quiet_time.is_quiet():
        logger.info("Quiet time active — skipping animated board send.")
        return False
    try:
        with httpx.Client(timeout=10) as c:
            resp = c.post(
                f"{VESTABOARD_BASE_URL}/local-api/message",
                headers=_headers(),
                json={
                    "message": chars,
                    "strategy": strategy,
                    "stepIntervalMs": step_interval_ms,
                    "stepSize": step_size,
                },
            )
            return resp.status_code in (200, 201)
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("Failed to send animated to board: %s", e)
        return False


def read() -> list[list[int]] | None:
    """Read the current board state. Returns 6x22 array or None on error."""
    try:
        with httpx.Client(timeout=10) as c:
            resp = c.get(
                f"{VESTABOARD_BASE_URL}/local-api/message",
                headers=_headers(),
            )
            if resp.status_code == 200:
                data = resp.json()
                # Response may be nested under a key
                if isinstance(data, dict):
                    return data.get("message") or data.get("currentMessage")
                return data
            return None
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("Failed to read board: %s", e)
        return None
