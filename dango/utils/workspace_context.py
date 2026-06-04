"""
Workspace context manager.

workspace_sys_prompt.txt is generated once from the workspace files (if it doesn't exist
or workspace files have changed since last generation) and injected directly into the
main agent's system prompt. It contains a topic index and instructs the main agent to
call the workspace tool for related queries.

Generation uses a dedicated Workspace Agent that reads files via tool calls,
so it never dumps all file contents into a single context window.
"""

import json
from pathlib import Path

from agno.agent import Agent


_META_PROMPT = """\
Read all files in the workspace and generate a short topic index.
Each entry: topic name and a one-line description.
End with a line telling the assistant to use the workspace tool for details.

Example:
## Workspace Topics
- **Topic A** — what it covers
- **Topic B** — what it covers
Use the workspace tool for details on any topic above.\
"""

_context: str = ""
_fingerprint: dict[str, float] = {}  # {absolute path: mtime}
_root: str = ""
_sys_prompt_path: str = ""


def _compute_fingerprint(root: str) -> dict[str, float]:
    p = Path(root)
    if not p.exists():
        return {}
    return {
        str(f): f.stat().st_mtime
        for f in sorted(p.rglob("*"))
        if f.is_file() and f.suffix in {".md", ".txt"}
    }


def _fingerprint_path(sys_prompt_path: str) -> str:
    return str(Path(sys_prompt_path).with_suffix(".fingerprint.json"))


def _load_stored_fingerprint(sys_prompt_path: str) -> dict[str, float]:
    p = Path(_fingerprint_path(sys_prompt_path))
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_fingerprint(sys_prompt_path: str, fp: dict[str, float]) -> None:
    Path(_fingerprint_path(sys_prompt_path)).write_text(
        json.dumps(fp, ensure_ascii=False), encoding="utf-8"
    )


async def _generate_and_save(save_path: str) -> str:
    """Generate workspace_sys_prompt.txt using a Workspace Agent and save it."""
    # Lazy import to avoid circular: call_agent → build_instructions → workspace_context
    from agno.tools.workspace import Workspace
    from ..steps.call_agent import _fast_model  # noqa: PLC0415

    agent = Agent(
        model=_fast_model,
        tools=[Workspace(_root, allowed=["read", "list", "search"])],
        instructions=_META_PROMPT,
        markdown=False,
    )
    response = await agent.arun(
        input="Explore the workspace and generate the system prompt block."
    )
    generated = (response.content or "").strip()
    if not generated:
        print("⚠️  Workspace context generation returned empty — cache not written")
        return ""
    Path(save_path).write_text(generated, encoding="utf-8")
    print(f"📝 Workspace system prompt generated and saved to {save_path}")
    return generated


async def init(root: str, sys_prompt_path: str) -> None:
    """Load workspace context. Call once from setup_hook."""
    global _context, _fingerprint, _root, _sys_prompt_path
    _root = root
    _sys_prompt_path = sys_prompt_path
    _fingerprint = _compute_fingerprint(root)
    if not _fingerprint:
        return

    path = Path(sys_prompt_path)
    stored_fp = _load_stored_fingerprint(sys_prompt_path)

    if path.exists() and stored_fp == _fingerprint:
        _context = path.read_text(encoding="utf-8").strip()
        print(f"📂 Workspace system prompt loaded from cache ({sys_prompt_path})")
    else:
        if path.exists():
            print("📂 Workspace files changed — regenerating system prompt...")
        _context = await _generate_and_save(sys_prompt_path)
        if _context:
            _save_fingerprint(sys_prompt_path, _fingerprint)

    print(f"📂 Workspace context ready ({len(_fingerprint)} files)")


def get() -> str:
    """Return the current workspace context string for system prompt injection."""
    return _context
