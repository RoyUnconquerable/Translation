"""Build a read-only authority sheet for a plain Chinese chapter source.

Usage: python chatgpt/scripts/prepare.py source.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import chat_check
import lint
import state

BRACKET_RE = re.compile(r"【([^】]+)】")
NUMBER_RE = re.compile(
    r"(?:[一二三四五六七八九]成[零〇一二三四五六七八九]"
    r"|[零〇一二三四五六七八九两]{2}开"
    r"|\d[\d,]*(?:年|月|日|层|位|枚|道|次|人|个|分|成|里|丈|岁|州|章)?"
    r"|(?:几|数)?[零〇一二三四五六七八九十百千万亿兆两]+(?:余|多|来)?"
    r"(?:甲子|年|月|日|层|位|枚|道|次|人|个|分|成|里|丈|尺|寸|厘|岁|州|章|世|座|条|种|轮|颗|片|根|名|件|处|部|路|口|步|眼|手|字|声|息|倍|等))"
)

PROSE_REVIEW_REMINDERS = (
    "Use natural contractions by default; expand only for emphasis, contrast, "
    "formal cadence, or clarity, and never use contractions ending in 'd.",
    "Audit English articles, prepositions, complements, and collocations instead "
    "of carrying over Chinese syntax.",
    "Link tightly related clauses inside each source paragraph when separate "
    "sentences create stop-start flow; never merge source paragraphs.",
    "Account for every source action, gesture, purpose, timing cue, degree, "
    "and relationship; paragraph totals alone cannot detect small omissions.",
    "Verify displayed inscriptions word for word, including bold corner "
    "brackets; record reviewed scene-break positions, or explicitly none.",
    "Read direct thoughts as natural mental speech with linked reasoning, "
    "while preserving every premise and the source's time reference.",
)


def paragraphs(text: str) -> list[str]:
    """Use the checker's content indices; separators are not content rows."""
    return chat_check.paragraphs(text, allow_scene_breaks=True)


def scoped_pronouns(entity: dict, chapter: int | None) -> str:
    """Apply only the owner's explicit chapter boundary, not inferred identity."""
    if chapter is not None and entity["entity_id"] in {"sword_sovereign", "vast_sky"}:
        if chapter < 1129:
            return "they/them/their"
        return "she/her" if entity["entity_id"] == "sword_sovereign" else "he/him/his"
    return entity["pronouns"]


