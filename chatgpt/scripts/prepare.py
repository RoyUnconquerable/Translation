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
import lint

BRACKET_RE = re.compile(r"【([^】]+)】")
NUMBER_RE = re.compile(
    r"(?:\d[\d,]*(?:年|月|日|层|位|枚|道|次|人|个|分|成|里|丈|岁|州|章)?"
    r"|[零〇一二三四五六七八九十百千万亿兆两]+(?:余|多|来)?"
    r"(?:甲子|年|月|日|层|位|枚|道|次|人|个|分|成|里|丈|岁|州|章|世|座|条|种|轮|颗|片|根|名|件|处|部|路|口|步|眼|手|字|声|息|倍))"
)


def paragraphs(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]


def main() -> None:
    common.configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    root = common.find_root()
    hard = common.load_glossary(root)
    phrases = common.load_phrase_memory(root)
    entities = common.load_entities(root)
    source_paragraphs = paragraphs(args.source.read_text(encoding="utf-8"))

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
    if source_paragraphs:
        print(f"title: {source_paragraphs[0]}")

    print("\nhard terminology:")
    for source in sorted(hard_hits, key=lambda value: min(hard_hits[value])):
        rows = ",".join(str(value) for value in sorted(hard_hits[source]))
        print(f"  [{rows}] {source} -> {hard[source]['target']}")

    print("\nentities and pronouns:")
    for alias in sorted(entity_hits, key=lambda value: min(entity_hits[value])):
        entity = alias_to_entity[alias]
        actual_name = hard[alias]["target"] if alias in hard else entity["english_names"]
        rows = ",".join(str(value) for value in sorted(entity_hits[alias]))
        print(
            f"  [{rows}] {alias} -> {actual_name} "
            f"[{entity['entity_id']}; {entity['pronouns']}]"
        )

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
    unknown = [term for term in bracketed if term not in hard]
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


if __name__ == "__main__":
    main()
