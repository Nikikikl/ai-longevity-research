import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from zipfile import ZipFile

from scripts import download_data, inspect_data


class DownloadTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory(dir=download_data.ROOT, suffix=".tmp")
        self.addCleanup(temp.cleanup)
        self.archive = Path(temp.name) / "human_genes.zip"
        self.url, self.member = download_data.SOURCES[self.archive.name]

    def write_zip(self, member):
        with ZipFile(self.archive, "w") as zipped:
            zipped.writestr(member, "test fixture")

    def test_untracked_archive_is_not_overwritten(self):
        self.write_zip(self.member)
        original = self.archive.read_bytes()
        with self.assertRaisesRegex(ValueError, "exists without metadata"):
            download_data.acquire(self.archive, self.url, self.member, register_local=False)
        self.assertEqual(self.archive.read_bytes(), original)

    def test_manual_registration_and_tamper_detection(self):
        self.write_zip(self.member)
        download_data.acquire(self.archive, self.url, self.member, register_local=True)
        sidecar = self.archive.with_suffix(".zip.json")
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        self.assertEqual(metadata["source_url"], self.url)
        self.assertIn("registered_at_utc", metadata)
        self.assertEqual(metadata["size_bytes"], self.archive.stat().st_size)
        self.assertEqual(download_data.acquire(self.archive, self.url, self.member, False),
                         "verified existing archive")
        self.archive.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "does not match"):
            download_data.acquire(self.archive, self.url, self.member, register_local=False)

    def test_wrong_official_export_is_rejected(self):
        self.write_zip("wrong-table.tsv")
        with self.assertRaisesRegex(ValueError, "Expected exactly one copy"):
            download_data.acquire(self.archive, self.url, self.member, register_local=True)
        self.assertFalse(self.archive.with_suffix(".zip.json").exists())

    def test_matching_download_restores_missing_archive(self):
        self.write_zip(self.member)
        original = self.archive.read_bytes()
        download_data.acquire(self.archive, self.url, self.member, register_local=True)
        sidecar = self.archive.with_suffix(".zip.json")
        recorded = sidecar.read_bytes()
        self.archive.unlink()

        response = io.BytesIO(original)
        response.geturl = lambda: self.url
        with patch.object(download_data, "build_opener") as build_opener:
            build_opener.return_value.open.return_value = response
            result = download_data.acquire(self.archive, self.url, self.member, register_local=False)

        self.assertEqual(result, "restored archive matching recorded fingerprint")
        self.assertEqual(self.archive.read_bytes(), original)
        self.assertEqual(sidecar.read_bytes(), recorded)

    def test_http_error_leaves_no_archive_or_provenance(self):
        error = HTTPError(self.url, 503, "Service Unavailable", {}, None)
        with patch.object(download_data, "build_opener") as build_opener:
            build_opener.return_value.open.side_effect = error
            with self.assertRaises(HTTPError):
                download_data.acquire(self.archive, self.url, self.member, register_local=False)
        self.assertEqual(list(self.archive.parent.iterdir()), [])


class InspectionTests(unittest.TestCase):
    def test_csv_keeps_quoted_delimiters_blanks_and_duplicates(self):
        sample = io.StringIO('id,name\n1,"Name, suffix"\n\n1,"Name, suffix"\n2,\n')
        columns, rows, blank_lines = inspect_data.read_table(sample, ",")
        self.assertEqual(columns, ["id", "name"])
        self.assertEqual(rows, [("1", "Name, suffix"), ("1", "Name, suffix"), ("2", "")])
        self.assertEqual(blank_lines, 1)

    def test_tsv_rejects_wrong_field_count(self):
        with self.assertRaisesRegex(ValueError, "expected 2 fields, found 1"):
            inspect_data.read_table(io.StringIO("id\tname\n1\n"), "\t")

    def test_identifier_maps_expose_ambiguous_values(self):
        by_entrez, by_symbol = inspect_data.identifier_maps(
            ["1", "1", "2", "3"], ["OLD", "NEW", "NEW", ""],
        )
        self.assertEqual(by_entrez, {"1": {"OLD", "NEW"}, "2": {"NEW"}})
        self.assertEqual(by_symbol, {"OLD": {"1"}, "NEW": {"1", "2"}})


if __name__ == "__main__":
    unittest.main()
