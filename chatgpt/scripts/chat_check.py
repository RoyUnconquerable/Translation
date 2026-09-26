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


ARCHAISM_RE = re.compile(r"\b(woe is me|alas|verily|forsooth|prithee|lo and behold|thee|thou|thy)\b", re.I)
BANNED_PHRASE_RE = re.compile(r"\b(only then did|at this moment|just at this moment|revealed an expression of)\b", re.I)
REPEAT_CONNECTORS = ("with that", "at that", "just then", "meanwhile", "after all", "however", "in that case", "at this point")
PRESENT_RE = re.compile(r"\b(is|are|am|has|does|isn't|aren't|doesn't)\b", re.I)
YOU_RE = re.compile(r"\b(you|your|yours)\b", re.I)
SENT_RE = re.compile(r"[^.!?]+[.!?]+")


def narration_only(paragraph: str) -> str:
    """Strip quoted speech and italic thought, leaving narration."""
    text = re.sub(r'"[^"]*"', " ", paragraph)
    return re.sub(r"\*[^*]+\*", " ", text)


def prose_findings(target: list[str]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for chapter-level prose tells."""
    errors: list[str] = []
    warnings: list[str] = []
    body = target[1:]
    joined = "\n".join(body).lower()
    for index, para in enumerate(body, 2):
        if para.strip().rstrip(".").strip().lower() in {"just then", "but just then", "at that moment"}:
            errors.append(f"paragraph {index}: standalone lead-in fragment")
        if ARCHAISM_RE.search(para):
            errors.append(f"paragraph {index}: archaism {ARCHAISM_RE.search(para).group(0)!r}")
        if BANNED_PHRASE_RE.search(para):
            errors.append(f"paragraph {index}: banned tell {BANNED_PHRASE_RE.search(para).group(0)!r}")
        words = len(para.split())
        if words > 120:
            warnings.append(f"paragraph {index}: {words} words (ceiling 120)")
        narration = narration_only(para)
        if YOU_RE.search(narration):
            warnings.append(f"paragraph {index}: 'you' in narration")
        if PRESENT_RE.search(narration):
            warnings.append(f"paragraph {index}: present-tense verb in narration ({PRESENT_RE.search(narration).group(0)})")
        run = 0
        for sentence in SENT_RE.findall(narration):
            run = run + 1 if len(sentence.split()) < 8 else 0
            if run >= 4:
                warnings.append(f"paragraph {index}: four or more short narration sentences in a row")
                break
    for phrase in REPEAT_CONNECTORS:
        count = len(re.findall(r"\b" + phrase + r"\b", joined))
        if count > 2:
            warnings.append(f"connector {phrase!r} used {count} times (limit 2)")
    return errors, warnings


def apply_lead_in_merges(
    source: list[str], declarations: list[int],
) -> tuple[list[str], dict[int, int], list[str]]:
    """Join each declared one-line lead-in with the source paragraph after it.

    The owner folds a bare lead-in fragment (然而就在这时。, 与此同时。) into the
    next paragraph. Each declaration is the one-based source index of the
    lead-in. Returns the merged source, a map from original to merged indices,
    and errors. A merged tail keeps no index of its own.
    """
    errors: list[str] = []
    merges = sorted(set(declarations))
    if len(merges) != len(declarations):
        errors.append("duplicate lead-in merge")
    for index in merges:
        if not 2 <= index < len(source):
            errors.append(f"invalid lead-in merge {index}; no title/final paragraph merge")
        elif index - 1 in merges:
            errors.append(f"lead-in merge {index} would chain onto merge {index - 1}")
    if errors:
        return source, {i: i for i in range(1, len(source) + 1)}, errors
    merged: list[str] = []
    mapping: dict[int, int] = {}
    skip = set(m + 1 for m in merges)
    for index, text in enumerate(source, 1):
        if index in skip:
            merged[-1] = merged[-1] + "\n" + text
            continue
        merged.append(text)
        mapping[index] = len(merged)
    return merged, mapping, errors


def align_display_splits(
    source: list[str], target: list[str], declarations: list[str],
) -> tuple[list[list[str]], dict[int, int], list[str]]:
    """Map only declared display-layout splits, retaining original source indices.

    Each declaration is SOURCE:COUNT. This is a layout attestation, not proof
    that a source span is a panel or that its translation preserves meaning.
    """
    counts: dict[int, int] = {}
    errors: list[str] = []
    for value in declarations:
        match = re.fullmatch(r"([0-9]+):([0-9]+)", value)
        if not match:
            errors.append(f"invalid display split {value!r}; use SOURCE:COUNT")
            continue
        index, count = map(int, match.groups())
        if not 2 <= index <= len(source) or count < 2:
            errors.append(f"invalid display split {value!r}; no title/out-of-range split or count below 2")
        elif index in counts:
            errors.append(f"duplicate display split for source paragraph {index}")
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
        groups.append(group)
        offset += count
        if index in counts:
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
        "--merge-into-next", type=int, nargs="*", default=[], metavar="SOURCE",
        help="Owner-style merges: source index of a one-line lead-in joined to the next paragraph.",
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
    original_count = len(source)
    source, merge_map, merge_errors = apply_lead_in_merges(source, args.merge_into_next)
    errors.extend(merge_errors)
    warnings: list[str] = []
    groups, target_starts, alignment_errors = align_display_splits(
        source, target, args.display_splits
    )
    errors.extend(alignment_errors)

    required_breaks = args.scene_break_before
    source_breaks = scene_break_positions(source_text)
    if source_breaks:
        required_breaks = sorted(set(source_breaks + (required_breaks or [])))
    if required_breaks is not None and args.merge_into_next:
        inside = [i for i in required_breaks if i not in merge_map and 1 <= i <= original_count]
        if inside:
            errors.append(f"scene break inside a lead-in merge before source paragraph(s): {inside}")
        required_breaks = [merge_map[i] for i in required_breaks if i in merge_map]
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
    for index, (src, group) in enumerate(zip(source, groups), 1):
        tgt = "\n\n".join(group)
        for detail in lint.fixed_display_errors(src, tgt, phrases):
            errors.append(f"paragraph {index}: {detail}")
        for detail in lint.expansion_errors(src, tgt, glossary):
            errors.append(f"paragraph {index}: {detail}")
        for entry in lint.glossary_matches(src, glossary):
            if not lint.target_has_variant(tgt, entry["variants"]):
                errors.append(
                    f"paragraph {index}: {entry['source']!r} requires {entry['target']}"
                )
        target_numbers = set(lint.digit_seqs(tgt))
        missing = [value for value in lint.digit_seqs(src) if value not in target_numbers]
        if missing:
            warnings.append(f"paragraph {index}: check digits {', '.join(missing)}")

    prose_errors, prose_warnings = prose_findings(target)
    errors.extend(prose_errors)
    warnings.extend(prose_warnings)

    if warnings:
        print(f"chat check: {len(warnings)} warning(s)")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print(f"chat check: FAIL ({len(errors)} error(s))")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)
    if args.merge_into_next:
        print(f"chat check: PASS ({original_count} source paragraphs, {len(target)} target paragraphs; lead-in merges)")
    elif args.display_splits:
        print(f"chat check: PASS ({len(source)} source paragraphs, {len(target)} target paragraphs; mapped displays)")
    else:
        print(f"chat check: PASS ({len(source)} paragraphs)")


if __name__ == "__main__":
    main()
