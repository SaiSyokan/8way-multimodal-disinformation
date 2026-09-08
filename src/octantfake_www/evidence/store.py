"""Read and render pre-collected text and reverse-image evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..io import load_json, validate_identifier


class EvidenceStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def text(self, sample_id: str) -> dict[str, Any]:
        return self._read("text", sample_id)

    def image(self, sample_id: str) -> dict[str, Any]:
        return self._read("image", sample_id)

    def _read(self, kind: str, sample_id: str) -> dict[str, Any]:
        sample_id = validate_identifier(sample_id, "sample_id")
        path = self.root / kind / f"{sample_id}.json"
        if not path.is_file():
            return {"status": "missing", "items": []}
        value = load_json(path)
        if not isinstance(value, dict):
            raise ValueError(f"evidence file must contain an object: {path}")
        return value

    @staticmethod
    def render_text(value: dict[str, Any], limit: int = 3) -> str:
        items = value.get("items", [])
        lines: list[str] = []
        for index, item in enumerate(items[:limit], 1):
            if not isinstance(item, dict):
                continue
            lines.append(
                f"[{index}] {item.get('title', '')}\n"
                f"URL: {item.get('link', '')}\n"
                f"Snippet: {item.get('snippet', '')}\n"
                f"Page metadata: {item.get('og_title', '')} {item.get('og_description', '')}".rstrip()
            )
        return "\n\n".join(lines) or "No text-search evidence available."

    @staticmethod
    def render_image(value: dict[str, Any], limit: int = 5) -> str:
        entities = ", ".join(
            str(row.get("description", ""))
            for row in value.get("web_entities", [])[:limit]
            if isinstance(row, dict)
        )
        pages = "\n".join(
            f"- {row.get('page_title') or row.get('retrieved_title', '')}: {row.get('url', '')}\n"
            f"  Context: {row.get('description') or row.get('surrounding_text', '')}"
            for row in value.get("pages_with_matching_images", [])[:limit]
            if isinstance(row, dict)
        )
        guesses = ", ".join(str(x) for x in value.get("best_guess_labels", [])[:limit])
        return (
            f"Best-guess labels: {guesses or 'none'}\n"
            f"Web entities: {entities or 'none'}\n"
            f"Pages with matching images:\n{pages or '- none'}"
        )
