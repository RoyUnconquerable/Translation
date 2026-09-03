"""Check a plain Chinese source and English chat draft paragraph by paragraph.

Usage:
  python chatgpt/scripts/chat_check.py source.txt target.txt

Use temporary untracked files for chat-only work. This command never writes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import lint


def paragraphs(text: str, *, allow_scene_breaks: bool = False) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    parts = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    if allow_scene_breaks:
        return [part for part in parts if part != "---"]
    return parts


def scene_break_errors(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    parts = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    errors: list[str] = []
    if parts and parts[0] == "---":
        errors.append("scene break cannot precede the title")
    if parts and parts[-1] == "---":
        errors.append("scene break cannot end the chapter")
    if any(left == right == "---" for left, right in zip(parts, parts[1:])):
        errors.append("consecutive scene breaks")
    return errors


def main() -> None:
    common.configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    root = common.find_root()
    glossary = common.load_glossary(root)
    source_text = args.source.read_text(encoding="utf-8")
    target_text = args.target.read_text(encoding="utf-8")
    source = paragraphs(source_text)
    target = paragraphs(target_text, allow_scene_breaks=True)
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(scene_break_errors(target_text))

    if len(source) != len(target):
        errors.append(f"paragraph count: source {len(source)}, target {len(target)}")
    if source and target:
        if re.search(r"第\s*\d+\s*章", source[0]) and not re.search(
            r"\bChapter\s+\d+\b", target[0]
        ):
            errors.append("target title is missing or malformed")

    for index, (src, tgt) in enumerate(zip(source, target), 1):
        residue = sorted({char for char in tgt if common.is_cjk(char)})
        if residue:
            errors.append(f"paragraph {index}: source characters {''.join(residue)}")
        banned = [char for char in lint.BANNED_STYLE_CHARS if char in tgt]
        if banned:
            errors.append(f"paragraph {index}: banned typography {''.join(banned)}")
        cjk_punct = sorted(
            char
            for char in set(tgt)
            if char in common.CJK_PUNCT and char not in lint.BANNED_STYLE_CHARS
        )
        if cjk_punct:
            errors.append(f"paragraph {index}: CJK punctuation {''.join(cjk_punct)}")
        if lint.D_CONTRACTION_RE.search(tgt):
            errors.append(f"paragraph {index}: contraction ending in 'd")
        for entry in lint.glossary_matches(src, glossary):
            if not lint.target_has_variant(tgt, entry["variants"]):
                errors.append(
                    f"paragraph {index}: {entry['source']!r} requires {entry['target']}"
                )
        target_numbers = set(lint.digit_seqs(tgt))
        missing = [value for value in lint.digit_seqs(src) if value not in target_numbers]
        if missing:
            warnings.append(f"paragraph {index}: check digits {', '.join(missing)}")

    if warnings:
        print(f"chat check: {len(warnings)} warning(s)")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print(f"chat check: FAIL ({len(errors)} error(s))")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)
    print(f"chat check: PASS ({len(source)} paragraphs)")


if __name__ == "__main__":
    main()
