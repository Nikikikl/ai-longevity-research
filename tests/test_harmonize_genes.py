import csv
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import harmonize_genes as genes
from scripts.inspect_data import EXPORTS


class HarmonizationTests(unittest.TestCase):
    def setUp(self):
        self.hgnc = genes.HgncIndex([
            genes.HgncGene("HGNC:1", "1", "CURRENT", ("PREVIOUS",), ("ALIAS", "OTHER")),
            genes.HgncGene("HGNC:2", "2", "OTHER"),
        ])
        self.ncbi = {
            "1": genes.NcbiGene("CURRENT", ("HGNC:1",)),
            "2": genes.NcbiGene("OTHER", ("HGNC:2",)),
            "3": genes.NcbiGene("UNMAPPED", ()),
        }

    def test_approved_previous_and_alias_match_same_reciprocal_id(self):
        for symbol, expected in (("CURRENT", "approved"), ("PREVIOUS", "previous"), ("ALIAS", "alias")):
            with self.subTest(symbol=symbol):
                result = genes.classify("1", [symbol], self.hgnc, self.ncbi)
                self.assertEqual(result["status"], "confirmed")
                self.assertEqual(result["symbol_relation"], expected)
                self.assertEqual(result["approved_hgnc_id"], "HGNC:1")
                self.assertEqual(result["approved_symbol"], "CURRENT")

    def test_symbol_approved_for_another_gene_blocks_confirmation(self):
        result = genes.classify("1", ["CURRENT", "OTHER"], self.hgnc, self.ncbi)
        self.assertEqual(result["ncbi_status"], "current_human")
        self.assertEqual(result["status"], "conflicting_symbol")
        self.assertEqual(result["symbol_relation"], "approved|other_approved")
        self.assertEqual(result["approved_hgnc_id"], "")
        self.assertEqual(result["other_symbol_candidates"], ["HGNC:2 OTHER (Gene ID 2)"])

    def test_missing_id_and_hgnc_never_resolve_by_symbol_alone(self):
        for gene_id, expected in (("01", "invalid_gene_id"), ("4", "missing_ncbi"), ("3", "missing_hgnc")):
            with self.subTest(gene_id=gene_id):
                result = genes.classify(gene_id, ["CURRENT"], self.hgnc, self.ncbi)
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["approved_hgnc_id"], "")

    def test_cross_reference_disagreement_preserves_both_candidates(self):
        self.ncbi["1"] = genes.NcbiGene("OTHER", ("HGNC:2",))
        result = genes.classify("1", ["CURRENT"], self.hgnc, self.ncbi)
        self.assertEqual(result["status"], "ambiguous_hgnc")
        self.assertEqual(len(result["id_candidates"]), 2)
        self.assertEqual(result["approved_symbol"], "")

    def test_one_way_cross_reference_is_unresolved(self):
        self.ncbi["1"] = genes.NcbiGene("CURRENT", ())
        result = genes.classify("1", ["CURRENT"], self.hgnc, self.ncbi)
        self.assertEqual(result["status"], "nonreciprocal_hgnc")
        self.assertEqual(result["approved_symbol"], "")

    def test_evidence_ordinals_survive_gene_grouping_and_csv_serialization(self):
        columns = ["Entrez ID", "Gene symbol", "Gene name", "Reference"]
        rows = [
            ("1", "CURRENT", "Current gene", "100"),
            ("2", "OTHER", "Other gene", "200"),
            ("1", "PREVIOUS", "Current gene", "300"),
            ("", "", "Unknown gene", "400"),
            ("", "", "Unknown gene", "500"),
        ]
        with patch.object(genes, "load_export", return_value=({}, [], (columns, rows, 1))):
            mapped = list(genes.map_export(EXPORTS[1], self.hgnc, self.ncbi, genes.RAW_DIR))
        self.assertEqual([row["source_record_numbers"] for row in mapped], [[1, 3], [2], [4], [5]])
        self.assertEqual([row["evidence_count"] for row in mapped], [2, 1, 1, 1])
        self.assertEqual(mapped[0]["source_symbols"], ["CURRENT", "PREVIOUS"])
        records = list(csv.DictReader(io.StringIO(genes.render_mapping(mapped))))
        self.assertEqual(json.loads(records[0]["source_record_numbers"]), [1, 3])

    def test_reference_fingerprint_rejects_changed_file(self):
        with TemporaryDirectory(dir=genes.ROOT, suffix=".tmp") as directory:
            raw_dir = Path(directory)
            path = raw_dir / "references" / genes.HGNC_FILE
            path.parent.mkdir()
            path.write_bytes(b"new")
            provenance = {path.name: genes.fingerprint(b"old")}
            with self.assertRaisesRegex(ValueError, "pinned reference fingerprint"):
                genes.reference_bytes(raw_dir, path.name, provenance)


if __name__ == "__main__":
    unittest.main()
