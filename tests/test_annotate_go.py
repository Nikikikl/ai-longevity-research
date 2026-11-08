import io
import unittest

from scripts import annotate_go as go


def gene(entrez, symbol):
    return {"entrez_gene_id": entrez, "approved_symbol": symbol}


def hgnc(*rows):
    header = "status\thgnc_id\tentrez_id\tsymbol\tuniprot_ids\n"
    return io.StringIO(header + "\n".join(rows) + "\n")


def gaf_row(accession="P12345", relation="involved_in", go_id="GO:0000001", code="IDA",
            aspect="P", taxon="taxon:9606", db="UniProtKB"):
    return [
        db, accession, "SOURCE_SYMBOL", relation, go_id, "PMID:1", code, "", aspect,
        "", "", "protein", taxon, "20260101", "UniProt", "", f"UniProtKB:{accession}-2",
    ]


class GoAnnotationTests(unittest.TestCase):
    def setUp(self):
        self.genes = {"HGNC:1": gene("10", "APPROVED")}
        self.lookup = {"P12345": "HGNC:1", "Q12345": "HGNC:1"}
        self.terms = {
            "GO:0000001": ("GO:0000001", "test process"),
            "GO:0000002": ("GO:0000001", "test process"),
            go.BP_ROOT: (go.BP_ROOT, "biological_process"),
        }

    def collect(self, *rows):
        return go.collect_annotations(enumerate(rows, start=5), self.lookup, self.genes, self.terms, "test-release")

    def test_quoted_one_to_many_cross_references_are_preserved(self):
        lookup, candidates, ambiguous = go.map_accessions(
            self.genes, hgnc('Approved\tHGNC:1\t10\tAPPROVED\t"P12345|Q12345"'))
        self.assertEqual(lookup, self.lookup)
        self.assertEqual(candidates, {"HGNC:1": {"P12345", "Q12345"}})
        self.assertEqual(ambiguous, {})

    def test_missing_and_ambiguous_accessions(self):
        genes = {**self.genes, "HGNC:2": gene("20", "NO_XREF")}
        lookup, candidates, ambiguous = go.map_accessions(genes, hgnc(
            "Approved\tHGNC:1\t10\tAPPROVED\tP12345",
            "Approved\tHGNC:2\t20\tNO_XREF\t",
            "Approved\tHGNC:3\t30\tOUTSIDE_OVERLAP\tP12345",
        ))
        self.assertEqual(lookup, {})
        self.assertEqual(candidates["HGNC:2"], set())
        self.assertEqual(ambiguous, {"P12345": ["HGNC:1", "HGNC:3"]})

    def test_approved_hgnc_identity_requires_entrez_agreement(self):
        with self.assertRaisesRegex(ValueError, "identity disagrees"):
            go.map_accessions(self.genes, hgnc("Approved\tHGNC:1\t99\tAPPROVED\tP12345"))

    def test_gaf_keeps_line_numbers_trailing_fields_and_checks_version(self):
        line = "\t".join(gaf_row()[:-1] + [""])
        headers = {}
        [(number, fields)] = go.gaf_rows(io.StringIO(f"!gaf-version: 2.2\n{line}\n"), headers)
        self.assertEqual(number, 2)
        self.assertEqual(fields[-1], "")
        self.assertEqual(headers, {"gaf-version": "2.2"})
        with self.assertRaisesRegex(ValueError, "expected 17"):
            list(go.gaf_rows(io.StringIO("!gaf-version: 2.2\nshort\n"), {}))
        with self.assertRaisesRegex(ValueError, "Expected a GAF 2.2"):
            list(go.gaf_rows(io.StringIO(f"!gaf-version: 2.1\n{line}\n"), {}))

    def test_filter_and_separate_not_nd_root_and_unknown_term(self):
        positive, negated, nd, root, unknown = self.collect(
            gaf_row(go_id="GO:0000002"),
            gaf_row(relation="NOT|involved_in"),
            gaf_row(go_id=go.BP_ROOT, code="ND"),
            gaf_row(go_id=go.BP_ROOT),
            gaf_row(go_id="GO:9999999"),
            gaf_row(aspect="F"),
            gaf_row(taxon="taxon:10090|taxon:9606"),
            gaf_row(db="RNAcentral"),
            gaf_row(accession="UNMAPPED"),
        )
        self.assertEqual(positive["gaf_go_id"], "GO:0000002")
        self.assertEqual(positive["go_id"], "GO:0000001")
        self.assertEqual(positive["gene_product_form_id"], "UniProtKB:P12345-2")
        self.assertEqual(negated["relation"], "NOT|involved_in")
        self.assertEqual([r["status"] for r in [positive, negated, nd, root, unknown]],
                         ["positive", "negated", "no_data", "root", "unresolved_term"])
        summary, covered, covered_non_iea, codes = go.summarize([positive, negated, nd, root, unknown])
        self.assertEqual(len(summary), 1)
        self.assertEqual(covered, covered_non_iea)
        self.assertEqual(codes, {"IDA": 1})

    def test_deduplicate_gene_term_counts_across_evidence_and_accessions(self):
        rows = self.collect(gaf_row(code="IEA"), gaf_row(accession="Q12345", code="IBA"),
                            gaf_row(accession="Q12345", code="IBA"))
        summary, covered, covered_non_iea, codes = go.summarize(rows)
        self.assertEqual(summary, [{"go_id": "GO:0000001", "go_term": "test process",
                                    "unique_genes": 1, "unique_genes_excluding_iea": 1}])
        self.assertEqual((covered, covered_non_iea, codes), ({"HGNC:1"}, {"HGNC:1"}, {"IEA": 1, "IBA": 2}))
        self.assertEqual({r["evidence_category"] for r in rows}, {"Electronic", "Phylogenetic"})
        _, _, non_iea_only, _ = go.summarize(rows[:1])
        self.assertEqual(non_iea_only, set())

    def test_evidence_categories_are_distinct(self):
        codes = ("HDA", "IBA", "ISS", "TAS", "IC", "IEA")
        rows = self.collect(*(gaf_row(code=code) for code in codes))
        self.assertEqual([r["evidence_category"] for r in rows],
                         ["Experimental", "Phylogenetic", "Computational", "Author statement",
                          "Curatorial statement", "Electronic"])

    def test_ontology_indexes_only_active_bp_ids_and_aliases(self):
        headers, terms = go.read_ontology(io.StringIO(
            "data-version: releases/test\n\n"
            "[Term]\nid: GO:0000001\nname: process\nnamespace: biological_process\nalt_id: GO:0000002\n\n"
            "[Term]\nid: GO:0000003\nname: function\nnamespace: molecular_function\n\n"
            "[Term]\nid: GO:0000004\nname: obsolete process\nnamespace: biological_process\nis_obsolete: true\n"
        ))
        self.assertEqual(headers, {"data-version": "releases/test"})
        self.assertEqual(terms, {"GO:0000001": ("GO:0000001", "process"), "GO:0000002": ("GO:0000001", "process")})

    def test_summary_and_figure_are_deterministic_under_input_reordering(self):
        terms = {**self.terms, "GO:0000003": ("GO:0000003", "process with < and &")}
        source = list(enumerate([gaf_row(go_id="GO:0000003"), gaf_row()], start=10))
        rows = go.collect_annotations(source, self.lookup, self.genes, terms, "test-release")
        reversed_rows = go.collect_annotations(reversed(source), self.lookup, self.genes, terms, "test-release")
        self.assertEqual(go.render_csv(go.ANNOTATION_FIELDS, rows),
                         go.render_csv(go.ANNOTATION_FIELDS, reversed_rows))
        summary = go.summarize(rows)[0]
        self.assertEqual(summary, go.summarize(reversed(rows))[0])
        self.assertEqual([r["go_id"] for r in summary], ["GO:0000001", "GO:0000003"])
        self.assertIn("&lt; and &amp;", go.render_figure(summary, 1, 1))


if __name__ == "__main__":
    unittest.main()
