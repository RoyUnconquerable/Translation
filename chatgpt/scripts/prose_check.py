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
    (re.compile(r"\b(passage|way|path|road|gap|crack|hole)\s+though\b|\bthough\s+(time|space|the years)\b", re.I), "though/through typo"),
    (re.compile(r"\blaying\s+(there|down|on|in|motionless|still|flat)\b", re.I), "lay/lie: a person lies or lay (past), not laying"),
    (re.compile(r"\b(an|the|any|no|this|that|its)\s+affect\b", re.I), "affect/effect: the noun is effect"),
    (re.compile(r"\b(will|to|would|could|can|might|not)\s+effect\s+(on|the|him|her|them)\b", re.I), "affect/effect: the verb is affect"),
]
# Doubled words that are legitimate in English prose or approved repetition.
DOUBLED_OK = {"that", "had", "very", "no", "so", "far", "on", "bye", "ha", "haha", "boom", "rumble", "tsk"}

WARN_PATTERNS = [
    (re.compile(r"\bat this time\b", re.I), "calque 'at this time'"),
    (re.compile(r"\bin a short while\b", re.I), "calque 'in a short while'"),
    (re.compile(r"\bit can be said that\b", re.I), "calque 'it can be said that'"),
    (re.compile(r"(?:^|[.!?]\s+)As for [^,.]{1,60}, (he|she|they|it|his|her|their)\b"), "calque 'As for X, he': make X the subject"),
    (re.compile(r"\b(carr(?:y|ied|ying) out|conduct(?:ed|ing)?|ma(?:ke|de|king)|perform(?:ed|ing)?)\s+(an?|the)\s+\w*(tion|ment|ance|ence|sis)\b", re.I), "nominalized verb; use the verb itself"),
    (re.compile(r"\b(very|extremely|incredibly|utterly|truly|really|completely|absolutely)\s+(very|extremely|incredibly|utterly|truly|really|completely|absolutely)\b", re.I), "stacked intensifiers"),
    (re.compile(r"\b(each and every|first and foremost|null and void|full and complete|sudden and abrupt|end result)\b", re.I), "redundant doublet"),
    # Owner Ch.1432: plain order and explicit logic over literary constructions.
    (re.compile(r"\bno sooner (would|did|had|could|was|were)\b", re.I), "inverted 'no sooner'; prefer the moment he..."),
    (re.compile(r"\bWith [^.!?]{3,90}, and with\b"), "stacked with-phrases; make one of them a main clause"),
    (re.compile(r", for (he|she|they|we|I|you|without|before|there|it was|it had|it would)\b"), "conjunction 'for'; prefer because or since"),
    # Owner Ch.1432 sound pass (editing-spec 2.4): showy devices, stacks and caption tails.
    (re.compile(r"\bof all things\b|\bnot unlike\b|\b(\w+), really \1\b", re.I), "showy device; say it plainly"),
    (re.compile(r"\bWhat was more\b"), "stiff connector; prefer More importantly or Besides"),
    (re.compile(r"\bbefore (his|her|their) \w+th (year|birthday)\b", re.I), "literary age phrase; prefer before he was even N years old"),
    (re.compile(r", (his|her|their)( entire| whole)? (gaze|gazes|focus|attention|eyes) (full of|fixed on|locked on|filled with)\b"), "caption tail; tie it to the actor with as or a participle"),
    (re.compile(r"\b[A-Z][\w-]*'s(?: [A-Z][a-z]+){2,} [a-z]+ (?:is|was|were|are|had|has)\b"), "noun stack after a possessive; unpack with of"),
    # Owner Ch.1433: a participle opener must attach to the person, not his brow or gaze.
    (re.compile(r"(?:^|[.!?]\s+)(?:Seeing|Hearing|Watching|Listening to|Looking at|Having \w+|After \w+ing)[^,.!?]{0,60}, (?:his|her|their|[A-Z][\w-]*(?: [A-Z][\w-]*)*(?:'s|s'))\s"), "dangling participle; make the person the subject"),
]

# Collocations the owner replaced; extend from each owner revision (editing-spec 2.4).
COLLOCATION_FIXES = [
    (re.compile(r"\b(gloom|darkness) crossed\b", re.I), "a shadow crossed (owner Ch.1432)"),
    (re.compile(r"\bdrained to (black|white|gr[ae]y)\b", re.I), "drained of color (owner Ch.1432)"),
    (re.compile(r"\blaid down in the unseen\b", re.I), "some unseen limit (owner Ch.1432)"),
    (re.compile(r"\bthe momentum was (already )?(his|hers|theirs)\b", re.I), "secured the overall advantage (owner Ch.1432)"),
    (re.compile(r"\bvault of the sky\b", re.I), "the dome of heaven (owner Ch.1433)"),
    (re.compile(r"\bdeathlessness\b", re.I), "immortality (owner Ch.1433)"),
    (re.compile(r"\bPeach Blossom Spring\b"), "a secluded paradise (owner Ch.1433)"),
    (re.compile(r"\bblood burst into light\b", re.I), "blood-red light exploded (owner Ch.1433)"),
]

CONTRACTABLE_RE = re.compile(
    r"\b(do not|does not|did not|is not|are not|was not|were not|cannot|will not|"
    r"would not|could not|should not|have not|has not|had not|I am|it is|that is|"
    r"you are|we are|they are|there is|what is|let us)\b"
)
# Owner V2 review: bookish words grate in a casual voice; narration may keep them (owner Ch.1431).
BOOKISH_RE = re.compile(r"\b(upon|whilst|amidst|amongst|thereupon|hitherto)\b", re.I)
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
        if re.search(r"(?:^|\s)_\S", para) or para.count("*") % 2:
            errors.append(f"paragraph {index}: unbalanced or underscore italics; wrap thought spans in paired asterisks")
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
                warnings.append(f"paragraph {index}: {label}: {match.group(0).strip()!r}")
        for pattern, fix in COLLOCATION_FIXES:
            for match in pattern.finditer(para):
                warnings.append(f"paragraph {index}: unidiomatic collocation {match.group(0)!r}; prefer {fix}")
        for span in QUOTE_OR_THOUGHT_RE.findall(para):
            for match in BOOKISH_RE.finditer(span):
                if match.group(0).lower() == "upon" and re.search(r"\b(\w+) upon \1\b|once upon", span, re.I):
                    continue
                warnings.append(f"paragraph {index}: bookish diction in speech or thought; prefer on, while, amid/among: {match.group(0)!r}")
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


# Stock phrases the owner varies once they recur within a chapter (owner Ch.1432).
STOCK_PHRASES = (
    "without the slightest hesitation", "without hesitation", "not the slightest",
    "couldn't help", "at the sight", "a trace of", "in the blink of an eye",
)


def chapter_warnings(target: list[str], glossary_targets: list[str]) -> list[str]:
    warnings: list[str] = []
    body = "\n".join(p for p in target[1:] if _prose(p))
    for phrase in STOCK_PHRASES:
        count = len(re.findall(rf"\b{re.escape(phrase)}\b", body, re.I))
        if count >= 3:
            warnings.append(f"chapter: stock phrase '{phrase}' used {count} times; vary it after the second use")
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
