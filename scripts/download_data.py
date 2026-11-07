"""Retrieve the official HAGR archives and record their provenance."""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from http.client import HTTPException
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
HAGR = "https://genomics.senescence.info"
SOURCES = {
    "human_genes.zip": (f"{HAGR}/genes/human_genes.zip", "genage_human.csv"),
    "cellAge.zip": (f"{HAGR}/cells/cellAge.zip", "cellage3.tsv"),
}


class OfficialRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlsplit(newurl)
        if target.scheme != "https" or target.netloc != urlsplit(HAGR).netloc:
            raise URLError(f"Refusing redirect outside official HTTPS source: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def publish_new(path, contents):
    """Publish a complete file atomically and fail if the destination exists."""
    with NamedTemporaryFile(dir=path.parent, suffix=".part") as staged:
        staged.write(contents)
        staged.flush()
        path.hardlink_to(staged.name)


def fingerprint(contents):
    return {"size_bytes": len(contents), "sha256": hashlib.sha256(contents).hexdigest()}


def verify_archive(archive, url):
    return verify_contents(archive.with_suffix(".zip.json"), url, archive.read_bytes())


def verify_contents(sidecar, url, contents):
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    expected = {"source_url": url, **fingerprint(contents)}
    if not isinstance(metadata, dict) or any(metadata.get(key) != value for key, value in expected.items()):
        raise ValueError("Archive or source URL does not match its provenance record.")
    return metadata


def acquire(archive, url, member, register_local):
    sidecar = archive.with_suffix(".zip.json")
    if sidecar.exists() and archive.exists():
        verify_archive(archive, url)
        return "verified existing archive"

    if register_local:
        contents = archive.read_bytes()
        timing = {"registered_at_utc": datetime.now(UTC).isoformat(timespec="seconds")}
    else:
        if archive.exists():
            raise ValueError("Archive exists without metadata. Use --register-local for an official copy.")
        opener = build_opener(OfficialRedirects())
        request = Request(url, headers={"User-Agent": "ai-longevity-research/0.1"})
        with opener.open(request, timeout=30) as response:
            contents = response.read()
            timing = {
                "downloaded_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
                "response_url": response.geturl(),
            }

    # Verify ZIP integrity without unpacking anything to disk.
    with ZipFile(BytesIO(contents)) as zipped:
        if zipped.namelist().count(member) != 1:
            raise ValueError(f"Expected exactly one copy of {member} in the ZIP archive.")
        damaged = zipped.testzip()
        if damaged is not None:
            raise BadZipFile(f"ZIP member failed checksum: {damaged}")

    if sidecar.exists():
        verify_contents(sidecar, url, contents)
        publish_new(archive, contents)
        return "restored archive matching recorded fingerprint"

    if not register_local:
        publish_new(archive, contents)
    metadata = {"source_url": url, **timing, **fingerprint(contents)}
    publish_new(sidecar, (json.dumps(metadata, indent=2) + "\n").encode("utf-8"))
    return "registered local archive" if register_local else "downloaded archive"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--register-local", action="store_true",
        help="Record fingerprints for manually downloaded official archives; make no network requests.",
    )
    args = parser.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    failed = False
    for filename, (url, member) in SOURCES.items():
        try:
            result = acquire(RAW_DIR / filename, url, member, args.register_local)
            print(f"{filename}: {result}")
        except (OSError, ValueError, HTTPException, BadZipFile) as error:
            print(f"{filename}: {error}", file=sys.stderr)
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
