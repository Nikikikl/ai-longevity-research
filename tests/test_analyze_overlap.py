import csv
import hashlib
import io
import json
import unittest

from scripts import analyze_overlap as overlap


def mapping_row(export, gene_id, ordinals, symbol="GENE"):
    return {
        "source": export.title,
        "source_archive": export.archive,
        "source_member": overlap.SOURCES[export.archive][1],
        "source_entrez_id": gene_id,
        "source_symbols": json.dumps([symbol]),
        "source_genage_ids": '["12"]' if export == overlap.GENAGE else "[]",
        "source_record_numbers": json.dumps(ordinals),
        "evidence_count": str(len(ordinals)),
        "status": "confirmed",
        "ncbi_status": "current_human",
        "approved_hgnc_id": f"HGNC:{gene_id}",
        "approved_symbol": symbol,
    }


class OverlapTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            mapping_row(overlap.GENAGE, "1", [1]),
            mapping_row(overlap.GENAGE, "2", [2]),
            mapping_row(overlap.CELLAGE, "2", [1, 3]),
            mapping_row(overlap.CELLAGE, "3", [2]),
        ]

    def test_gene_sets_partition_union_and_preserve_duplicate_gene_evidence(self):
        genage, cellage, excluded = overlap.confirmed_sets(self.rows)
        groups = overlap.compare(genage, cellage)
        self.assertEqual(groups, ({"1"}, {"2"}, {"3"}, {"1", "2", "3"}))
        self.assertEqual(excluded, [])
        [shared] = csv.DictReader(io.StringIO(overlap.render_genes(genage, cellage, groups[1])))
        self.assertEqual(shared["entrez_gene_id"], "2")
        self.assertEqual(shared["cellage_evidence_count"], "2")
        self.assertEqual(json.loads(shared["cellage_source_record_numbers"]), [1, 3])

    def test_shared_gene_requires_hgnc_id_and_symbol_agreement(self):
        for field, value in (("approved_hgnc_id", "HGNC:9000"), ("approved_symbol", "OTHER")):
            with self.subTest(field=field):
                changed = [*self.rows[:2], {**self.rows[2], field: value}, self.rows[3]]
                genage, cellage, _ = overlap.confirmed_sets(changed)
                with self.assertRaisesRegex(ValueError, "disagree for shared Gene ID 2"):
                    overlap.compare(genage, cellage)

    def test_hgnc_accession_cannot_confirm_two_gene_ids(self):
        self.rows[3]["approved_hgnc_id"] = "HGNC:1"
        with self.assertRaisesRegex(ValueError, "different confirmed Entrez Gene IDs"):
            overlap.confirmed_sets(self.rows)

    def test_duplicate_mapping_or_evidence_reference_fails(self):
        with self.assertRaisesRegex(ValueError, "Duplicate confirmed gene"):
            overlap.confirmed_sets([*self.rows, mapping_row(overlap.CELLAGE, "2", [4])])
        with self.assertRaisesRegex(ValueError, "repeated source record ordinals"):
            overlap.confirmed_sets([*self.rows, mapping_row(overlap.CELLAGE, "4", [3])])

    def test_unresolved_candidates_change_only_hypothetical_counts(self):
        conflict = mapping_row(overlap.CELLAGE, overlap.CONFLICT_ID, [4], "FNTB")
        conflict.update(
            status="conflicting_symbol",
            approved_hgnc_id="",
            approved_symbol="",
            id_candidates='["HGNC:100529261 CHURC1-FNTB (Gene ID 100529261)"]',
            other_symbol_candidates='["HGNC:1 FNTB (Gene ID 1)"]',
        )
        genage, cellage, excluded = overlap.confirmed_sets([*self.rows, conflict])
        self.assertEqual(excluded, [conflict])
        self.assertNotIn(overlap.CONFLICT_ID, cellage)
        self.assertNotIn("1", cellage)
        row, scenarios = overlap.sensitivity(excluded, genage, cellage)
        self.assertEqual(row["source_record_numbers"], "[4]")
        self.assertEqual([scenario[2:] for scenario in scenarios], [(False, 1), (True, 2)])
        self.assertEqual(overlap.compare(genage, cellage)[1], {"2"})

    def test_output_is_deterministic_for_different_input_orders(self):
        rows = [
            *self.rows,
            mapping_row(overlap.GENAGE, "10", [3]),
            mapping_row(overlap.CELLAGE, "10", [4]),
        ]
        original = overlap.confirmed_sets(rows)
        reversed_order = overlap.confirmed_sets(reversed(rows))
        outputs = []
        for genage, cellage, _ in (original, reversed_order):
            groups = overlap.compare(genage, cellage)
            outputs.append((overlap.render_genes(genage, cellage, groups[1]), overlap.render_figure(groups)))
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual([r["entrez_gene_id"] for r in csv.DictReader(io.StringIO(outputs[0][0]))], ["2", "10"])

    def test_mapping_must_match_phase2_audit_pin(self):
        mapping = b"pinned mapping"
        digest = hashlib.sha256(mapping).hexdigest()
        audit = f"Generated `data/processed/gene_mapping.csv` SHA-256 — `{digest}`.\n"
        self.assertEqual(overlap.verify_mapping(mapping, audit), digest)
        with self.assertRaisesRegex(ValueError, "differs"):
            overlap.verify_mapping(b"changed", audit)
        with self.assertRaisesRegex(ValueError, "Expected one pinned"):
            overlap.verify_mapping(mapping, audit + audit)


if __name__ == "__main__":
    unittest.main()
