"""Render scientific evidence results as readable HTML."""
from html import escape
from math import isfinite

from scripts.research_assistant import reference_links

STATUS_LABELS = {
    "answered": "Answered",
    "not_measured": "Not measured",
    "insufficient_evidence": "Insufficient evidence",
    "unsupported_question": "Unsupported question",
}

EVIDENCE_LABELS = {
    "go_annotation": "GO annotation",
    "cellage_perturbation_record": "CellAge perturbation record",
    "genage_membership": "GenAge membership",
}

METRIC_LABELS = {
    "tested": ("Genes tested", ""),
    "panel": ("Panel size", ""),
    "agree": ("Matching signs", ""),
    "percent": ("Sign agreement", "%"),
    "discovery_r": ("Discovery partial r", ""),
    "validation_r": ("Validation partial r", ""),
    "both_concordant": ("Both, same direction", ""),
    "target": ("Replication score", ""),
    "matched_median": ("Matched median", ""),
    "permutation_p": ("Permutation p", ""),
    "ridge_mae": ("Ridge MAE", " years"),
    "median_age_mae": ("Median age MAE", " years"),
    "matched_median_mae": ("Matched panel MAE", " years"),
    "rows": ("Source rows", ""),
    "distinct_pmids": ("Distinct PMIDs", ""),
}

LOCAL_FIELDS = {
    "path": "Local source",
    "locator": "Locator",
    "member": "Archive member",
    "raw_path": "Local raw file",
    "ledger": "Local ledger",
    "source_reference": "Source reference",
    "pmid": "PMID",
    "doi": "DOI",
}


def reference_html(reference):
    links = [
        f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{label} ↗</a>'
        for label, url in reference_links(reference)
    ]
    locations = [
        f'<div class="reference-location"><span>{label}</span> <code>{escape(str(reference[field]))}</code></div>'
        for field, label in LOCAL_FIELDS.items() if reference.get(field)
    ]
    identifier = escape(str(reference["id"]))
    return (f'<li><div class="reference-heading"><strong>{identifier}</strong>{"".join(links)}</div>'
            f'{"".join(locations)}</li>')


def numerical_findings(facts, status):
    labels = dict(METRIC_LABELS)
    group = "hits" if "both_concordant" in facts else "donors"
    labels.update(discovery=(f"Discovery {group}", ""), validation=(f"Validation {group}", ""))
    for field, value in facts.items():
        if field not in labels:
            continue
        label, suffix = labels[field]
        if type(value) in (int, float) and isfinite(value):
            yield label, f"{value}{suffix}"
        elif value is None and status == "not_measured" and field in {"discovery_r", "validation_r"}:
            yield label, "Not measured"


def answer_html(result):
    status = result["status"]
    answer = result["answer"]
    if status == "unsupported_question":
        answer = "The selected mode could not interpret this request. Try an example or switch evidence modes."
    kind = result["evidence_type"]
    evidence = escape(EVIDENCE_LABELS.get(kind, kind.replace("_", " ").capitalize()))
    parts = [f'<div class="answer-copy">{escape(answer)}</div>',
             f'<div class="answer-meta"><span class="status {status}">{STATUS_LABELS[status]}</span>'
             f'<span class="evidence-type">{evidence}</span></div>']

    metrics = list(numerical_findings(result["facts"], status))
    if metrics:
        cards = "".join(f'<div><strong>{escape(value)}</strong><span>{escape(label)}</span></div>'
                        for label, value in metrics)
        parts.append(f'<h4>Key figures</h4><div class="metrics">{cards}</div>')

    if result["references"]:
        sources = "".join(reference_html(ref) for ref in result["references"])
        title = "Scope references" if status == "unsupported_question" else "Sources"
        parts.append(f'<h4>{title}</h4><ul class="references">{sources}</ul>')

    if result["limitations"]:
        limits = "".join(f"<li>{escape(limit)}</li>" for limit in result["limitations"])
        parts.append(f'<h4>Limitations</h4><ul class="limitations">{limits}</ul>')

    if result.get("details"):
        fields = "".join(f"<dt>{escape(key.replace('_', ' ').capitalize())}</dt><dd>{escape(value)}</dd>"
                         for key, value in result["details"].items())
        parts.append(f'<details class="study-details"><summary>Reviewed record details</summary><dl>{fields}</dl></details>')
    return f'<div class="scientific-answer">{"".join(parts)}</div>'
