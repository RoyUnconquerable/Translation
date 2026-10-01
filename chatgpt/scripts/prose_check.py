"""English mechanics checks for a delivered chapter (owner manuscript V2 review).

Errors are definite defects: split sentences, doubled words, then/than and
similar confusions. Warnings are candidates that need a reviewer's judgment:
calques, bookish diction, repetition, trailing participles, missing
contractions in speech, and inconsistent comma or capitalization style.
Nothing here proves good English; it finds the owner's recurring complaints.
"""

from __future__ import annotations

import re

DISPLAY_LINE_RE = re.compile(r"^\*\*【.*】\*\*$")
SENTENCE_RE = re.compile(r"[^.!?]+(?:[.!?]+|$)")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

ERROR_PATTERNS = [
    (re.compile(r"\b(more|less|rather|other|better|worse|greater|fewer|sooner|faster|stronger|weaker|higher|lower|larger|smaller)\s+then\b", re.I), "then/than: use than in a comparison"),
    (re.compile(r"\b(and|just|only|since|until|back)\s+than\b", re.I), "then/than: use then for time"),
    (re.compile(r"\b(could|would|should|must|might)\s+of\b", re.I), "modal + of: use have"),
    (re.compile(r"\b(had|has|have|in the|the)\s+past\s+(?=\w+ed\b)", re.I), "passed/past confusion"),
    (re.compile(r"\b(\w+)\s+\1\b", re.I), "doubled word"),
    (re.compile(r"\blaying\s+(there|down|on|in|motionless|still|flat)\b", re.I), "lay/lie: a person lies or lay (past), not laying"),
    (re.compile(r"\b(an|the|any|no|this|that|its)\s+affect\b", re.I), "affect/effect: the noun is effect"),
    (re.compile(r"\b(will|to|would|could|can|might|not)\s+effect\s+(on|the|him|her|them)\b", re.I), "affect/effect: the verb is affect"),
]
# Doubled words that are legitimate in English prose or approved repetition.
DOUBLED_OK = {"that", "had", "very", "no", "so", "far", "on", "bye", "ha", "haha", "boom", "rumble", "tsk"}

WARN_PATTERNS = [
    (re.compile(r"\b(upon|whilst|amidst|amongst|thereupon|hitherto)\b", re.I), "bookish diction; prefer on, while, amid/among or plainer wording"),
    (re.compile(r"\bat this time\b", re.I), "calque 'at this time'"),
    (re.compile(r"\bin a short while\b", re.I), "calque 'in a short while'"),
    (re.compile(r"\bit can be said that\b", re.I), "calque 'it can be said that'"),
    (re.compile(r"(?:^|[.!?]\s+)As for [^,.]{1,60}, (he|she|they|it|his|her|their)\b"), "calque 'As for X, he': make X the subject"),
    (re.compile(r"\b(carr(?:y|ied|ying) out|conduct(?:ed|ing)?|ma(?:ke|de|king)|perform(?:ed|ing)?)\s+(an?|the)\s+\w*(tion|ment|ance|ence|sis)\b", re.I), "nominalized verb; use the verb itself"),
    (re.compile(r"\b(very|extremely|incredibly|utterly|truly|really|completely|absolutely)\s+(very|extremely|incredibly|utterly|truly|really|completely|absolutely)\b", re.I), "stacked intensifiers"),
    (re.compile(r"\b(each and every|first and foremost|null and void|full and complete|sudden and abrupt|end result)\b", re.I), "redundant doublet"),
]

CONTRACTABLE_RE = re.compile(
    r"\b(do not|does not|did not|is not|are not|was not|were not|cannot|will not|"
    r"would not|could not|should not|have not|has not|had not|I am|it is|that is|"
    r"you are|we are|they are|there is|what is|let us)\b"
)
QUOTE_OR_THOUGHT_RE = re.compile(r'"[^"]*"|\*[^*]+\*')

STOPWORDS = set("""
a an the and or but if then than so as at by for from in into of on onto to with without
he she it they them him her his hers its their theirs we us our you your i me my mine this
that these those who whom whose which what when where why how was were is are be been being
had has have having do does did done not no nor all any each every some such only just even
still also again once more most much many very too own same other another there here now
then up down out off over under about after before while since until through upon one two
would could should will shall can may might must lü yang said like back away yet though
""".split())

