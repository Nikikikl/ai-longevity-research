"""Framework-independent access to the existing scientific lookups."""
from ipaddress import ip_address
import re
from typing import Literal
from urllib.parse import urlsplit

from scripts.phase7c_qa import NormalizedEvidence
from scripts.phase7d_evidence import ExpandedEvidence

Mode = Literal["research", "records"]


def answer_question(question: str, *, mode: Mode = "research") -> dict:
    """Return the chosen backend's unmodified evidence response.

    Research mode uses Phase 7C and records mode uses Phase 7D. The result
    contains status, abstains, answer, facts, evidence_type, references and
    limitations, with optional details. Each call is independent.
    """
    if mode == "research":
        return NormalizedEvidence().ask(question)
    if mode == "records":
        return ExpandedEvidence().ask(question)
    raise ValueError(f"Unknown evidence mode: {mode}")


def _public_url(value):
    """Accept public HTTP(S) link targets without fetching them."""
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value) or "\\" in value:
        return None
    try:
        url = urlsplit(value)
        host = url.hostname
        if url.scheme not in {"https", "http"} or not host or url.username is not None or url.port == 0:
            return None
    except ValueError:
        return None
    try:
        address = ip_address(host)
    except ValueError:
        if not re.fullmatch(r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z][a-zA-Z0-9-]*", host or ""):
            return None
        if host.endswith((".local", ".localhost", ".internal", ".test")):
            return None
    else:
        if not address.is_global:
            return None
    return value


def reference_links(reference: dict) -> list[tuple[str, str]]:
    """Resolve public link labels and URLs without reading local paths or the network."""
    public = _public_url(reference.get("url"))
    reviewed = _public_url(reference.get("reviewed_text_url"))
    pmid = str(reference.get("pmid") or "")
    if not public and re.fullmatch(r"[1-9][0-9]*", pmid):
        public = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    links = [("Public source", public)] if public else []
    if reviewed and reviewed != public:
        links.append(("Reviewed text", reviewed))
    return links
