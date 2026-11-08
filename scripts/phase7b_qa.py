"""Answer narrow questions from the Phase 7B evidence ledger."""
import argparse
import json
import re

from scripts.phase7b_ledger import AUDITED, LEDGER, METRICS, OVERLAP, ROOT, read_csv

BASELINE = "reports/phase7_baseline_results.md"
ASSOCIATIONS = "reports/phase7_gene_associations.csv"
CASE_STUDIES = "reports/gene_case_studies.md"
REFERENCES = {
    "P7A:association": (BASELINE, "#independent-association-analysis"),
    "P7A:prediction": (BASELINE, "#discovery-prediction-feasibility"),
    "P5A:scope": (CASE_STUDIES, "#scope-and-sources"),
    "P5A:comparison": (CASE_STUDIES, "#comparison"),
}
ASSOC_LIMIT = "Cross-cohort fibroblast expression associations do not measure effects of perturbations."
REUSE_LIMIT = "Repeated references are not independent corroboration; distinct PMIDs do not prove independence."
CELLAGE_EXPERIMENT = {"CDKN2A": "CellAge:152", "TERT": "CellAge:845", "TP53": "CellAge:870"}


class Evidence:
    def __init__(self):
        self.rows = {row["record_id"]: row for row in read_csv(LEDGER)}
        self.association = {r["approved_symbol"]: r for r in read_csv(ASSOCIATIONS)}
        self.overlap = {r["approved_symbol"]: r for r in read_csv(OVERLAP)}
        self.metrics = json.loads((ROOT / METRICS).read_text())
        self.tested = [r for r in self.association.values()
                       if r["gse113957_partial_r"] and r["gse226189_partial_r"]]

    def cellage(self, gene):
        return [r for r in self.rows.values() if r["source"] == "CellAge" and r["approved_symbol"] == gene]

    def reference(self, key):
        ref = {"id": key}
        if key in REFERENCES:
            path, locator = REFERENCES[key]
            return {**ref, "path": path, "locator": locator}
        if key.startswith(("P7A:gene:", "P3:gene:")):
            path = ASSOCIATIONS if key.startswith("P7A:") else OVERLAP
            return {**ref, "path": path, "locator": f"Entrez Gene ID {key.rsplit(':', 1)[1]}"}
        if key.startswith("PMID:"):
            row = next(r for r in self.rows.values() if r["pmid"] == key.split(":")[1])
            return {**ref, "pmid": row["pmid"], "doi": row["doi"], "url": row["citation_url"],
                    "reviewed_text_url": row["reviewed_text_url"]}
        row = self.rows[key]
        location = ({"member": row["source_member"]} if row["source"] == "CellAge" else
                    {"raw_path": f"data/raw/references/{row['source_member']}"})
        return {**ref, "path": row["source_file"], **location,
                "locator": key, "ledger": LEDGER, "source_reference": row["source_reference"],
                "pmid": row["pmid"] or None, "doi": row["doi"] or None}

    def answer(self, answer, evidence_type, facts, keys, limit, status="answered"):
        return {"status": status, "abstains": status != "answered", "answer": answer,
                "facts": facts, "evidence_type": evidence_type,
                "references": [self.reference(k) for k in keys], "limitations": [limit]}

    def association_answer(self, question, gene):
        ref = ("P7A:association",)
        n = len(self.tested)
        limits = ASSOC_LIMIT
        if re.search(r"\bpartial correlations?\b", question) and gene:
            row = self.association[gene]
            d, v = (row[f"{g}_partial_r"] for g in ("gse113957", "gse226189"))
            facts = {"gene": gene, "discovery_status": row["gse113957_status"],
                     "validation_status": row["gse226189_status"],
                     "discovery_r": round(float(d), 3) if d else None,
                     "validation_r": round(float(v), 3) if v else None}
            keys = (f"P7A:gene:{row['entrez_id']}", *ref)
            if not (d and v):
                return self.answer(
                    f"No paired partial correlations were estimated for {gene}: "
                    f"discovery eligibility = {facts['discovery_status']}; validation eligibility = "
                    f"{facts['validation_status']}. Empty estimates are not zeros.",
                    "cohort_analysis", facts, keys, limits, "not_measured")
            return self.answer(
                f"{gene}: discovery r = {float(d):.3f}, validation r = {float(v):.3f}.",
                "cohort_analysis", facts, keys, limits)
        if gene:
            return None
        if "healthy donors" in question:
            facts = self.metrics["donors"]
            prose = f"{facts['discovery']} eligible discovery donors and {facts['validation']} eligible validation donors."
        elif "genes were tested" in question and ("both" in question or "cohort" in question):
            facts = {"tested": n, "panel": len(self.association)}
            prose = f"{n} of {facts['panel']} panel genes were eligible for both cohorts."
        elif re.search(r"\b(sign agreement|directions agreed)\b", question):
            agree = sum(float(r["gse113957_partial_r"]) * float(r["gse226189_partial_r"]) > 0
                        for r in self.tested)
            facts = {"agree": agree, "tested": n, "percent": round(100 * agree / n, 1)}
            prose = f"The signs agreed for {agree} of {n} genes ({facts['percent']:.1f}%)."
        elif re.search(r"\bq\s*<\s*0\.05\b", question) and "cohort" in question:
            d, v = (float(r["gse113957_q"]) < 0.05 for r in self.tested), (
                float(r["gse226189_q"]) < 0.05 for r in self.tested)
            pairs = list(zip(d, v))
            facts = {"discovery": sum(x for x, _ in pairs), "validation": sum(y for _, y in pairs),
                     "both_concordant": sum(x and y and float(r["gse113957_partial_r"])
                                            * float(r["gse226189_partial_r"]) > 0
                                            for (x, y), r in zip(pairs, self.tested))}
            prose = (f"Discovery: {facts['discovery']}; validation: {facts['validation']}; "
                     f"both with concordant signs: {facts['both_concordant']}.")
            limits = "The q-values were calculated separately within each cohort."
        elif "replication score" in question:
            facts = self.metrics["replication"]
            decision = "met" if facts["decision_met"] else "not met"
            prose = (f"Replication score {facts['target']:.5f}; matched median {facts['matched_median']:.5f}; "
                     f"validation permutation p = {facts['permutation_p']:.4f}. The primary rule was {decision}.")
            limits = "The comparison is relative to the prespecified expression-matched panels."
        elif "ridge" in question and re.search(r"\b(mae|mean absolute error)\b", question):
            facts = self.metrics["prediction"]
            return self.answer(
                f"MAE in years: Ridge {facts['ridge_mae']:.2f}; median age {facts['median_age_mae']:.2f}; "
                f"median matched panel {facts['matched_median_mae']:.2f}.",
                "prediction_validation", facts, ("P7A:prediction",),
                "Five-fold validation within discovery; chronological age only, with no external prediction test.")
        else:
            return None
        return self.answer(prose, "cohort_analysis", facts, ref, limits)

    def citation_answer(self, pmid):
        rows = [r for r in self.rows.values() if r["pmid"] == pmid]
        if not rows:
            return self.answer(
                f"PMID {pmid} is not indexed in the scoped ledger.", "citation_audit",
                {"pmid": pmid, "rows": 0}, ("P5A:scope",),
                "The ledger covers three genes and selected GO processes; it is not a literature search.",
                "insufficient_evidence")
        facts = {"pmid": pmid, "rows": len(rows), "genes": sorted({r["approved_symbol"] for r in rows}),
                 "sources": sorted({r["source"] for r in rows})}
        labels = "; ".join(f"{r['record_id']} ({r['approved_symbol']}"
                           + (f", {r['go_id']})" if r["go_id"] else ")") for r in rows)
        notes = {
            "9454332": " The records cite Bodnar's hTERT culture study for different assertions.",
            "15149599": " Herbig's abstract distinguishes the ATM–p53–p21 pathway from p16 upregulation.",
        }
        return self.answer(f"PMID {pmid}: {labels}." + notes.get(pmid, ""),
                           "citation_audit", facts, (*(r["record_id"] for r in rows), f"PMID:{pmid}"),
                           REUSE_LIMIT)

    def cellage_answer(self, gene, independence):
        rows = self.cellage(gene)
        keys = tuple(r["record_id"] for r in rows)
        pmids = sorted({r["pmid"] for r in rows})
        if independence:
            study = ("Sugrue's p53 restoration in EJ carcinoma cells" if gene == "TP53"
                     else "Kato's p16 protein delivery in cultured fibroblasts")
            return self.answer(
                f"Insufficient evidence for independent trigger tests. The {len(rows)} CellAge rows "
                f"cite {study} (PMID {pmids[0]}).",
                "citation_audit", {"gene": gene, "rows": len(rows), "distinct_pmids": len(pmids),
                                   "independent_trigger_tests_established": False},
                (*keys, f"PMID:{pmids[0]}"), "The paper does not verify a separate assay for each CellAge label.",
                "insufficient_evidence")
        records = [{"record": int(r["cellage_record_number"]), "effect": r["cellage_senescence_effect"],
                    "cancer_cell": r["cellage_cancer_cell"], "type": r["cellage_senescence_type"],
                    "pmid": r["pmid"]} for r in rows]
        labels = "; ".join(f"{r['record']}: {r['effect']}, {r['type']}, cancer cell {r['cancer_cell']}, "
                           f"PMID {r['pmid']}" for r in records)
        return self.answer(f"CellAge Build 3, {gene}: {labels}.", "database_record",
                           {"gene": gene, "records": records}, keys,
                           "Effects and senescence labels are the database's curation; a row is not an independent experiment.")

    def experiment_answer(self, gene):
        row = self.rows[CELLAGE_EXPERIMENT[gene]]
        facts = {key: row[key] for key in ("study_model", "intervention_or_exposure",
                                         "measurements", "reviewed_experimental_result", "review_depth")}
        return self.answer(
            f"{gene} in {facts['study_model']}: {facts['reviewed_experimental_result']}",
            "primary_experiment", facts, (row["record_id"], f"PMID:{row['pmid']}"),
            row["known_limitations"])

    def reviewed_answer(self, question):
        # Narrow, source-specific adjudications. Keep measured negatives separate from missing tests.
        if "human lifespan" in question or "human life span" in question:
            return self.answer(
                "Insufficient evidence for human lifespan extension. The audited experiments use cells or "
                "a specific mouse model, and Phase 7A targets donor chronological age.",
                "scope_assessment", {"human_lifespan_extension_established": False},
                ("P5A:comparison", "P7A:prediction"),
                "The reviewed evidence does not measure survival after manipulating these genes in people.",
                "insufficient_evidence")
        pmid = re.search(r"\bpmid\s*:?\s*(\d+)\b", question)
        if ("recombination" in question and re.search(r"\b(tert|20351177|go:0000722)\b", question)
                and (not pmid or pmid[1] == "20351177")):
            row = self.rows["GAF:27882"]
            return self.answer(
                "Insufficient evidence for the proposed mechanism. The NAS annotation exists, but Egan "
                "and Collins studied telomerase assembly rather than TERT-mediated recombination.",
                "annotation_source_check", {"go_id": row["go_id"], "code": row["evidence_code"],
                                            "mechanism_demonstrated": False},
                ("GAF:27882", "PMID:20351177"), "This check addresses one citation, not all evidence for the mechanism.",
                "insufficient_evidence")
        if re.search(r"\b(kato|9607312)\b", question) and re.search(r"\b(bond|14720514)\b", question):
            return self.answer(
                "Kato delivered p16 protein to early-passage fibroblasts and induced arrest. Bond used "
                "p16 siRNA in late-passage fibroblasts and reported temporary escape from replicative arrest.",
                "primary_experiment", {"distinct_reported_experiments": True,
                                       "kato_intervention": "p16 protein delivery",
                                       "bond_intervention": "p16 siRNA knockdown"},
                ("CellAge:152", "GAF:289848", "PMID:9607312", "PMID:14720514"),
                "These are distinct reported perturbations; sample independence and exact replication were not verified.")
        if ("p14arf" in question and ("mammary" in question or "htert-immortalized" in question)
                and re.search(r"\b(sa[- ]?(?:beta|β)[- ]?gal|galactosidase)\b", question)):
            return self.answer(
                "Shamanin and Androphy reported p53-dependent growth arrest and senescence-like morphology "
                "but no detected SA-β-gal increase in p14ARF-transduced hTERT-immortalized mammary cells.",
                "primary_experiment", {"product": self.rows["GAF:592182"]["db_object_id"],
                                       "arrest_reported": True, "sa_beta_gal_increase_detected": False},
                ("GAF:592182", "PMID:14966292"),
                "A measured negative in this cell model; it does not apply to the other CDKN2A product, p16.")
        if re.search(r"\b(bodnar|9454332)\b", question) and "established senescence" in question:
            return self.answer(
                "Reversal of established senescence was not tested. Bodnar et al. reported delayed "
                "replicative senescence after hTERT transfection in growing cultures.",
                "primary_experiment", {"replicative_senescence_delay_reported": True,
                                       "established_senescence_reversal_tested": False},
                ("CellAge:845", "PMID:9454332"),
                "The comparison measured culture proliferation, not recovery from stable arrest.", "not_measured")
        if re.search(r"\b(ghosh|29474172)\b", question) and "survival" in question:
            return self.answer(
                "Reducing Trp53 dosage increased survival in Sirt6-null mice compared with Sirt6-null controls.",
                "primary_experiment", {"organism": "mouse", "background": "Sirt6-null",
                                       "survival_direction": "increased"},
                ("GAF:133834", "PMID:29474172"),
                "This result is specific to a short-lived mouse genotype; the GO target is human.")
        return None

    def ask(self, question):
        q = " ".join(question.casefold().split())
        # A compound or unrecognized request must not receive a partial answer as though complete.
        if "?" not in q.rstrip("?") and ";" not in q:
            terms = set(re.findall(r"[a-z0-9]+", q))
            genes = [symbol for symbol in self.overlap if symbol.casefold() in terms
                     or self.overlap[symbol]["entrez_gene_id"] in terms]
            # A PMID lookup treats the publication as a citation, never as proof of a claim.
            pmid = re.search(r"\bpmid\s*:?\s*(\d+)\b", q)
            if pmid and re.search(r"\b(cited|reuse|reused|references)\b", q):
                return self.citation_answer(pmid[1])
            if (answer := self.reviewed_answer(q)) is not None:
                return answer
            gene = genes[0] if len(genes) == 1 else None
            if gene in CELLAGE_EXPERIMENT and re.fullmatch(r"experiment [a-z0-9]+", q):
                return self.experiment_answer(gene)
            if gene and gene not in AUDITED.values() and "manual audit" in q:
                return self.answer(
                    f"Insufficient evidence in this audit for a causal senescence effect of {gene}. "
                    "Shared database membership is confirmed.",
                    "scope_assessment", {"gene": gene, "manual_review_in_scope": False},
                    ("P5A:scope", f"P3:gene:{self.overlap[gene]['entrez_gene_id']}"),
                    "Only TP53, CDKN2A and TERT received this manual evidence review.",
                    "insufficient_evidence")
            if gene in AUDITED.values() and "cellage" in q:
                independent = bool(re.search(r"\bindependent (?:senescence )?trigger\b", q))
                if independent and gene in {"TP53", "CDKN2A"}:
                    return self.cellage_answer(gene, independence=True)
                if not independent and re.search(r"\b(which|list)\b.*\brecords?\b", q):
                    return self.cellage_answer(gene, independence=False)
            if len(genes) <= 1 and (answer := self.association_answer(q, gene)) is not None:
                return answer
        return self.answer(
            "This question is outside the supported lookup forms. No biological conclusion was drawn.",
            "scope_assessment", {}, ("P5A:scope", "P7A:association"),
            "The interface supports narrow English queries over pinned sources and cannot search the literature.",
            "unsupported_question")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="one narrow English research question")
    args = parser.parse_args()
    print(json.dumps(Evidence().ask(args.question), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
