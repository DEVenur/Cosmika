"""Thin async wrapper around Docker Engine API via Unix socket."""
import os

import httpx

_SOCKET = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")
_COMPOSE_PROJECT = os.getenv("COMPOSE_PROJECT_NAME", "")


def available() -> bool:
    return os.path.exists(_SOCKET)


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.AsyncHTTPTransport(uds=_SOCKET),
        base_url="http://docker",
    )


async def list_containers(all_: bool = True) -> list[dict]:
    params = "?all=1" if all_ else ""
    async with _client() as c:
        r = await c.get(f"/containers/json{params}", timeout=5)
        r.raise_for_status()
        return r.json()


async def find_service(service: str) -> dict | None:
    """Find a docker-compose service container by service label."""
    try:
        containers = await list_containers()
        for ct in containers:
            labels = ct.get("Labels", {})
            if labels.get("com.docker.compose.service") != service:
                continue
            if _COMPOSE_PROJECT and labels.get("com.docker.compose.project") != _COMPOSE_PROJECT:
                continue
            return ct
    except Exception:
        pass
    return None


async def action(container_id: str, verb: str) -> bool:
    """verb: start | stop | restart"""
    try:
        async with _client() as c:
            r = await c.post(f"/containers/{container_id}/{verb}", timeout=30)
            return r.status_code in (200, 204, 304)
    except Exception:
        return False
