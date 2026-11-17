"""Convert DOF note HTML into clean, LLM friendly Markdown.

DOF notes are exported from a desktop publishing tool: every run of text is its
own ``<span>`` with inline styles, emphasis lives in ``style="font-weight:bold"``
rather than ``<b>``, and the body is wrapped in a full HTML document with a
``<style>`` block. This module keeps the meaning (headings, bold, italics,
tables, lists) and drops the noise.
"""

from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from markdownify import MarkdownConverter

from .models import DOF_SITE

_BOLD = re.compile(r"font-weight\s*:\s*(bold|[6-9]00)", re.I)
_ITALIC = re.compile(r"font-style\s*:\s*italic", re.I)
_BLANK_LINES = re.compile(r"\n{3,}")
_TRAILING_SPACE = re.compile(r"[ \t]+\n")
_NBSP = re.compile(r"[   ]")


class _DofConverter(MarkdownConverter):
    """markdownify converter that understands inline style emphasis."""

    def convert_span(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        style = el.get("style") or ""
        if not text.strip() or "pre" in parent_tags:
            return text
        if _BOLD.search(style) and _ITALIC.search(style):
            return self._wrap(text, "***")
        if _BOLD.search(style):
            return self._wrap(text, "**")
        if _ITALIC.search(style):
            return self._wrap(text, "*")
        return text

    @staticmethod
    def _wrap(text: str, marker: str) -> str:
        leading = text[: len(text) - len(text.lstrip())]
        trailing = text[len(text.rstrip()) :]
        return f"{leading}{marker}{text.strip()}{marker}{trailing}"


def html_to_markdown(html: str, *, base_url: str = DOF_SITE) -> str:
    """Return Markdown for a DOF note body."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["head", "style", "script", "title", "meta", "link"]):
        tag.decompose()

    # Demote headings: the tool output owns the H1 (the note title).
    for level in range(5, 0, -1):
        for heading in soup.find_all(f"h{level}"):
            heading.name = f"h{level + 1}"

    for tag in soup.find_all(["a", "img"]):
        attr = "href" if tag.name == "a" else "src"
        if tag.get(attr):
            tag[attr] = urljoin(base_url + "/", tag[attr])

    body = soup.body or soup
    markdown = _DofConverter(
        heading_style="ATX",
        bullets="-",
        strip=["font", "u"],
        table_infer_header=True,
        escape_underscores=False,
        escape_asterisks=False,
    ).convert_soup(body)
    return tidy(markdown)


def tidy(markdown: str) -> str:
    text = _NBSP.sub(" ", markdown)
    text = _TRAILING_SPACE.sub("\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip() + "\n"


def slice_text(text: str, start: int, max_chars: int) -> tuple[str, int | None]:
    """Return ``text[start:start+max_chars]`` cut at a paragraph boundary.

    The second element is the offset where the next slice should start, or
    ``None`` when the end of the text was reached.
    """
    if start >= len(text):
        return "", None
    end = start + max_chars
    if end >= len(text):
        return text[start:], None
    cut = text.rfind("\n\n", start + max_chars // 2, end)
    if cut == -1:
        cut = text.rfind("\n", start + max_chars // 2, end)
    if cut == -1:
        cut = end
    return text[start:cut].rstrip() + "\n", cut
