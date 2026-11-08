# Phase 8A local chat evaluation

Phase 8A is an engineering prototype built on the v2.0.0 research release. The [lexical retriever](../scripts/local_retrieval.py) searches five tracked reports, including their reviewed evidence-record summaries. It sends up to four passages, with a total excerpt budget of 3,600 characters. Source cards link to the immutable v2.0.0 commit and use report and line identifiers. Markdown link labels are kept in the excerpt so the prompt does not carry the link destinations.

The [chat module](../scripts/local_ai.py) talks to Ollama on `127.0.0.1:11434`. It requests `qwen3:1.7b` with thinking disabled, a 4,096-token context, up to 384 output tokens, temperature 0.1 and a 90-second socket timeout for generation. The model may use up to two preceding user questions of 400 characters each to resolve a follow-up. Generated replies never enter the prompt as evidence.

## Run the manual evaluation

Install the macOS Ollama app and run the [local server and model commands](../README.md#local-ai--experimental). From the repository root, start the UI in another terminal.

```sh
python3 -m venv .venv/ui
.venv/ui/bin/python -m pip install -r requirements-ui.txt
.venv/ui/bin/python -m streamlit run web_ui/app.py
```

At [http://127.0.0.1:8501](http://127.0.0.1:8501), select **Local AI — Experimental** and check that the model is available. Clear the conversation before each case except case 5, which follows case 4 in the same session. Submit the prompts as written, and use **Retrieved evidence** to check the support for each generated claim.

| Case | Prompt | Expected facts and boundaries |
| --- | --- | --- |
| 1 · TP53 | What happened when researchers restored p53 in EJ carcinoma cells? | Wild-type p53 restoration in human EJ bladder carcinoma cells caused durable growth arrest and senescence markers. The three CellAge labels do not establish three independently tested triggers. [TP53 case study](../reports/gene_case_studies.md#tp53--a-damage-responsive-transcription-factor) |
| 2 · TERT culture | Did hTERT expression delay replicative senescence or reverse established arrest? | Telomerase-active clones grew past negative controls, with at least 20 additional population doublings reported. The experiment followed proliferating human cultures and did not test reversal of established arrest. [TERT case study](../reports/gene_case_studies.md#tert--the-catalytic-subunit-of-telomerase) |
| 3 · TERT RNA-seq | Why are the Phase 7A partial correlations for TERT missing? | TERT failed the expression filter in both cohorts. No partial correlation was estimated in either cohort. [Phase 7A association analysis](../reports/phase7_baseline_results.md#independent-association-analysis) |
| 4 · FOXO3 | What happened when FOXO3 was knocked down in human dermal fibroblasts? | Stable siRNA knockdown was associated with slower doubling and senescence-associated changes such as increased SA-β-gal. The reviewed abstract does not resolve stable arrest or the effect of FOXO3 activation. [FOXO3 case study](../reports/phase7d_case_studies.md#foxo3) |
| 5 · Follow-up to case 4 | And what did they find about human longevity? | For rs2802292 in Japanese American men, GG versus TT was associated with long-lived case status (OR 2.75, 95% CI 1.51–5.02). This was a genotype association. The study did not alter FOXO3 expression. [FOXO3 case study](../reports/phase7d_case_studies.md#foxo3) |
| 6 · SIRT6 in Russian | Доказывает ли нокдаун SIRT6 в хондроцитах репликативное старение? | Ответ на русском. Нокдаун в культивируемых хондроцитах человека увеличивал долю SA-β-gal-положительных клеток и снижал пролиферацию. Проверенные источники не установили исчерпание пролиферации после серии пассажей или сохранение ареста после прекращения воздействия. [SIRT6 case study](../reports/phase7d_case_studies.md#sirt6) |
| 7 · SIRT6 in mice | Did overexpressing SIRT6 extend lifespan in mice? | Sirt6 overexpression extended lifespan in male transgenic mice in the Kanfi study. No significant extension was reported in females in that experiment. The evidence is specific to that model. [SIRT6 case study](../reports/phase7d_case_studies.md#sirt6) |
| 8 · SIRT6 in humans | Does GAF 591445 show that intervening on SIRT6 increases human lifespan? | TenNapel compared naturally occurring rs107251 genotypes and measured age at death. The study did not intervene on SIRT6 or demonstrate a causal lifespan effect. [SIRT6 case study](../reports/phase7d_case_studies.md#sirt6) |
| 9 · Unsupported inference | Does TERT help people live longer? | Abstain from concluding that a TERT intervention extends human lifespan. The supplied work describes cell-culture outcomes or observational markers. [TERT case study](../reports/gene_case_studies.md#tert--the-catalytic-subunit-of-telomerase) |
| 10 · Out of scope | How do I bake sourdough bread? | The retriever finds no relevant passage. The UI reports insufficient evidence without running inference. |

For each case, record the model tag and ID from `ollama list`, the retrieved and cited IDs, the displayed answer or warning, and approximate response time. Mark omitted expected facts, unsupported claims, citations that fail to support the sentence, citation warnings, and any failure to abstain. A source ID can be valid even when the cited passage does not support the claim.

## Run record

Ollama and its API were unavailable on the development machine. Live model accuracy, unsupported-claim frequency, citation accuracy and response time remain unmeasured. The automated tests exercise retrieval, request settings, transport failures, citation validation and Streamlit behavior with mocks.

The corpus is limited to selected project reports and their scope. Lexical matching can miss paraphrases and vocabulary outside the indexed text. The Russian retrieval vocabulary covers a small set of common terms. The prototype checks whether citation IDs were supplied to the model. Scientific interpretation still requires reading the cited sources and checking the study design, endpoint and population.