TRAILING_PARTICIPLE_RE = re.compile(r",\s+(?:[a-z]+ly\s+)?(?!(?:nothing|something|anything|everything|during|morning|evening|king|ring|thing|wing|string|bring|being)\b)[a-z]+ing\b[^,.!?\"]*[.!?]\s*$")


def _prose(paragraph: str) -> bool:
    return bool(paragraph) and not DISPLAY_LINE_RE.match(paragraph) and paragraph != "---"


def paragraph_errors(target: list[str]) -> list[str]:
    errors: list[str] = []
    for index, para in enumerate(target, 1):
        if not _prose(para) or index == 1:
            continue
        if re.search(r"[,;]\s*$", para):
            errors.append(f"paragraph {index}: ends with a comma or semicolon; a lead-in belongs with what it introduces")
        if re.match(r"^[*\"']*[a-z]", para) and not re.match(r"^\*?[a-z]+\*?$", para):
            errors.append(f"paragraph {index}: starts in lowercase; a sentence is split across paragraphs")
        for pattern, label in ERROR_PATTERNS:
            for match in pattern.finditer(para):
                if label == "doubled word" and match.group(1).lower() in DOUBLED_OK:
                    continue
                errors.append(f"paragraph {index}: {label}: {match.group(0)!r}")
    return errors


def _sentences(para: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.findall(para) if s.strip()]


def _opener(sentence: str) -> str:
    words = WORD_RE.findall(sentence.lstrip('*"\''))
    return " ".join(words[:2]).lower()


def paragraph_warnings(target: list[str], protected: set[str]) -> list[str]:
    warnings: list[str] = []
    for index, para in enumerate(target, 1):
        if not _prose(para) or index == 1:
            continue
        for pattern, label in WARN_PATTERNS:
            for match in pattern.finditer(para):
                if match.group(0).lower() == "upon" and re.search(r"\b(\w+) upon \1\b|once upon", para, re.I):
                    continue
                warnings.append(f"paragraph {index}: {label}: {match.group(0).strip()!r}")
        for span in QUOTE_OR_THOUGHT_RE.findall(para):
            for match in CONTRACTABLE_RE.finditer(span):
                warnings.append(f"paragraph {index}: uncontracted '{match.group(0)}' in speech or thought; contract unless formal or emphatic")
        counts: dict[str, int] = {}
        for word in WORD_RE.findall(para):
            low = word.lower().strip("'")
            if len(low) < 4 or low in STOPWORDS or low in protected:
                continue
            root = re.sub(r"(ing|ed|es|s|ly)$", "", low) if len(low) > 5 else low
            counts[root] = counts.get(root, 0) + 1
        repeated = sorted(root for root, count in counts.items() if count >= 3)
        if repeated:
            warnings.append(f"paragraph {index}: word or root used three or more times: {', '.join(repeated)}")
        sentences = _sentences(para)
        openers = [_opener(s) for s in sentences]
        for left, right in zip(openers, openers[1:]):
            if left and left == right:
                warnings.append(f"paragraph {index}: consecutive sentences open with '{left}'")
                break
        firsts = [o.split(" ")[0] for o in openers if o]
        for a, b, c in zip(firsts, firsts[1:], firsts[2:]):
            if a == b == c:
                warnings.append(f"paragraph {index}: three consecutive sentences open with '{a}'")
                break
    return warnings


def chapter_warnings(target: list[str], glossary_targets: list[str]) -> list[str]:
    warnings: list[str] = []
    body = "\n".join(p for p in target[1:] if _prose(p))
    item = r"[A-Za-z'-]+(?: [A-Za-z'-]+){0,2}"
    serial = len(re.findall(rf"(?:{item}, ){{2,}}(?:and|or) ", body))
    open_list = len(re.findall(rf"(?:{item}, ){{2,}}{item} (?:and|or) ", body))
    if serial and open_list:
        warnings.append(f"chapter: serial comma used {serial} time(s) and omitted in about {open_list} list(s); use the serial comma throughout")
    for term in glossary_targets:
        if not any(ch.isupper() for ch in term) or " " not in term:
            continue
        exact = body.count(term)
        loose = len(re.findall(re.escape(term), body, re.I))
        if exact and loose > exact:
            warnings.append(f"chapter: capitalization of '{term}' varies within the chapter")
    return warnings


def protected_words(glossary_targets: list[str]) -> set[str]:
    words: set[str] = set()
    for term in glossary_targets:
        for word in WORD_RE.findall(term):
            words.add(word.lower())
    return words
