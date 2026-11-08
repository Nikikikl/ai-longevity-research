# Phase 8A local chat evaluation

Phase 8A is an engineering prototype built on the v2.0.0 research release. The [lexical retriever](../scripts/local_retrieval.py) searches five tracked reports, including their reviewed evidence-record summaries. It sends up to four passages, with a total excerpt budget of 3,600 characters. Source cards link to the immutable v2.0.0 commit and use report and line identifiers. Markdown link labels are kept in the excerpt so the prompt does not carry the link destinations.

The chat module talks to Ollama on `127.0.0.1:11434`. It requests `qwen3:1.7b` with thinking disabled, a 4,096-token context, up to 384 output tokens, temperature 0 and a 90-second socket timeout for generation. The model may use up to two preceding user questions of 400 characters each to resolve a follow-up. The prompt identifies the highest-ranked excerpt and includes the other retrieved passages as context. [Chat module](../scripts/local_ai.py)

The response schema requires `status`, `answer` and `source_ids`. The schema limits IDs to the excerpts supplied for that question. Python independently validates the IDs and builds the source cards. An answered response requires a source. The app tries one correction with a 30-second socket timeout after invalid model output. It keeps the same excerpts and discards the invalid reply.

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

For each case, record the model tag and ID from `ollama list`, the retrieved and cited IDs, the displayed answer or warning, and approximate response time. Mark omitted expected facts, unsupported claims, citations that fail to support a claim, citation warnings, and any failure to abstain. A source ID can be valid even when the cited passage does not support the claim.

## Run record

### Live integration check, 2026-11-09

Ollama 0.40.15 served `qwen3:1.7b` (model ID `8f68893c685c`). Before the fix, both reported failures returned complete JSON with status `answered`. The SIRT6 answer had no passage ID. The TERT answer contained the correct ID `P7A-L17-L17` without square brackets. The previous schema constrained the response fields but left citation formatting inside the answer string. The validator rejected both replies.

The final run submitted each question in a fresh conversation through Streamlit's AppTest adapter using the real local API. All four responses completed on the first attempt in this run. The retrieved excerpts were available in each case.

| Question | Result and source IDs | Manual review |
| --- | --- | --- |
| SIRT6 knockdown and replicative senescence (case 6) | `answered`, `P7D-L22-L22` | Correctly answered in Russian that the experiment did not establish replicative senescence and mentioned increased SA-β-gal and other markers. It omitted reduced proliferation and the specific gap in the serial-passage design. |
| Missing TERT partial correlations (case 3) | `answered`, `P7A-L17-L17` | Correctly attributed the missing correlations to the expression filter in both cohorts. |
| FOXO3 knockdown in dermal fibroblasts (case 4) | `answered`, `P7D-L16-L16` | Correctly reported longer doubling times and changes in senescence-associated markers. It limited the interpretation to the culture model. |
| How many years does TERT gene therapy add to the human lifespan? | `insufficient_evidence`, no cited IDs | Correctly abstained without reporting a lifespan effect. |

Earlier structured-output prompt variants produced valid IDs alongside a claim that SIRT6 knockdown proved replicative senescence and an explanation that confused missing TERT expression correlations with human lifespan. These errors informed the final prompt and illustrate why ID validation alone cannot establish scientific support. This four-question check measures behavior on these prompts only. Automated tests separately exercise retrieval, request settings, transport failures, invalid IDs, correction limits and Streamlit behavior with mocks.

### Multilingual retrieval check, 2026-11-09

The earlier retriever found only one matching term, `113`, in “что за результат в 113 генов мы нашли”. The Russian words for genes and findings did not match the English reports, and the non-gene-symbol path required two matching terms. The short FOXO3 question matched the symbol and ranked a detailed knockdown passage ahead of the consolidated evidence summary.

The revised retriever normalizes common Russian inflections and English synonyms. Broad wording about 113 genes favors the consolidated comparison and prior art. Specific terms such as RNA-seq and panel keep a question focused on the association analysis. Broad gene questions favor a named synopsis when the reports provide one. Generic terms alone are insufficient unless the question asks for the project summary.

Both runs used the Streamlit AppTest adapter with a fresh conversation for each question and the real Ollama 0.40.15 API. The model was `qwen3:1.7b` (ID `8f68893c685c`). Source IDs below are the model's selections. The application did not add citations.

| Question | Before | After and manual review |
| --- | --- | --- |
| что за результат в 113 генов мы нашли | No passages; abstained. | `V2-L7-L7`. Correctly identified the shared count and said that it agreed with a previously published count. |
| Что означает пересечение GenAge и CellAge? | Cited extension audit and case-study passages. Gave a vague account without the count. | `V2-L11-L11`. Correctly gave 113 shared genes out of sets of 307 and 865. It overstated what the overlap shows about source compatibility. |
| What did the 113 shared genes tell us? | `V2-L11-L11`. Introduced a GO annotation claim that the cited passage did not support. | `V2-L11-L11`. Correctly described the overlap and left its functional significance open. It omitted the prior publication, although that evidence was retrieved. |
| Какие главные результаты нашего исследования? | No passages; abstained. | `V2-L7-L7`. Included the overlap and the panel comparison, but overstated the negative finding as an absence of statistically significant results overall. |
| суть гена foxo3 | `P7D-L16-L16`. Described the cell experiment alone. | `V2-L52-L52`. Retrieved the culture and genotype studies as well (`P7D-L16-L16` and `P7D-L18-L18`). The answer mentioned both lines of evidence but did not name the transcription-factor function, overgeneralized regulation of senescence and imprecisely described the Japanese American cohort. |
| Why are TERT's Phase 7A correlations missing? | `P7A-L17-L17`. Correct expression-filter explanation. | Same source and correct explanation. |
| Что показал нокдаун SIRT6 в хондроцитах? | `P7D-L22-L22`. Reported the marker changes and reduced proliferation using several mistranslated terms. | Same source. Kept the marker name and used clearer Russian for DNA damage and reduced proliferation. The answer omitted p16 and expressed the limitation too broadly. The separate question about proof of replicative senescence correctly rejected that conclusion. |
| пока | No passages; abstained without inference. | Same. |
| How many years does TERT gene therapy add to the human lifespan? | `insufficient_evidence`, no cited IDs. | Same. The model did not estimate a lifespan effect. |

The corpus is limited to selected project reports and their scope. Lexical matching can miss paraphrases and vocabulary outside the indexed text. The Russian retrieval vocabulary covers a small set of common terms. The prototype checks whether citation IDs were supplied to the model. Scientific interpretation still requires reading the cited sources and checking the study design, endpoint and population.
