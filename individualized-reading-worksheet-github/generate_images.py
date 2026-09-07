"""Automatically generate worksheet scene images and write paths back to JSON.

Default provider: OpenAI GPT-Image-2.

Usage:
  # Preview prompts only (no API call)
  python generate_images.py sample_3c.json --dry-run

  # Generate images (requires OPENAI_API_KEY)
  python generate_images.py sample_3c.json --output-json sample_3c_with_images.json

  # Level 3D also generates a square image for every core vocabulary item.

The program caches generated files by a hash of model + prompt + size + quality.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any

from image_prompt_builder import (
    build_prediction_prompt,
    build_section_prompt,
    build_vocab_prompt,
)


def safe_name(value: str, fallback: str = "image") -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "_", value.strip())
    value = re.sub(r"\s+", "_", value)
    return value[:80] or fallback


def prompt_hash(prompt: str, model: str, size: str, quality: str) -> str:
    raw = f"{model}\n{size}\n{quality}\n{prompt}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def save_api_image(item: Any, destination: Path) -> None:
    """Save an OpenAI image response item that contains b64_json or url."""
    b64_data = getattr(item, "b64_json", None)
    url = getattr(item, "url", None)

    if b64_data:
        destination.write_bytes(base64.b64decode(b64_data))
        return
    if url:
        with urllib.request.urlopen(url) as response:
            destination.write_bytes(response.read())
        return
    raise RuntimeError("Image API response contained neither b64_json nor url.")


class OpenAIImageGenerator:
    def __init__(self, model: str = "gpt-image-2") -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Missing dependency: pip install openai") from exc
        self.client = OpenAI()
        self.model = model

    def generate(self, prompt: str, destination: Path, *, size: str, quality: str) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        if not getattr(response, "data", None):
            raise RuntimeError("Image API returned no image data.")
        save_api_image(response.data[0], destination)
        return destination


def cached_generate(
    generator: OpenAIImageGenerator,
    prompt: str,
    destination: Path,
    *,
    cache_dir: Path,
    size: str,
    quality: str,
    overwrite: bool,
) -> Path:
    if destination.exists() and not overwrite:
        return destination

    cache_dir.mkdir(parents=True, exist_ok=True)
    key = prompt_hash(prompt, generator.model, size, quality)
    cached = cache_dir / f"{key}.png"
    if cached.exists() and not overwrite:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cached, destination)
        return destination

    generator.generate(prompt, cached, size=size, quality=quality)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cached, destination)
    return destination


def plan_images(data: dict[str, Any], base_dir: Path) -> list[dict[str, Any]]:
    title = data.get("title", "worksheet")
    level = data.get("level", "")
    title_slug = safe_name(title)
    level_slug = safe_name(level, "level")
    root = base_dir / title_slug / level_slug

    jobs: list[dict[str, Any]] = []
    prediction = data.get("prediction") or {}
    if prediction:
        jobs.append({
            "kind": "prediction",
            "prompt": build_prediction_prompt(title, prediction.get("prompt", "")),
            "path": root / "prediction.png",
            "size": "1536x1024",
            "target": (prediction, "image"),
        })

    for idx, section in enumerate(data.get("sections", []), 1):
        section_title = section.get("title") or f"第{idx}段"
        keywords = section.get("keywords") or []
        if section.get("vocab", {}).get("word") and not keywords:
            keywords = [section["vocab"]["word"]]

        jobs.append({
            "kind": "section",
            "prompt": build_section_prompt(
                section_title,
                section.get("text", []),
                keywords=keywords,
                level=level,
                visual_brief=section.get("visual_brief", ""),
            ),
            "path": root / f"section_{idx:02d}.png",
            "size": "1536x1024",
            "target": (section, "image"),
        })

        vocab = section.get("vocab")
        if vocab and vocab.get("word"):
            jobs.append({
                "kind": "vocab",
                "prompt": build_vocab_prompt(
                    vocab.get("word", ""),
                    vocab.get("example", ""),
                    paragraph_context=" ".join(section.get("text", [])),
                    visual_brief=vocab.get("visual_brief", ""),
                ),
                "path": root / f"section_{idx:02d}_vocab_{safe_name(vocab.get('word','word'))}.png",
                "size": "1024x1024",
                "target": (vocab, "image"),
            })
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate worksheet context images and update JSON image paths.")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--image-dir", type=Path, default=Path("images/generated"))
    parser.add_argument("--cache-dir", type=Path, default=Path("images/cache"))
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--quality", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--dry-run", action="store_true", help="Only write prompt manifest; do not call API.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    jobs = plan_images(data, args.image_dir)

    manifest = []
    for job in jobs:
        manifest.append({
            "kind": job["kind"],
            "path": str(job["path"]),
            "size": job["size"],
            "prompt": job["prompt"],
        })

    manifest_path = args.input_json.with_name(args.input_json.stem + "_image_prompts.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.dry_run:
        print(f"Prompt manifest written: {manifest_path}")
        print(f"Planned images: {len(jobs)}")
        return 0

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY is not set. Use --dry-run to preview prompts.", file=sys.stderr)
        return 2

    generator = OpenAIImageGenerator(args.model)
    for n, job in enumerate(jobs, 1):
        path = cached_generate(
            generator,
            job["prompt"],
            job["path"],
            cache_dir=args.cache_dir,
            size=job["size"],
            quality=args.quality,
            overwrite=args.overwrite,
        )
        target, key = job["target"]
        target[key] = str(path.resolve())
        print(f"[{n}/{len(jobs)}] {job['kind']}: {path}")

    output_json = args.output_json or args.input_json.with_name(args.input_json.stem + "_with_images.json")
    output_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated worksheet JSON: {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
