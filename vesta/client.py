import httpx
from config import VESTABOARD_BASE_URL, VESTABOARD_LOCAL_API_KEY


def _headers() -> dict:
    return {"X-Vestaboard-Local-Api-Key": VESTABOARD_LOCAL_API_KEY}


def send(chars: list[list[int]]) -> bool:
    """Send a 6x22 character code array to the board."""
    with httpx.Client() as client:
        resp = client.post(
            f"{VESTABOARD_BASE_URL}/local-api/message",
            headers=_headers(),
            json={"message": chars},
        )
        return resp.status_code in (200, 201)


def send_animated(
    chars: list[list[int]],
    strategy: str = "column",
    step_interval_ms: int = 100,
    step_size: int = 1,
) -> bool:
    """Send a message with an animation strategy."""
    with httpx.Client() as client:
        resp = client.post(
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


def read() -> list[list[int]] | None:
    """Read the current board state. Returns 6x22 array or None on error."""
    with httpx.Client() as client:
        resp = client.get(
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
