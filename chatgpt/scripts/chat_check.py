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


def scene_break_positions(text: str) -> list[int]:
    """Return one-based source paragraph indices following each separator."""
    count = 0
    positions = []
    for part in paragraphs(text):
        if part == "---":
            positions.append(count + 1)
        else:
            count += 1
    return positions


def scene_break_errors(text: str, expected_before: list[int] | None = None) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    parts = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    errors: list[str] = []
    if parts and parts[0] == "---":
        errors.append("scene break cannot precede the title")
    if parts and parts[-1] == "---":
        errors.append("scene break cannot end the chapter")
    if any(left == right == "---" for left, right in zip(parts, parts[1:])):
        errors.append("consecutive scene breaks")
    if expected_before is not None:
        actual = set(scene_break_positions(text))
        expected = set(expected_before)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            errors.append(f"missing reviewed scene break before paragraph(s): {missing}")
        if extra:
            errors.append(f"unreviewed scene break before paragraph(s): {extra}")
    return errors


def chapter_input_errors(source: list[str], target: list[str]) -> list[str]:
    """Reject empty inputs and a missing or mismatched chapter number."""
    errors = []
    if not source:
        errors.append("source is empty")
    if not target:
        errors.append("target is empty")
    if source and target:
        source_title = re.search(r"第\s*(\d+)\s*章", source[0])
        if source_title:
            target_title = re.match(r"^Chapter\s+(\d+)\b", target[0])
            if not target_title:
                errors.append("target title is missing or malformed")
            elif int(source_title[1]) != int(target_title[1]):
                errors.append("target chapter number does not match source")
    return errors


def main() -> None:
    common.configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--scene-break-before", type=int, nargs="*", default=None,
        help="Reviewed one-based source paragraph indices; pass no values for none.",
    )
    args = parser.parse_args()
    root = common.find_root()
    glossary = common.load_glossary(root)
    phrases = common.load_phrase_memory(root)
    source_text = args.source.read_text(encoding="utf-8")
    target_text = args.target.read_text(encoding="utf-8")
    source = paragraphs(source_text, allow_scene_breaks=True)
    target = paragraphs(target_text, allow_scene_breaks=True)
    errors = chapter_input_errors(source, target)
    warnings: list[str] = []

    required_breaks = args.scene_break_before
    source_breaks = scene_break_positions(source_text)
    if source_breaks:
        required_breaks = sorted(set(source_breaks + (required_breaks or [])))
    errors.extend(scene_break_errors(target_text, required_breaks))

    if len(source) != len(target):
        errors.append(f"paragraph count: source {len(source)}, target {len(target)}")
    for index, (src, tgt) in enumerate(zip(source, target), 1):
        residue = sorted({char for char in tgt if common.is_cjk(char)})
        if residue:
            errors.append(f"paragraph {index}: source characters {''.join(residue)}")
        banned = [char for char in lint.BANNED_STYLE_CHARS if char in tgt]
        if banned:
            errors.append(f"paragraph {index}: banned typography {''.join(banned)}")
        cjk_punct = lint.punctuation_residue(src, tgt)
        if cjk_punct:
            errors.append(f"paragraph {index}: CJK punctuation {''.join(cjk_punct)}")
        for detail in lint.fixed_display_errors(src, tgt, phrases):
            errors.append(f"paragraph {index}: {detail}")
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
