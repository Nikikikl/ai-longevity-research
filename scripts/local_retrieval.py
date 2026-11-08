"""Deterministic lexical search over the published research reports."""

from collections import Counter
from dataclasses import dataclass
from itertools import groupby
from math import log
from pathlib import Path
import re
from textwrap import shorten

ROOT = Path(__file__).resolve().parents[1]
# The five reports are identical in the working tree and the v2.0.0 release.
REPORT_URL = "https://github.com/Nikikikl/ai-longevity-research/blob/ba0365a234d4b0b4bf16bc8aa5ce5049dbf7819a"
REPORTS = {
    "V2": "reports/research_report_v2.md",
    "GENES": "reports/gene_case_studies.md",
    "P7D": "reports/phase7d_case_studies.md",
    "P7A": "reports/phase7_baseline_results.md",
    "P7B": "reports/phase7b_evidence_audit.md",
}
MAX_PASSAGES = 4
MAX_PASSAGE_CHARS = 1650
MAX_EVIDENCE_CHARS = 3600

GENES = {"tp53", "cdkn2a", "tert", "foxo3", "sirt6"}
ALIASES = {
    "p53": "tp53", "trp53": "tp53", "htert": "tert", "foxo3a": "foxo3",
    "replicate": "replication", "replicated": "replication",
    "restore": "restoration", "restored": "restoration", "restoring": "restoration",
    "measured": "measure", "measurement": "measure",
    "interventional": "intervention", "intervening": "intervention", "observational": "association",
    "knocked": "knockdown", "silencing": "knockdown", "sirna": "knockdown",
    "agreed": "agreement", "mice": "mouse", "overexpressing": "overexpression", "people": "human",
}
# A small query vocabulary for common Russian phrasings of the indexed topics.
RUSSIAN_PREFIXES = {
    "сенесцен": "senescence", "старен": "senescence", "фибробласт": "fibroblast",
    "хондроцит": "chondrocyte", "карцином": "carcinoma", "восстанов": "restoration",
    "теломераз": "telomerase", "теломер": "telomere", "долголет": "longevity",
    "продолжительност": "lifespan", "мыш": "mouse", "самц": "male", "самок": "female",
    "челов": "human", "люд": "human", "генотип": "genotype", "ассоциац": "association",
    "вмешательств": "intervention", "репликатив": "replicative", "репликац": "replication",
    "корреляц": "correlation", "экспресс": "expression", "измер": "measure",
    "когорт": "cohort", "фильтр": "filter", "подавлен": "knockdown", "нокдаун": "knockdown",
    "пролиферац": "proliferation", "удвоен": "doubling", "арест": "arrest",
}
STOP_WORDS = set("""
    about after again also and any are because been before being both but can could did does for from
    had happen happened has have how into its long may more most only our over phase researcher
    same should some take than that the their them then there these they thing this those through
    under use used very was were what when where which
    who why will with would you your
    как что это этот этой там для при или был была были чем ли по на от до мы вы они их
""".split())
FOLLOW_UP = re.compile(
    r"^(?:and\b|what about\b|why\??$|а\s|и\s|почему\??$)"
    r"|\b(?:it|its|that|they|their|those|this|both|same|это|этот|они|его|эти)\b",
    re.IGNORECASE,
)
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")


@dataclass(frozen=True)
class Passage:
    id: str
    path: str
    heading: str
    start: int
    end: int
    text: str

    @property
    def url(self):
        lines = f"L{self.start}" if self.start == self.end else f"L{self.start}-L{self.end}"
        return f"{REPORT_URL}/{self.path}?plain=1#{lines}"


def terms(text):
    text = text.casefold()
    result = set()
    if "same direction" in text or "concordant signs" in text or "cross-cohort gene screen" in text:
        result.add("replication")
    for token in re.findall(r"[^\W_]+", text):
        if len(token) < 3 and token not in {"ej", "7a", "7b", "7c", "7d"}:
            continue
        token = next((word for prefix, word in RUSSIAN_PREFIXES.items() if token.startswith(prefix)), token)
        if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
            token = token[:-1]
        if token not in STOP_WORDS:
            result.add(ALIASES.get(token, token))
    return result


def read_passages():
    passages = []
    for code, path in REPORTS.items():
        heading = ""
        lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
        for nonblank, group in groupby(enumerate(lines, 1), key=lambda row: bool(row[1].strip())):
            if not nonblank:
                continue
            block = list(group)
            _, first = block[0]
            if first.startswith("#"):
                heading = first.lstrip("# ").split(" | ", 1)[0]
                continue
            if first.startswith(("![", "```")):
                continue
            chunks = [[row] for row in block] if first.startswith("- ") else [block]
            for chunk in chunks:
                start, end = chunk[0][0], chunk[-1][0]
                excerpt = MARKDOWN_LINK.sub(r"\1", "\n".join(line for _, line in chunk))
                if len(excerpt) > MAX_PASSAGE_CHARS:
                    excerpt = shorten(excerpt, width=MAX_PASSAGE_CHARS, placeholder=" …")
                passages.append(Passage(f"{code}-L{start}-L{end}", path, heading, start, end, excerpt))
    return tuple(passages)


def retrieve(question, prior_questions=()):
    passages = read_passages()
    index = [(passage, terms(passage.text), terms(passage.heading)) for passage in passages]
    frequencies = Counter(term for _, body, heading in index for term in body | heading)
    current = terms(question)
    target_genes = current & GENES
    context = set()
    if FOLLOW_UP.search(question.strip()):
        for prior in reversed(prior_questions):
            prior_terms = terms(prior)
            context |= prior_terms
            if prior_terms & GENES:
                target_genes = target_genes or prior_terms & GENES
                break

    def weight(term):
        return 1 + log((1 + len(index)) / (1 + frequencies[term]))

    ranked = []
    for passage, body, heading in index:
        matched = current & (body | heading)
        relevant_genes = target_genes & (body | heading)
        if target_genes:
            if not relevant_genes or (not matched and current):
                continue
        elif len(matched) < 2:
            continue
        score = sum(weight(term) for term in sorted(matched))
        score += 0.25 * sum(weight(term) for term in sorted((context & body) - current))
        # A gene-specific section is more focused than an incidental mention.
        if passage.heading.casefold() in relevant_genes:
            score += 2
        ranked.append((-score, passage.id, passage))

    selected = []
    remaining = MAX_EVIDENCE_CHARS
    for _, _, passage in sorted(ranked):
        if len(passage.text) <= remaining:
            selected.append(passage)
            remaining -= len(passage.text)
        if len(selected) == MAX_PASSAGES:
            break
    return tuple(selected)
