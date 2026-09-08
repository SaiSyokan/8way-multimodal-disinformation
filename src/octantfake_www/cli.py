"""Command-line entry points for construction, inference, and evaluation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .builder import build_dataset
from .evaluation import evaluate_predictions
from .evidence.collectors import collect_image_evidence, collect_text_evidence
from .evidence.store import EvidenceStore
from .io import dump_json, dump_jsonl, load_jsonl
from .manifest import validate_manifest
from .method.llava_backend import LlavaBackend
from .method.pipeline import OctantAgent


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="octantfake")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a dataset manifest")
    validate.add_argument("manifest")
    validate.add_argument("--check-files", action="store_true")
    validate.add_argument("--media-root")

    evaluate = subparsers.add_parser("evaluate", help="evaluate normalized predictions")
    evaluate.add_argument("predictions")
    evaluate.add_argument("--output")

    build = subparsers.add_parser("build", help="construct paper-aligned manifests")
    build.add_argument("--config", required=True)

    text = subparsers.add_parser("collect-text-evidence")
    text.add_argument("--manifest", required=True)
    text.add_argument("--output", required=True)
    text.add_argument("--limit", type=int, default=3)

    image = subparsers.add_parser("collect-image-evidence")
    image.add_argument("--manifest", required=True)
    image.add_argument("--output", required=True)
    image.add_argument("--limit", type=int, default=5)
    image.add_argument("--media-root")
    image.add_argument("--no-page-context", action="store_true")

    run = subparsers.add_parser("run", help="run OctantAgent")
    run.add_argument("--manifest", required=True)
    run.add_argument("--evidence-root", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--backend", choices=["llava"], default="llava")
    run.add_argument("--model-path", required=True)
    run.add_argument("--media-root")
    run.add_argument("--model-base")
    run.add_argument("--conversation-mode")
    run.add_argument("--temperature", type=float, default=0.0)
    run.add_argument("--top-p", type=float)
    run.add_argument("--num-beams", type=int, default=1)
    run.add_argument("--max-new-tokens", type=int, default=512)
    run.add_argument("--seed", type=int, default=42)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    if args.command == "validate":
        result = validate_manifest(args.manifest, args.check_files, args.media_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["valid"]:
            raise SystemExit(1)
    elif args.command == "evaluate":
        print(
            json.dumps(
                evaluate_predictions(args.predictions, args.output),
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.command == "build":
        print(json.dumps(build_dataset(args.config), ensure_ascii=False, indent=2))
    elif args.command == "collect-text-evidence":
        count = collect_text_evidence(args.manifest, args.output, limit=args.limit)
        print(json.dumps({"collected": count, "kind": "text"}))
    elif args.command == "collect-image-evidence":
        count = collect_image_evidence(
            args.manifest,
            args.output,
            limit=args.limit,
            media_root=args.media_root,
            fetch_page_context=not args.no_page_context,
        )
        print(json.dumps({"collected": count, "kind": "image"}))
    elif args.command == "run":
        backend = LlavaBackend(
            args.model_path,
            model_base=args.model_base,
            conversation_mode=args.conversation_mode,
            temperature=args.temperature,
            top_p=args.top_p,
            num_beams=args.num_beams,
            max_new_tokens=args.max_new_tokens,
            seed=args.seed,
        )
        agent = OctantAgent(backend, EvidenceStore(args.evidence_root))
        manifest_path = Path(args.manifest).expanduser().resolve()
        media_root = (
            Path(args.media_root).expanduser().resolve()
            if args.media_root
            else manifest_path.parent
        )
        output_rows = []
        for row in load_jsonl(manifest_path):
            prediction = agent.predict(row, media_root).to_dict()
            if "label" in row:
                prediction["gold_label"] = row["label"]
            output_rows.append(prediction)
        dump_jsonl(args.output, output_rows)
        output_path = Path(args.output).expanduser().resolve()
        metadata_path = output_path.with_name(output_path.name + ".run.json")
        dump_json(
            metadata_path,
            {
                "package_version": __version__,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "manifest": str(args.manifest),
                "evidence_root": str(args.evidence_root),
                "backend": args.backend,
                "model_path": args.model_path,
                "model_base": args.model_base,
                "conversation_mode": args.conversation_mode or "auto",
                "temperature": args.temperature,
                "top_p": args.top_p,
                "num_beams": args.num_beams,
                "max_new_tokens": args.max_new_tokens,
                "seed": args.seed,
                "processed": len(output_rows),
            },
        )
        print(
            json.dumps(
                {
                    "processed": len(output_rows),
                    "output": str(args.output),
                    "run_metadata": str(metadata_path),
                }
            )
        )


if __name__ == "__main__":
    main()
