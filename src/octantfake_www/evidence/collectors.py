"""Optional collectors for the search services used by OctantAgent."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..io import dump_json, load_jsonl, validate_identifier


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.skip_depth = 0
        self.title: list[str] = []
        self.text: list[str] = []
        self.description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript"}:
            self.skip_depth += 1
        if normalized == "title":
            self.in_title = True
        if normalized == "meta":
            values = {key.lower(): value or "" for key, value in attrs}
            name = values.get("name", "").lower()
            prop = values.get("property", "").lower()
            if name == "description" or prop == "og:description":
                self.description = values.get("content", self.description)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
        if normalized == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if not value or self.skip_depth:
            return
        if self.in_title:
            self.title.append(value)
        self.text.append(value)


def _page_context(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {}
    try:
        import requests

        response = requests.get(
            url,
            timeout=(5, 10),
            headers={"User-Agent": "OctantFake-research-evidence-collector/1.0"},
        )
        response.raise_for_status()
        if "html" not in response.headers.get("content-type", "").lower():
            return {}
        parser = _PageParser()
        parser.feed(response.content[:1_000_000].decode(response.encoding or "utf-8", errors="replace"))
        return {
            "retrieved_title": " ".join(parser.title)[:500],
            "description": " ".join(parser.description.split())[:1000],
            "surrounding_text": " ".join(parser.text)[:1500],
        }
    except Exception:
        return {}


def collect_text_evidence(
    manifest: str | Path,
    output_root: str | Path,
    api_key: str | None = None,
    search_engine_id: str | None = None,
    limit: int = 3,
) -> int:
    if not 1 <= limit <= 10:
        raise ValueError("text evidence limit must be between 1 and 10")
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError("Install evidence dependencies with: pip install -e '.[evidence]'") from exc
    key = api_key or os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    engine = search_engine_id or os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    if not key or not engine:
        raise RuntimeError(
            "Set GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID"
        )
    destination = Path(output_root).expanduser().resolve() / "text"
    count = 0
    for row in load_jsonl(manifest):
        sample_id = validate_identifier(row["sample_id"], "sample_id")
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": key, "cx": engine, "q": str(row["text"]), "num": min(limit, 10)},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        items = []
        for item in payload.get("items", [])[:limit]:
            metatags = item.get("pagemap", {}).get("metatags", [])
            meta = metatags[0] if metatags and isinstance(metatags[0], dict) else {}
            items.append(
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "og_title": meta.get("og:title", ""),
                    "og_description": meta.get("og:description", ""),
                }
            )
        result = {
            "sample_id": sample_id,
            "provider": "google_custom_search",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "query": str(row["text"]),
            "limit": limit,
            "items": items,
        }
        dump_json(destination / f"{sample_id}.json", result)
        count += 1
    return count


def collect_image_evidence(
    manifest: str | Path,
    output_root: str | Path,
    limit: int = 5,
    media_root: str | Path | None = None,
    fetch_page_context: bool = True,
) -> int:
    if limit < 1:
        raise ValueError("image evidence limit must be positive")
    try:
        from google.cloud import vision
    except ImportError as exc:
        raise RuntimeError("Install evidence dependencies with: pip install -e '.[evidence]'") from exc
    client = vision.ImageAnnotatorClient()
    destination = Path(output_root).expanduser().resolve() / "image"
    manifest_root = (
        Path(media_root).expanduser().resolve()
        if media_root is not None
        else Path(manifest).expanduser().resolve().parent
    )
    count = 0
    for row in load_jsonl(manifest):
        sample_id = validate_identifier(row["sample_id"], "sample_id")
        image_path = Path(str(row["image_path"])).expanduser()
        if not image_path.is_absolute():
            image_path = manifest_root / image_path
        content = image_path.read_bytes()
        response = client.web_detection(image=vision.Image(content=content))
        if response.error.message:
            raise RuntimeError(f"{sample_id}: {response.error.message}")
        web = response.web_detection
        pages = []
        for page in web.pages_with_matching_images[:limit]:
            page_value: dict[str, Any] = {
                "url": page.url,
                "page_title": page.page_title,
                "full_matching_images": [image.url for image in page.full_matching_images],
                "partial_matching_images": [image.url for image in page.partial_matching_images],
            }
            if fetch_page_context:
                page_value.update(_page_context(page.url))
            pages.append(page_value)
        result: dict[str, Any] = {
            "sample_id": sample_id,
            "provider": "google_vision_web_detection",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "limit": limit,
            "best_guess_labels": [row.label for row in web.best_guess_labels[:limit]],
            "web_entities": [
                {"description": row.description, "score": row.score}
                for row in web.web_entities[:limit]
            ],
            "pages_with_matching_images": pages,
            "visually_similar_images": [row.url for row in web.visually_similar_images[:limit]],
        }
        dump_json(destination / f"{sample_id}.json", result)
        count += 1
    return count
