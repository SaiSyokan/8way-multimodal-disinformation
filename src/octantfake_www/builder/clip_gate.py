"""CLIP-based auxiliary consistency filter."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


class ClipGate:
    """Score image-text pairs and apply the paper's rejection region."""

    def __init__(
        self,
        model_name: str = "openai/clip-vit-base-patch32",
        device: Optional[str] = None,
        match_threshold: float = 0.32,
        mismatch_threshold: float = 0.22,
    ) -> None:
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor
        except ImportError as exc:
            raise RuntimeError("Install the builder dependencies with: pip install -e '.[builder]'") from exc

        self._torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CLIPModel.from_pretrained(model_name).to(self.device).eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.match_threshold = float(match_threshold)
        self.mismatch_threshold = float(mismatch_threshold)
        self._cache: dict[tuple[str, str], float] = {}

    def score(self, image_path: str, text: str) -> float:
        from PIL import Image

        key = (str(Path(image_path).resolve()), text)
        if key in self._cache:
            return self._cache[key]
        if not text.strip():
            raise ValueError("text must not be empty")

        with Image.open(image_path) as image:
            rgb = image.convert("RGB")
            inputs = self.processor(images=rgb, text=[text], truncation=True, return_tensors="pt")
        inputs = {name: value.to(self.device) for name, value in inputs.items()}

        with self._torch.inference_mode():
            output = self.model(**inputs)
            image_vector = output.image_embeds
            text_vector = output.text_embeds
            image_vector = image_vector / image_vector.norm(dim=-1, keepdim=True)
            text_vector = text_vector / text_vector.norm(dim=-1, keepdim=True)
            similarity = float((image_vector * text_vector).sum(dim=-1).item())

        self._cache[key] = similarity
        return similarity

    def accepts(self, image_path: str, text: str, consistency: str) -> tuple[bool, float]:
        similarity = self.score(image_path, text)
        normalized = consistency.strip().upper()
        if normalized == "T":
            return similarity > self.match_threshold, similarity
        if normalized == "F":
            return similarity < self.mismatch_threshold, similarity
        raise ValueError(f"consistency must be T or F; received {consistency!r}")

