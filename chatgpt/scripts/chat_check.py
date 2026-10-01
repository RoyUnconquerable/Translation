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
import prose_check


PARAGRAPH_INDENT_RE = re.compile(r"[ \t]*\n(?=(?:[ \t]{2,}|　)\S)")


def paragraphs(text: str, *, allow_scene_breaks: bool = False) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    # A pasted line that opens with the paragraph indent is its own paragraph
    # even when the blank line before it was lost (owner Ch.1428 revision).
    normalized = PARAGRAPH_INDENT_RE.sub("\n\n", normalized)
    parts = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    if allow_scene_breaks:
        return [part for part in parts if part != "---"]
    return parts


END_MARKERS = {"(本章完)", "（本章完）", "本章完", "(End of Chapter)"}


def strip_end_marker(parts: list[str]) -> list[str]:
    """The source end line is framing, not content; the owner manuscript omits it."""
    if parts and parts[-1].strip() in END_MARKERS:
        return parts[:-1]
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


def align_display_splits(
    source: list[str], target: list[str], declarations: list[str],
    pacing_splits: list[str] | None = None, pacing_joins: list[int] | None = None,
) -> tuple[list[list[str]], dict[int, int], list[str]]:
    """Map only declared display-layout splits, retaining original source indices.

    Each declaration is SOURCE:COUNT. This is a layout attestation, not proof
    that a source span is a panel or that its translation preserves meaning.
    """
    counts: dict[int, int] = {}
    errors: list[str] = []
    pacing: set[int] = set()
    for value in pacing_splits or []:
        match = re.fullmatch(r"([0-9]+):([0-9]+)", value)
        if not match:
            errors.append(f"invalid pacing split {value!r}; use SOURCE:COUNT")
            continue
        index, count = map(int, match.groups())
        if not 2 <= index <= len(source) or count < 2 or index in counts:
            errors.append(f"invalid pacing split {value!r}")
        else:
            counts[index] = count
            pacing.add(index)
    for index in pacing_joins or []:
        if not 3 <= index <= len(source) or index in counts or index - 1 in counts and counts[index - 1] == 0:
            errors.append(f"invalid pacing join {index}; it must join a body paragraph to the previous one")
        else:
            counts[index] = 0
            pacing.add(index)
    for value in declarations:
        match = re.fullmatch(r"([0-9]+):([0-9]+)", value)
        if not match:
            errors.append(f"invalid display split {value!r}; use SOURCE:COUNT")
            continue
        index, count = map(int, match.groups())
        if not 2 <= index <= len(source) or count < 2:
            errors.append(f"invalid display split {value!r}; no title/out-of-range split or count below 2")
        elif index in counts:
            errors.append(f"duplicate display or pacing declaration for source paragraph {index}")
        else:
            counts[index] = count

    expected = len(source) + sum(count - 1 for count in counts.values())
    if len(target) != expected:
        errors.append(
            f"paragraph count: source {len(source)}, target {len(target)}, "
            f"expected target {expected} after declared display splits"
        )
    groups: list[list[str]] = []
    starts: dict[int, int] = {}
    offset = 0
    for index in range(1, len(source) + 1):
        starts[index] = offset + 1
        count = counts.get(index, 1)
        group = target[offset:offset + count]
        if count == 0 and groups:
            group = groups[-1]
        groups.append(group)
        offset += count
        if index in counts and index not in pacing:
            displays = [bool(lint.DISPLAY_RE.fullmatch(part)) for part in group]
            if not any(displays):
                errors.append(f"source paragraph {index}: display split contains no standalone panel")
            if any(not left and not right for left, right in zip(displays, displays[1:])):
                errors.append(f"source paragraph {index}: display split divides ordinary prose")
    return groups, starts, errors


