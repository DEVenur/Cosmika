"""Self-hosted "Copy for LLM" support for the Dango docs.

Replaces the third-party ``mkdocs-copy-to-llm`` plugin. During the build it:

* copies every source Markdown file into the built site so each page gains a
  same-origin ``<url>.md`` twin (WorkOS style), letting the frontend fetch the
  raw Markdown without hitting ``raw.githubusercontent.com``;
* injects a ``<meta name="llm:md-url">`` tag into every page pointing at that
  twin, so the frontend never has to guess the URL;
* generates ``llms.txt`` (a curated index built from the nav and each page's
  ``summary``/``description`` front matter) and ``llms-full.txt`` (the full
  Markdown corpus) at the site root.

Wire it up in ``mkdocs.yml`` with::

    hooks:
      - docs/hooks/llm_md.py
"""

from __future__ import annotations

import re
from pathlib import Path

from mkdocs.utils import get_relative_url

# Captured in ``on_nav`` so ``on_post_build`` can walk pages in nav order with
# their section titles intact.
_nav = None

_FRONT_MATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def on_nav(nav, config, files):
    global _nav
    _nav = nav
    return nav


def on_post_page(output: str, *, page, config) -> str:
    """Inject the Markdown-twin URL as a meta tag the frontend can read."""
    md_url = get_relative_url(page.file.src_uri, page.url)
    tag = f'<meta name="llm:md-url" content="{md_url}">'
    if "</head>" in output:
        output = output.replace("</head>", f"    {tag}\n  </head>", 1)
    return output


def on_post_build(*, config) -> None:
    docs_dir = Path(config["docs_dir"])
    site_dir = Path(config["site_dir"])

    # 1. Emit a clean same-origin .md twin for every source page.
    for md in docs_dir.rglob("*.md"):
        rel = md.relative_to(docs_dir)
        dest = site_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(_strip_front_matter(_read(md)), encoding="utf-8")

    # 2. Generate llms.txt and llms-full.txt.
    _write_llms_txt(config, site_dir)
    _write_llms_full_txt(config, site_dir)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _strip_front_matter(text: str) -> str:
    return _FRONT_MATTER_RE.sub("", text, count=1).lstrip()


def _md_abs_url(config, page) -> str:
    base = (config.get("site_url") or "").rstrip("/")
    src = page.file.src_uri
    return f"{base}/{src}" if base else f"/{src}"


def _first_paragraph(page) -> str:
    """Fallback summary: the first prose paragraph of the source Markdown.

    Skips headings, tables, code fences and admonitions so the fallback is
    always readable. (Pages should still define an explicit ``summary``.)
    """
    text = _strip_front_matter(_read(page.file.abs_src_path))
    skip_prefixes = ("#", "!!!", "???", "|", "```", "~~~", "<", "- ", "* ", "> ")
    for block in text.split("\n\n"):
        block = block.strip()
        if not block or block.startswith(skip_prefixes):
            continue
        return " ".join(block.split())
    return ""


def _summary(page) -> str:
    meta = page.meta or {}
    for key in ("summary", "description"):
        value = meta.get(key)
        if value:
            return str(value).strip()
    return _first_paragraph(page)


def _section_lines(item, config) -> list[str]:
    if getattr(item, "is_section", False):
        children: list[str] = []
        for child in item.children or []:
            children += _section_lines(child, config)
        if not children:
            return []
        return [f"## {item.title}", "", *children, ""]

    if getattr(item, "is_page", False):
        page = item
        if page.is_homepage or (page.meta or {}).get("llms_exclude"):
            return []
        title = page.title or page.file.src_uri
        url = _md_abs_url(config, page)
        summary = _summary(page)
        return [f"- [{title}]({url}): {summary}" if summary else f"- [{title}]({url})"]

    return []


def _write_llms_txt(config, site_dir: Path) -> None:
    lines = [f"# {config['site_name']}", ""]
    intro = (config.get("extra") or {}).get("llms_summary") or config.get(
        "site_description"
    )
    if intro:
        lines += [f"> {intro}", ""]

    if _nav is not None:
        for item in _nav.items:
            lines += _section_lines(item, config)

    content = "\n".join(lines).rstrip() + "\n"
    (site_dir / "llms.txt").write_text(content, encoding="utf-8")


def _iter_pages(item):
    if getattr(item, "is_page", False):
        yield item
    for child in getattr(item, "children", None) or []:
        yield from _iter_pages(child)


def _write_llms_full_txt(config, site_dir: Path) -> None:
    if _nav is None:
        return
    parts = [f"# {config['site_name']}", ""]
    intro = (config.get("extra") or {}).get("llms_summary") or config.get(
        "site_description"
    )
    if intro:
        parts += [f"> {intro}", ""]

    seen: set[str] = set()
    for item in _nav.items:
        for page in _iter_pages(item):
            if page.is_homepage and page.file.src_uri in seen:
                continue
            if (page.meta or {}).get("llms_exclude"):
                continue
            src = page.file.src_uri
            if src in seen:
                continue
            seen.add(src)
            body = _strip_front_matter(_read(page.file.abs_src_path))
            parts += [
                "---",
                "",
                f"Source: {_md_abs_url(config, page)}",
                "",
                body,
                "",
            ]

    content = "\n".join(parts).rstrip() + "\n"
    (site_dir / "llms-full.txt").write_text(content, encoding="utf-8")
