import re

MAX_WORDS_PER_SENTENCE = 25
MIN_WORDS, MAX_WORDS = 500, 1100
REQUIRED_SECTIONS = ["what", "why", "how", "example", "summary"]


def _body_lines(text):
    return [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]


def _sentences(text):
    out = []
    for l in _body_lines(text):
        l = re.sub(r"^[\s>*\-\d.)]+", "", l)
        out += [s.strip() for s in re.split(r"(?<=[.!?])\s+", l) if s.strip()]
    return out


def run_code_checks(text):
    results = []

    long_ones = [s for s in _sentences(text) if len(s.split()) > MAX_WORDS_PER_SENTENCE]
    results.append({
        "id": "sentence_length",
        "pass": not long_ones,
        "reason": "OK" if not long_ones else
        f"{len(long_ones)} sentence(s) exceed {MAX_WORDS_PER_SENTENCE} words, e.g.: \"{long_ones[0][:140]}...\"",
    })

    n = len(text.split())
    results.append({
        "id": "length",
        "pass": MIN_WORDS <= n <= MAX_WORDS,
        "reason": "OK" if MIN_WORDS <= n <= MAX_WORDS else
        f"Lesson has {n} words; must be {MIN_WORDS}-{MAX_WORDS}.",
    })

    headings = " ".join(l.lower() for l in text.splitlines() if l.lstrip().startswith("#"))
    missing = [s for s in REQUIRED_SECTIONS if s not in headings]
    results.append({
        "id": "sections",
        "pass": not missing,
        "reason": "OK" if not missing else f"Missing section headings for: {', '.join(missing)}.",
    })
    return results