def main() -> None:
    common.configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--scene-break-before", type=int, nargs="*", default=None,
        help="Reviewed one-based source paragraph indices; pass no values for none.",
    )
    parser.add_argument(
        "--display-splits", nargs="*", default=[], metavar="SOURCE:COUNT",
        help="Reviewed display-only splits: source index and total target paragraphs.",
    )
    parser.add_argument(
        "--pacing-splits", nargs="*", default=[], metavar="SOURCE:COUNT",
        help="Reviewed pacing splits that isolate a punch line (translation-spec).",
    )
    parser.add_argument(
        "--pacing-joins", type=int, nargs="*", default=[], metavar="SOURCE",
        help="Reviewed pacing joins: a source paragraph that only continues the previous sentence.",
    )
    args = parser.parse_args()
    root = common.find_root()
    glossary = common.load_glossary(root)
    phrases = common.load_phrase_memory(root)
    source_text = args.source.read_text(encoding="utf-8")
    target_text = args.target.read_text(encoding="utf-8")
    source = strip_end_marker(paragraphs(source_text, allow_scene_breaks=True))
    target = strip_end_marker(paragraphs(target_text, allow_scene_breaks=True))
    errors = chapter_input_errors(source, target)
    warnings: list[str] = []
    groups, target_starts, alignment_errors = align_display_splits(
        source, target, args.display_splits, args.pacing_splits, args.pacing_joins
    )
    errors.extend(alignment_errors)

    required_breaks = args.scene_break_before
    source_breaks = scene_break_positions(source_text)
    if source_breaks:
        required_breaks = sorted(set(source_breaks + (required_breaks or [])))
    target_breaks = None
    if required_breaks is not None:
        unknown = sorted(set(required_breaks) - set(target_starts))
        if unknown:
            errors.append(f"reviewed scene breaks name unknown source paragraphs: {unknown}")
        target_breaks = [target_starts[i] for i in required_breaks if i in target_starts]
    errors.extend(scene_break_errors(target_text, target_breaks))
    for position in scene_break_positions(target_text):
        if position not in target_starts.values():
            errors.append(f"scene break inside a display split before target paragraph {position}")

    # Check every target paragraph, including extras when alignment is invalid.
    for index, tgt in enumerate(target, 1):
        residue = sorted({char for char in tgt if common.is_cjk(char)})
        if residue:
            errors.append(f"paragraph {index}: source characters {''.join(residue)}")
        banned = [char for char in lint.BANNED_STYLE_CHARS if char in tgt]
        if banned:
            errors.append(f"paragraph {index}: banned typography {''.join(banned)}")
        cjk_punct = lint.punctuation_residue("", tgt, allow_displays=True)
        if cjk_punct:
            errors.append(f"paragraph {index}: CJK punctuation {''.join(cjk_punct)}")
        for detail in lint.display_format_errors(tgt):
            errors.append(f"target paragraph {index}: {detail}")
        if lint.D_CONTRACTION_RE.search(tgt):
            errors.append(f"paragraph {index}: contraction ending in 'd")
    errors.extend(prose_check.paragraph_errors(target))
    glossary_targets = sorted({variant for entry in glossary.values() for variant in entry["variants"]})
    warnings.extend(prose_check.paragraph_warnings(target, prose_check.protected_words(glossary_targets)))
    warnings.extend(prose_check.chapter_warnings(target, glossary_targets))
    for index, (src, group) in enumerate(zip(source, groups), 1):
        tgt = "\n\n".join(group)
        for detail in lint.fixed_display_errors(src, tgt, phrases):
            errors.append(f"paragraph {index}: {detail}")
        for detail in lint.expansion_errors(src, tgt, glossary):
            errors.append(f"paragraph {index}: {detail}")
        for entry in lint.glossary_matches(src, glossary):
            found = lint.target_has_variant(tgt, entry["variants"])
            if not found and index == 1:
                # Titles are in title case; match terms case-insensitively there.
                found = lint.target_has_variant(tgt.lower(), [v.lower() for v in entry["variants"]])
            if not found:
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
    if args.display_splits:
        print(f"chat check: PASS ({len(source)} source paragraphs, {len(target)} target paragraphs; mapped displays)")
    else:
        print(f"chat check: PASS ({len(source)} paragraphs)")


if __name__ == "__main__":
    main()