def main() -> None:
    common.configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--observed-through", type=int,
        help="Verified in-session source frontier since the last approved update. "
             "Use only with actual intervening source evidence; never infers "
             "delivery/approval or writes repository state.",
    )
    args = parser.parse_args()
    root = common.find_root()
    hard = common.load_glossary(root)
    phrases = common.load_phrase_memory(root)
    entities = common.load_entities(root)
    source_text = args.source.read_text(encoding="utf-8")
    source_paragraphs = paragraphs(source_text)
    chapter_number = None
    if source_paragraphs:
        chapter = re.search(r"第\s*(\d+)\s*章", source_paragraphs[0])
        if chapter:
            chapter_number = int(chapter[1])
            routing = state.load_json(root / "chapters" / "state.json")
            errors = state.incoming_chapter_errors(
                int(chapter[1]), routing, observed_through=args.observed_through
            )
            if errors:
                raise SystemExit("prepare: FAIL\n  " + "\n  ".join(errors))
            if args.observed_through is not None:
                print(
                    f"verified session source frontier: {args.observed_through}; "
                    "repository state unchanged; no delivery/approval inferred"
                )
        elif args.observed_through is not None:
            parser.error("--observed-through requires a numbered source chapter")
    elif args.observed_through is not None:
        parser.error("--observed-through requires a numbered source chapter")

    hard_hits: dict[str, set[int]] = defaultdict(set)
    phrase_hits: dict[str, set[int]] = defaultdict(set)
    entity_hits: dict[str, set[int]] = defaultdict(set)
    number_hits: dict[str, set[int]] = defaultdict(set)
    bracketed: dict[str, set[int]] = defaultdict(set)

    alias_to_entity = {}
    for entity in entities:
        for alias in entity["source_aliases"].split("|"):
            alias_to_entity[alias] = entity

    for index, paragraph in enumerate(source_paragraphs, 1):
        matched_terms = lint.glossary_matches(paragraph, hard)
        for entry in matched_terms:
            hard_hits[entry["source"]].add(index)
            if entry["source"] in alias_to_entity:
                entity_hits[entry["source"]].add(index)
        for row in phrases:
            if row["source"] in paragraph:
                phrase_hits[row["source"]].add(index)
        for match in NUMBER_RE.finditer(paragraph):
            if match.group(0):
                number_hits[match.group(0)].add(index)
        for term in BRACKET_RE.findall(paragraph):
            bracketed[term].add(index)

    print(f"paragraphs: {len(source_paragraphs)}")
    print("indices: title is 1; standalone scene separators are excluded")
    print(f"explicit source scene breaks before: {chat_check.scene_break_positions(source_text)}")
    if source_paragraphs:
        print(f"title: {source_paragraphs[0]}")

    print("\nhard terminology:")
    for source in sorted(hard_hits, key=lambda value: min(hard_hits[value])):
        rows = ",".join(str(value) for value in sorted(hard_hits[source]))
        print(f"  [{rows}] {source} -> {hard[source]['target']}")
        if hard[source]["notes"]:
            print(f"    {hard[source]['notes']}")

    print("\nentities and pronouns:")
    for alias in sorted(entity_hits, key=lambda value: min(entity_hits[value])):
        entity = alias_to_entity[alias]
        actual_name = hard[alias]["target"] if alias in hard else entity["english_names"]
        rows = ",".join(str(value) for value in sorted(entity_hits[alias]))
        print(
            f"  [{rows}] {alias} -> {actual_name} "
            f"[{entity['entity_id']}; {scoped_pronouns(entity, chapter_number)}]"
        )
        if entity["notes"]:
            print(f"    {entity['notes']}")

    print("\nrelevant phrase memory:")
    phrase_by_source = {row["source"]: row for row in phrases}
    for source in sorted(phrase_hits, key=lambda value: min(phrase_hits[value])):
        row = phrase_by_source[source]
        rows = ",".join(str(value) for value in sorted(phrase_hits[source]))
        print(
            f"  [{rows}] [{row['scope']}] {source} -> {row['target']}"
            f"; {row['notes']}"
        )

    print("\nbracketed terms not in hard terminology:")
    print("  Candidate list only; also inspect unbracketed and single-use new terms.")
    unknown = [term for term in bracketed if term not in hard and f"【{term}】" not in hard]
    if unknown:
        for term in sorted(unknown, key=lambda value: min(bracketed[value])):
            rows = ",".join(str(value) for value in sorted(bracketed[term]))
            memory = phrase_by_source.get(term)
            suffix = f"; phrase memory: {memory['target']}" if memory else ""
            print(f"  [{rows}] {term}{suffix}")
    else:
        print("  none")

    print("\nnumbers and quantified expressions:")
    for value in sorted(number_hits, key=lambda item: min(number_hits[item])):
        rows = ",".join(str(index) for index in sorted(number_hits[value]))
        print(f"  [{rows}] {value}")

    print("\nmandatory English review:")
    for reminder in PROSE_REVIEW_REMINDERS:
        print(f"  - {reminder}")

    print("\nowner-reference lookup:")
    print("  Use state authority paths for formatting, idioms, title italics and system templates.")
    print("  Retrieve matching entries only; later scoped owner rules override older phrase defaults.")
    print("  Suspected idiom sources are hints; retained variants are local, not new global choices.")
    print("  For display-only paragraph splits, record SOURCE:COUNT for chat_check.py --display-splits.")

    print("\nscene-break review candidates (judgment required):")
    for index, paragraph in enumerate(source_paragraphs, 1):
        if re.match(r"^(与此同时|另一边|光海内|睁开眼)", paragraph):
            print(f"  before [{index}]: {paragraph[:80]}")
    print("  Review all other changes of place, time, and viewpoint as well.")


if __name__ == "__main__":
    main()
