# Phase 8A B01 prior-art citation support

## Investigation

The frozen B01 retrieval included the prior-art paragraph `V2-L15-L15`, the summary `V2-L7-L7`, the GO paragraph `V2-L17-L17` and the RNA-seq paragraph `P7A-L7-L7`. The model broadly rejected novelty of the count but selected only the first-ranked GO paragraph. That paragraph supports direct GO annotations for the shared genes. It says nothing about Bonnefous, previous publication or gene-list equivalence. The schema and citation validator checked ID membership, so the answer was accepted. The evidence was available in the context. Ranking and source selection made the support failure possible. [Frozen B01 audit](phase8a_release_readiness.md#b01--overlap-and-prior-publication) · [Prior-art paragraph](../reports/research_report_v2.md?plain=1#L15) · [GO paragraph](../reports/research_report_v2.md?plain=1#L17)

The project reproduced the intersection count of 113 confirmed human genes from 307 GenAge Human Build 21 and 865 CellAge Build 3 genes. Bonnefous et al. (2024) had reported 113 from 303 and 852 exploitable genes under different eligibility rules. The reviewed supplements did not provide comparable gene lists. Count agreement leaves gene-by-gene equivalence unverified. The project's contribution is the reproducible workflow, including pinned source handling, identifier harmonization, traceability and evidence analysis. [Project intersection](../reports/research_report_v2.md?plain=1#L11) · [Prior-art comparison](../docs/related_work.md#bonnefous-et-al-2024) · [Contribution and limits](../docs/related_work.md#contribution-and-limits)

## Frozen regression cases

These questions and expectations were fixed before the baseline and candidate runs.

| ID | Exact question | Expected support and boundaries |
| --- | --- | --- |
| A | Можно ли считать 113 совпавших генов новым результатом по сравнению с работой Bonnefous? | Reject novelty of the count. Cite the previous publication and the reproduced count. Keep membership equivalence unverified. |
| B | Сообщалось ли раньше о пересечении GenAge и CellAge в 113 генов? | State that Bonnefous et al. (2024) reported 113 before. Cite prior-art evidence. Do not claim identical lists. |
| C | Нашёл ли наш проект 113 ранее неизвестных генов старения? | Reject the premise. The result is an intersection of existing curated resources and a reproduced count. Cite the count and prior report. |
| D | Does the same 113-gene count in our overlap and Bonnefous et al. prove that the gene lists are identical? | Explain why equal counts do not establish identical membership. Cite the differing eligibility and unavailable comparable lists. |
| E | How did the GenAge and CellAge eligibility rules used by Bonnefous et al. differ from ours? | Distinguish their protein and orthology requirements from reciprocal human NCBI Gene ID and HGNC criteria. Give the denominators with both datasets correctly labeled. Cite the detailed eligibility and count passages. |
| F | В чём вклад нашего проекта по GenAge и CellAge помимо уже опубликованного числа 113? | Describe reproducible source handling, identifier harmonization, provenance and evidence analysis. Cite the contribution and prior-art evidence. |
| G | Was the 113-gene GenAge–CellAge overlap count a new finding or a reproduction of prior work? | Identify reproduction of a previously published count with a supporting citation. Do not assert membership equivalence. |
| H | Did all 113 shared genes retain a direct positive GO Biological Process annotation after excluding IEA? | Answer yes for the tracked analysis and cite `V2-L17-L17` or equivalent GO evidence. Do not use prior-art evidence alone. |
| I | Was the Phase 7A discovery partial correlation for CDKN2A a measured value near zero? | Preserve the B06 lookup and exact measured coefficient −0.001464046161 with the frozen CSV row. |
| J | What temperature should I use to bake sourdough bread? | Abstain before inference with no research source. |

## Evidence-presentation trial and correction

The trial replaced the retrieved excerpts for A–G with the exact contiguous overlap and prior-art paragraphs (V2 lines 11–15). E and F used the exact detailed methods or contribution paragraph as primary evidence and the overlap range as supporting evidence. The trial used the original prompts and real model. It improved citation selection in several cases, including A, D and G. C still claimed novel genes and E reversed the documented CellAge exclusion despite citing the right methods paragraph. Ranking or presentation alone therefore did not provide a defensible correction on the frozen regressions.

The implementation uses a narrow deterministic response for explicit questions about prior publication, novelty, list equivalence, eligibility rules or project contribution in the context of the overlap. It reads the exact reviewed passages from the frozen project reports and related-work document. The response separates the reproduced count from unverified membership and adds the eligibility or contribution details only when asked. GO questions and the other study routes retain their existing behavior. The ranking, prompts and generic citation validator stay unchanged. The guard does not cover every paraphrase or validate scientific claims elsewhere.

## Live regression on 2026-11-09

The baseline, presentation trial and corrected app ran through Streamlit AppTest with the real local Ollama 0.40.15 API and `qwen3:1.7b` (model ID `8f68893c685c`), with cloud disabled. The observer forwarded requests without replacing model responses. The baseline and trial made eight inference calls each (A–H). The final run made one inference call for H, used the prior-art response for A–G and the existing B06 lookup for I, and abstained before inference for J. The exact displayed text and passage IDs follow.

### A

**Baseline model output.** Status `answered`. Retrieved `V2-L17-L17`, `V2-L7-L7`, `V2-L15-L15`, `P7A-L7-L7`. Selected `V2-L17-L17`.

> Нет, 113 совпавших генов не является новым результатом по сравнению с работой Bonnefous. Это результат наблюдения, который был подтверждён в рамках исследования GenAge–CellAge, и не является новым выводом из отдельной работы Bonnefous.

**Presentation trial model output.** Status `answered`. Retrieved `V2-L11-L15`. Selected `V2-L11-L15`.

> Нет, 113 совпавших генов не является новым результатом по сравнению с работой Bonnefous. Это количество генов, совпадающих между GenAge и CellAge, было указано в исходном отрывке, но не является новым выводом или сравнением с работой Bonnefous.

**Deterministic response.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`. Selected `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`.

> Проект воспроизвёл опубликованное ранее число пересечения. Среди 307 генов GenAge Human Build 21 и 865 генов CellAge Build 3 нашли 113 общих подтверждённых человеческих генов. Bonnefous et al. (2024) уже сообщали о 113, используя 303 гена GenAge и 852 гена CellAge, прошедших другой отбор. Открытие ранее неизвестных генов этими данными не установлено. В доступных приложениях нет сопоставимых списков, поэтому совпадение списков по отдельным генам не подтверждено.

The baseline cited the GO paragraph for a prior-publication claim. The trial cited a passage containing the two relevant paragraphs but gave a muddled account of what Bonnefous reported. The final response identifies both counts and the membership limit with exact source cards.

### B

**Baseline model output.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L7-L7`, `V2-L15-L15`, `V2-L17-L17`. Selected `V2-L11-L11`.

> Да, сообщалось о пересечении GenAge и CellAge в 113 генах, как указано в первом отрывке.

**Presentation trial model output.** Status `answered`. Retrieved `V2-L11-L15`. Selected `V2-L11-L15`.

> Да, сообщалось о пересечении GenAge и CellAge в 113 генах.

**Deterministic response.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`. Selected `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`.

> Проект воспроизвёл опубликованное ранее число пересечения. Среди 307 генов GenAge Human Build 21 и 865 генов CellAge Build 3 нашли 113 общих подтверждённых человеческих генов. Bonnefous et al. (2024) уже сообщали о 113, используя 303 гена GenAge и 852 гена CellAge, прошедших другой отбор. Открытие ранее неизвестных генов этими данными не установлено. В доступных приложениях нет сопоставимых списков, поэтому совпадение списков по отдельным генам не подтверждено.

The baseline cited the project count without the earlier publication. The trial selected the right range but omitted the study attribution. The final answer names Bonnefous et al. (2024) and cites the prior-art record.

### C

**Baseline model output.** Status `answered`. Retrieved `V2-L11-L11`, `P7A-L7-L7`, `V2-L17-L17`, `V2-L21-L21`. Selected `V2-L11-L11`.

> Да, проект нашёл 113 ранее неизвестных генов старения, которые находились в пересечении GenAge и CellAge данных.

**Presentation trial model output.** Status `answered`. Retrieved `V2-L11-L15`. Selected `V2-L11-L15`.

> Да, проект нашёл 113 ранее неизвестных генов старения. Измеренный результат - 113 генов. Предел вывода - повреждение ДНК и сенесценция.

**Deterministic response.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`. Selected `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`.

> Проект воспроизвёл опубликованное ранее число пересечения. Среди 307 генов GenAge Human Build 21 и 865 генов CellAge Build 3 нашли 113 общих подтверждённых человеческих генов. Bonnefous et al. (2024) уже сообщали о 113, используя 303 гена GenAge и 852 гена CellAge, прошедших другой отбор. Открытие ранее неизвестных генов этими данными не установлено. В доступных приложениях нет сопоставимых списков, поэтому совпадение списков по отдельным генам не подтверждено.

Both the baseline and the trial called the genes previously unknown. The trial also introduced unrelated DNA-damage and senescence wording. The final response rejects the novelty premise and identifies a reproduced count from existing curated resources.

### D

**Baseline model output.** Status `answered`. Retrieved `V2-L15-L15`, `V2-L11-L11`, `V2-L17-L17`, `V2-L7-L7`. Selected `V2-L11-L11`.

> No, the 113-gene count in the overlap does not prove that the gene lists are identical. The gene lists differ in eligibility criteria and verification methods, as noted in the study.

**Presentation trial model output.** Status `answered`. Retrieved `V2-L11-L15`. Selected `V2-L11-L15`.

> No, the 113-gene count in our overlap does not prove that the gene lists are identical. The study notes that Bonnefous et al. reported the same count in an evolutionary network analysis, but their gene eligibility rules differ from our criteria. Additionally, the available supplements lack the gene lists needed to verify membership equivalence.

**Deterministic response.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`. Selected `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`.

> The project reproduced a previously published count. The intersection of 307 GenAge Human Build 21 genes and 865 CellAge Build 3 genes contained 113 confirmed human genes. Bonnefous et al. (2024) already reported 113 from 303 exploitable GenAge and 852 exploitable CellAge genes under different eligibility rules. These results do not establish the discovery of previously unknown genes. The reviewed supplements lack comparable lists, so gene-by-gene membership equivalence remains unverified.

The baseline correctly rejected proof of identical membership but cited only the project's intersection. The trial and final response explain the different eligibility and missing gene lists with supporting passages.

### E

**Baseline model output.** Status `answered`. Retrieved `V2-L15-L15`, `P7A-L21-L21`, `P7A-L34-L34`, `V2-L23-L23`. Selected `V2-L23-L23`.

> The GenAge and CellAge eligibility rules used by Bonnefous et al. differ from ours in that their protein and orthology eligibility differs from our gene identifier rules. Our rules are based on gene identifiers, while theirs use different protein and orthology criteria.

**Presentation trial model output.** Status `answered`. Retrieved `RW-L19-L19`, `V2-L11-L15`. Selected `RW-L19-L19`.

> Bonnefous et al. used different eligibility rules compared to ours. They required protein-coding gene identifiers mapped to OMA orthogroups and applied a low-sequence-complexity filter, while we use confirmed current human NCBI Gene IDs with reciprocal HGNC mappings without requiring protein-network or orthology matches. Additionally, they excluded one conflicting CellAge record, whereas we excluded none.

**Deterministic response.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`, `RW-L19-L19`. Selected `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`, `RW-L19-L19`.

> The project reproduced a previously published count. The intersection of 307 GenAge Human Build 21 genes and 865 CellAge Build 3 genes contained 113 confirmed human genes. Bonnefous et al. (2024) already reported 113 from 303 exploitable GenAge and 852 exploitable CellAge genes under different eligibility rules. These results do not establish the discovery of previously unknown genes. The reviewed supplements lack comparable lists, so gene-by-gene membership equivalence remains unverified. Bonnefous et al. mapped protein-coding genes to STRING through Entrez and Ensembl. Their evolutionary analysis required an OMA orthogroup of known origin and applied a low-sequence-complexity filter. This project required current human NCBI Gene IDs and reciprocal HGNC agreement.

The baseline cited RNA-seq results for eligibility. The trial used the correct methods paragraph but reversed which project excluded a conflicting CellAge record and omitted the counts. The final response distinguishes the two sets of rules and reports both denominators with sources.

### F

**Baseline model output.** Status `answered`. Retrieved `V2-L76-L76`, `V2-L11-L11`, `V2-L17-L17`, `V2-L7-L7`. Selected `V2-L17-L17`.

> Вклад проекта по GenAge и CellAge помимо уже опубликованного числа 113 включает в себя анализ генов с использованием методов ридж-регрессии, проверку достоверности аннотаций через аудит, и создание инструментов для анализа данных, таких как терминологическая нормализация и оптимизация поиска. Также проект предоставляет возможность проверки источников и подтверждения заявлений через аудит.

**Presentation trial model output.** Status `answered`. Retrieved `RW-L38-L38`, `V2-L11-L15`. Selected `RW-L38-L38`.

> Вклад нашего проекта по GenAge и CellAge включает в себя реализацию traceable workflow для identified snapshots, проверку SHA-256 checksums, запись reciprocal NCBI–HGNC решений и явных исключений, а также сохранение CellAge ordinals для каждого совпадающего гена. Также вклад включает анализ GO таблиц и выявление повторяющихся цитат и аннотаций, не подтверждающих указанное биологическое действие.

**Deterministic response.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`, `RW-L38-L38`. Selected `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`, `RW-L38-L38`.

> Проект воспроизвёл опубликованное ранее число пересечения. Среди 307 генов GenAge Human Build 21 и 865 генов CellAge Build 3 нашли 113 общих подтверждённых человеческих генов. Bonnefous et al. (2024) уже сообщали о 113, используя 303 гена GenAge и 852 гена CellAge, прошедших другой отбор. Открытие ранее неизвестных генов этими данными не установлено. В доступных приложениях нет сопоставимых списков, поэтому совпадение списков по отдельным генам не подтверждено. Вклад проекта — воспроизводимая работа с закреплёнными снимками. Мы проверяем SHA-256, согласуем идентификаторы NCBI и HGNC, документируем исключения и сохраняем номера исходных записей CellAge. Анализ прослеживает аннотации и научные утверждения до их источников.

The baseline gave unrelated details from elsewhere in the project while citing GO. The trial improved source selection and described workflow details, with mixed-language wording. The final response describes pinned sources, harmonization, provenance and evidence analysis, supported by the contribution paragraph.

### G

**Baseline model output.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L7-L7`, `V2-L15-L15`, `V2-L17-L17`. Selected `V2-L11-L11`.

> The 113-gene GenAge–CellAge overlap count was a reproduction of prior work, as it was reported in the primary excerpt and matched a previously published count.

**Presentation trial model output.** Status `answered`. Retrieved `V2-L11-L15`. Selected `V2-L11-L15`.

> The 113-gene GenAge–CellAge overlap count was a reproduction of prior work, as it was reported by Bonnefous et al. in an evolutionary network analysis.

**Deterministic response.** Status `answered`. Retrieved `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`. Selected `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13`.

> The project reproduced a previously published count. The intersection of 307 GenAge Human Build 21 genes and 865 CellAge Build 3 genes contained 113 confirmed human genes. Bonnefous et al. (2024) already reported 113 from 303 exploitable GenAge and 852 exploitable CellAge genes under different eligibility rules. These results do not establish the discovery of previously unknown genes. The reviewed supplements lack comparable lists, so gene-by-gene membership equivalence remains unverified.

The baseline called the result a reproduction but cited the project's current count alone. The trial and final response link the claim to prior art. The final response also gives the membership boundary.

### H

**All runs.** Status `answered`. Retrieved `V2-L17-L17`, `GENES-L5-L5`, `P7D-L5-L5`, `GENES-L68-L68`. Selected `V2-L17-L17`.

> Yes, all 113 shared genes retained a direct, positive GO Biological Process annotation after excluding IEA.

All three runs correctly described the direct positive GO annotation result after excluding IEA and selected the GO paragraph. The final app still calls Ollama for this question.

### I

**All runs.** Status `answered`. Retrieved `P7A-CSV-L15-L15`, `P7A-L17-L17`. Selected `P7A-CSV-L15-L15`, `P7A-L17-L17`.

> CDKN2A, Phase 7A. Fibroblast expression and donor chronological age. Discovery cohort. r = -0.001464046161. Validation cohort. r = -0.1722628565.

All three runs preserve the measured CDKN2A discovery coefficient at stored precision through the B06 lookup, with the frozen CSV row.

### J

**All runs.** Status `insufficient_evidence`. Retrieved None. Selected None.

> No matching passages in the project reports. Try naming the gene, study or outcome.

All three runs abstained before calling Ollama and selected no sources.

## Frozen 20-case replay

The original questions, order and follow-up context were preserved. B01 changed to the deterministic response shown under A. The other 19 cases matched the post-B09 replay in displayed answer, app status, retrieved passages and selected citations. The replay made 14 real inference calls, four deterministic replies (A03, B01, B06 and B09), and two pre-inference abstentions. The earlier reports contain the exact outputs and detailed source reviews for the unchanged cases. [Post-B09 scientific review](phase8a_b09_panel_eligibility.md#frozen-20-case-replay) · [Historical release audit](phase8a_release_readiness.md)

| Case | Review | Selected source IDs | Scientific assessment |
| --- | --- | --- | --- |
| A01 | Minor | `GENES-L31-L31` | Supported p53 restoration and arrest in EJ cells. Separate CellAge trigger boundary omitted. |
| A02 | Minor | `GENES-L51-L51` | Correctly distinguishes delay from reversal in culture. Quantitative doubling detail omitted. |
| A03 | Pass | `P7A-CSV-L103-L103`, `P7A-L17-L17` | Both cohorts failed the expression filter. CSV line and original report paragraph support the explanation. |
| A04 | Minor | `P7D-L16-L16` | Supported FOXO3 knockdown effects in fibroblasts. Stable arrest and activation limits omitted. |
| A05 | Minor | `P7D-L18-L18` | Correct association direction and odds ratio in Japanese American men. Confidence interval omitted. |
| A06 | Minor | `P7D-L22-L22` | Correctly rejects proof of replicative senescence. Specific marker and serial-passage details omitted. |
| A07 | Minor | `P7D-L28-L28` | Reports mouse survival and qualifies the female result. Male group and wild-type comparator not explicit. |
| A08 | Pass | `P7D-L26-L26` | Correctly separates the SIRT6 genotype association from a human intervention. |
| A09 | Minor | `GENES-L57-L57` | Declines a human survival inference. The culture characterization is more specific than the selected source. |
| A10 | Pass | None | Appropriate out-of-scope abstention before inference. |
| B01 | Pass | `V2-L11-L11`, `V2-L15-L15`, `RW-L5-L13` | Published sources support the repeated count, different eligibility and unverified membership. No novelty claim. |
| B02 | Minor | `V2-L23-L23` | Correct comparison direction. Cross-cohort scope and numeric results omitted. |
| B03 | Critical | `P7D-L16-L16` | The cited fibroblast passage does not support the human side of the FOXO3 comparison. |
| B04 | Critical | `P7D-L16-L16` | Declines a human lifespan inference but gives a misleading account of the cell intervention and lacks support for the genotype claim. |
| B05 | Critical | `P7D-L22-L22` | The cited chondrocyte paragraph does not support the mouse-survival claim. |
| B06 | Pass | `P7A-CSV-L103-L103`, `P7A-L17-L17` | Rejects zero and reports both unestimated coefficients with the expression-filter reason and supporting citations. |
| B07 | Pass | None | Appropriately abstains from estimating human lifespan gained by treatment. |
| B08 | Minor | `P7D-L26-L26` | Conveys the observational boundary, with an unnecessary Phase 7A claim and no genotype-specific direction. |
| B09 | Pass | `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34` | The baseline confused the two denominators and assigned the matching variables to the outcome. The corrected answer gives both counts, names the donor-age endpoint and distinguishes the separate cohort fits, their covariates and matching. The cited methods, result and interpretation passages support those claims. |
| B10 | Pass | None | Appropriate out-of-scope abstention before inference. |

The replay had **8 Pass, 9 Minor and 3 Critical**, compared with **7 Pass, 9 Minor and 4 Critical** after B09. The B06 missingness and near-zero controls passed, and B09 kept its separate eligibility and sign counts, chronological-age endpoint and matching explanation.

The stable release remains **NOT READY**. B03 and B04 still lack adequate citation support for the human-genotype evidence in the FOXO3 comparison and follow-up. B05 still cites only the cellular experiment for a comparison that includes mouse survival. Scientific interpretation and citation support remain unverified for general model output.

## Automated and source checks

`python3 -B -m unittest discover -s tests -v` discovered 82 tests and skipped three Streamlit tests in the base interpreter. All 82 passed in the UI environment, and all eight Phase 7 tests passed in the Phase 7 environment. `git diff --check` passed. GitHub's plain-code view of the frozen related-work document confirmed lines 5–13, 19 and 38. The historical audit, related-work document, scientific reports, data and frozen benchmarks were preserved.
