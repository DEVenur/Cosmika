"""Thin async wrapper around Docker Engine API via Unix socket."""
import os
import socket

import httpx

_SOCKET = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")
_COMPOSE_PROJECT = os.getenv("COMPOSE_PROJECT_NAME", "")
_own_project_cache: str | None = None


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


async def _own_project() -> str:
    """Compose project of the container this process runs in ('' outside Docker).

    COMPOSE_PROJECT_NAME takes precedence; otherwise the project label is read
    from our own container (hostname == container id inside Docker).
    """
    global _own_project_cache
    if _COMPOSE_PROJECT:
        return _COMPOSE_PROJECT
    if _own_project_cache is None:
        try:
            async with _client() as c:
                r = await c.get(f"/containers/{socket.gethostname()}/json", timeout=5)
                r.raise_for_status()
                labels = r.json().get("Config", {}).get("Labels", {}) or {}
                _own_project_cache = labels.get("com.docker.compose.project", "")
        except Exception:
            _own_project_cache = ""
    return _own_project_cache


async def find_service(service: str) -> dict | None:
    """Find a docker-compose service container by service label.

    Matches are restricted to this GUI's own compose project, so a host
    running several Dango deployments never starts/stops/restarts a sibling
    project's bot. When project detection fails (e.g. running outside
    Docker), no project filter is applied.
    """
    try:
        project = await _own_project()
        containers = await list_containers()
        for ct in containers:
            labels = ct.get("Labels", {})
            if labels.get("com.docker.compose.service") != service:
                continue
            if project and labels.get("com.docker.compose.project") != project:
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
