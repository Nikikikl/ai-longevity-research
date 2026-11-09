# Phase 8A multi-study evidence reliability

## Investigation

B03 and B04 retrieved the FOXO3 culture and human genotype passages. B05 retrieved the human chondrocyte and mouse survival passages. The selected citations covered only the cell experiment in all three baseline answers. B03 omitted the human association, B04 gave a misleading account of the cell intervention, and B05 stated the female result more categorically than the cited mouse study supports. The model's citation IDs were valid. They did not support all central claims. The earlier prompt trial also left these cases critical. The shared failure was incomplete use of available evidence combined with errors in synthesis. Adding an ID alone would not repair the prose. [Historical audit](phase8a_release_readiness.md) · [Post-B01 baseline](phase8a_b01_prior_art_citation.md#frozen-20-case-replay)

The study pairs and boundaries are fixed by the reviewed evidence. FOXO3 knockdown in human dermal fibroblasts increased senescence-associated markers and slowed population doubling. The separate Japanese American case-control study associated rs2802292 with exceptional longevity in men and did not alter expression. Neither shows that changing expression extends human lifespan. SIRT6 depletion in human knee chondrocytes altered cellular markers and reduced proliferation. Sirt6 overexpression in transgenic mice extended lifespan in males, with no significant extension in females. The intervention, model and endpoint differ. [FOXO3 culture](../reports/phase7d_case_studies.md?plain=1#L16) · [FOXO3 human association](../reports/phase7d_case_studies.md?plain=1#L18) · [SIRT6 culture](../reports/phase7d_case_studies.md?plain=1#L22) · [SIRT6 mouse survival](../reports/phase7d_case_studies.md?plain=1#L28)

## Frozen regression and holdout cases

The questions and expected outcomes were written before implementation. B04 follows B03. H02 follows H01. All other questions start a fresh conversation. The holdout is first evaluated after the correction and is not used to tune it.

| ID | Exact question | Expected evidence and boundary |
| --- | --- | --- |
| B03 | Какой вывод о FOXO3 позволяет сделать опыт с фибробластами, а какой — данные по генотипам людей? | Separate knockdown and cellular changes from the observational human genotype association. Cite `P7D-L16-L16` and `P7D-L18-L18`. |
| B04 | А можно ли по этим данным сказать, что изменение экспрессии этого гена продлит жизнь человеку? | Resolve FOXO3 from the preceding turn and reject a human lifespan conclusion. Cite both study designs. |
| B05 | How do the SIRT6 findings in human knee chondrocytes differ from the survival findings in Sirt6-overexpressing mice? | Separate cellular depletion from mouse overexpression and survival. Report the sex-specific result and cite `P7D-L22-L22` and `P7D-L28-L28`. |
| R01 | What did FOXO3 knockdown show in fibroblasts compared with the human genotype evidence? | Cover both studies, their outcomes and distinct designs. Cite both. |
| R02 | Чем отличается опыт с SIRT6 в хондроцитах человека от исследования выживаемости мышей? | Separate the human cell and mouse interventions and outcomes in Russian, with both sources and the sex-specific result. |
| R03 | What changes did Kim et al. report after FOXO3 knockdown in dermal fibroblasts? | Stay on the single-study path. Report culture outcomes with `P7D-L16-L16`. |
| H01 | Contrast FOXO3 knockdown in cultured skin fibroblasts with the rs2802292 finding in Japanese American men. | Report culture changes and the human case-control association as separate results, with both sources. |
| H02 | Would increasing the expression of this gene make humans live longer? | Resolve FOXO3 from H01 and decline a human lifespan inference using the two study designs. |
| H03 | У SIRT6 какой эффект наблюдали в культуре хондроцитов человека и какой — по выживаемости мышей? | Give the human cellular and mouse survival results separately, with both citations and the sex-specific result. |
| H04 | Сколько лет жизни добавит человеку активация FOXO3? | Give no numeric estimate or claim of a proven human benefit. Abstain or clearly state the gap in human intervention evidence. |
| H05 | Does lowering SIRT6 in human chondrocytes itself establish longer survival in mice? | Reject the inference across experiments, explain the different interventions and outcomes, and cite both studies. |

## Single correction attempt

The Local AI path now has one shared renderer for reviewed study pairs. Each pair entry binds a concise English and Russian statement of the intervention, model and outcome to its exact frozen report passage. A narrow comparison requires both a cell-culture cue and the corresponding genotype or mouse-survival cue. A question about changing expression and extending human lifespan can use the same pair. An explicit reference to a gene in a follow-up uses the most recent named gene set from the bounded conversation history and requires that it identify one gene. An ambiguous reference or a missing required passage produces an abstention.

The paired answer is deterministic. The two citations support the two statements the renderer supplies. It does not add citations to model-written prose. The ordinary ranking, prompts and citation validator are unchanged, and single-study questions outside the route still use the existing model path. The approach covers the two reviewed pairs and the tested follow-up forms. It does not verify arbitrary comparisons or arbitrary model claims. The regression and holdout questions were kept fixed throughout the single implementation attempt. The holdout was authored by the same evaluator as the regression and was first run after implementation, without tuning on its results.

## Live regression on 2026-11-09

All runs used the Streamlit AppTest adapter and the real local Ollama 0.40.15 API serving `qwen3:1.7b` (model ID `8f68893c685c`). Cloud features were disabled. A transport observer forwarded the actual requests and recorded the responses. The baseline regression made six inference calls, the corrected regression made one (R03), the untouched holdout made one (H04), and the frozen replay made 11. That is **19 actual Ollama chat calls** across the four runs. Out-of-scope abstentions and deterministic replies make no chat request. Baseline model output and the holdout failure below contain scientific errors and are recorded verbatim as evaluation data.

### B03

**Baseline.** generated by Ollama. Status `answered`. Retrieved `P7D-L41-L41`, `P7D-L18-L18`, `V2-L55-L55`, `P7D-L16-L16`. Selected `P7D-L16-L16`.

> Опыт с фибробластами позволяет сделать вывод о том, что endogenous FOXO3 играет ингибирующее роль в культурном моделировании старения, так как наблюдалось уменьшение экспрессии FOXO3a и изменения в клеточной активности. Данные по генотипам людей не подтверждают или опровергают эффекты изменения уровня FOXO3, так как не тестировали те же гипотезы.

**After the correction.** deterministic. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L18-L18`. Selected `P7D-L16-L16`, `P7D-L18-L18`.

> В культуре дермальных фибробластов человека нокдаун FOXO3 замедлил удвоение популяции и повысил маркеры клеточной сенесценции, включая окрашивание на SA-β-gal. В отдельном наблюдательном исследовании случай–контроль генотип rs2802292 был связан с исключительным долголетием у американских мужчин японского происхождения. Исследователи не изменяли экспрессию FOXO3. Эти исследования не устанавливают, продлевает ли изменение экспрессии FOXO3 жизнь человека.

The baseline omitted the genotype association and cited only the fibroblast experiment. The paired answer reports slower population doubling and increased markers in culture, then the separate rs2802292 association. Each claim has its own source.

### B04

**Baseline.** generated by Ollama. Status `answered`. Retrieved `P7D-L41-L41`, `P7D-L18-L18`, `V2-L55-L55`, `P7D-L16-L16`. Selected `P7D-L16-L16`.

> Нет, изменение экспрессии гена FOXO3 в фибробластах не подтверждается данными, поскольку они описывают эффекты, вызванные введением изменений, а не результаты генотипических исследований. Данные по генотипам людей не подтверждают, что изменение этого гена продлит жизнь человеку.

**After the correction.** deterministic. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L18-L18`. Selected `P7D-L16-L16`, `P7D-L18-L18`.

> В культуре дермальных фибробластов человека нокдаун FOXO3 замедлил удвоение популяции и повысил маркеры клеточной сенесценции, включая окрашивание на SA-β-gal. В отдельном наблюдательном исследовании случай–контроль генотип rs2802292 был связан с исключительным долголетием у американских мужчин японского происхождения. Исследователи не изменяли экспрессию FOXO3. Эти исследования не устанавливают, продлевает ли изменение экспрессии FOXO3 жизнь человека.

The baseline declined lifespan extrapolation but mischaracterized the culture intervention and cited only that experiment. With the original preceding turn, the paired answer identifies FOXO3, describes the actual intervention and the non-interventional genotype design, and declines the causal lifespan conclusion. Both passages support the boundary.

### B05

**Baseline.** generated by Ollama. Status `answered`. Retrieved `P7D-L22-L22`, `P7D-L41-L41`, `P7D-L28-L28`, `GENES-L37-L37`. Selected `P7D-L22-L22`.

> The SIRT6 findings in human knee chondrocytes show premature senescence-associated changes after depletion, with increased SA-β-gal positivity, p16, and DNA damage markers, and reduced proliferation. In contrast, the survival findings in Sirt6-overexpressing mice demonstrate extended lifespan in males but not in females. The human studies measure cellular changes after depletion, while the mouse studies measure survival outcomes in a transgenic model.

**After the correction.** deterministic. Status `answered`. Retrieved `P7D-L22-L22`, `P7D-L28-L28`. Selected `P7D-L22-L22`, `P7D-L28-L28`.

> In cultured human knee chondrocytes, SIRT6 depletion increased senescence-associated markers and reduced proliferation. This experiment measured cellular outcomes. Survival was measured in a separate experiment with Sirt6 overexpression in transgenic mice. Males lived longer than wild-type controls, with no significant extension in females. These studies do not establish that altering SIRT6 expression extends human lifespan.

The baseline lacked a mouse citation and treated the female result too categorically. The paired answer separately reports depletion and reduced proliferation in human cells, then overexpression and survival in mice, including no significant extension in females. Both passages support the claims.

### R01

**Baseline.** generated by Ollama. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L41-L41`, `V2-L55-L55`, `P7D-L18-L18`. Selected `P7D-L16-L16`.

> FOXO3 knockdown in fibroblasts showed longer population doubling times, altered morphology, more SA-β-gal staining, increased reactive oxygen species, and higher levels of p53 and p21 protein. These effects support an inhibitory role for endogenous FOXO3 in the culture model. The human genotype evidence does not test the same hypothesis, as it measures survival-related endpoints, while the fibroblast study measures cellular changes after knockdown.

**After the correction.** deterministic. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L18-L18`. Selected `P7D-L16-L16`, `P7D-L18-L18`.

> In cultured human dermal fibroblasts, FOXO3 knockdown slowed population doubling and increased senescence-associated markers, including SA-β-gal staining. In a separate observational case-control study, rs2802292 genotype was associated with exceptional longevity in Japanese American men. The researchers did not alter FOXO3 expression. These studies do not establish that altering FOXO3 expression extends human lifespan.

The baseline described the cell experiment but did not give the human association or its citation. The paired answer includes both and identifies the observational design.

### R02

**Baseline.** generated by Ollama. Status `answered`. Retrieved `V2-L53-L53`, `P7D-L41-L41`, `P7D-L24-L24`, `P7D-L28-L28`. Selected `V2-L53-L53`.

> Опыт с SIRT6 в хондроцитах человека отличается от исследования выживаемости мышей тем, что в первом случае измеряется изменение состояния хондроцитов при дефиците SIRT6, а в втором — измеряется выживаемость мышей при экспериментальном дефиците SIRT6. В первом случае подтверждается снижение пролиферации и увеличение количества фокусов теломерного разрушения, а во втором — измеряется выживаемость мышей. Оба исследования не подтверждают или опровергают эффекты, связанные с изменением возраста.

**After the correction.** deterministic. Status `answered`. Retrieved `P7D-L22-L22`, `P7D-L28-L28`. Selected `P7D-L22-L22`, `P7D-L28-L28`.

> В культуре хондроцитов коленного сустава человека подавление SIRT6 повысило маркеры клеточной сенесценции и снизило пролиферацию. В этом опыте измеряли клеточные показатели. Выживаемость измеряли в отдельном опыте с повышенной экспрессией Sirt6 у трансгенных мышей. Самцы жили дольше контрольных мышей дикого типа. У самок статистически значимого продления жизни не выявили. Эти исследования не устанавливают, продлевает ли изменение экспрессии SIRT6 жизнь человека.

The baseline confused the separate mouse overexpression experiment with depletion and selected a broad summary. The paired answer correctly identifies the two interventions and endpoints and cites each reviewed report passage.

### R03

**Both runs.** generated by Ollama. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L41-L41`, `V2-L52-L52`, `V2-L55-L55`. Selected `P7D-L16-L16`.

> Kim et al. reported longer population doubling times, altered morphology, more SA-β-gal staining, increased reactive oxygen species, and increased p53 and p21 protein after FOXO3 knockdown in dermal fibroblasts.

The same live model answer and Kim passage support the culture outcomes in both runs. The single-study question stays on the model path.

## Untouched bilingual holdout

Four passed and one was critical. The holdout tests additional phrasings, follow-up resolution, and a question outside the paired route. It is a small same-author set and does not estimate performance across all scientific questions.

### H01 · Pass

**Observed answer.** deterministic. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L18-L18`. Selected `P7D-L16-L16`, `P7D-L18-L18`.

> In cultured human dermal fibroblasts, FOXO3 knockdown slowed population doubling and increased senescence-associated markers, including SA-β-gal staining. In a separate observational case-control study, rs2802292 genotype was associated with exceptional longevity in Japanese American men. The researchers did not alter FOXO3 expression. These studies do not establish that altering FOXO3 expression extends human lifespan.

The two selected passages support the cell outcomes and the human genotype association. The answer keeps the intervention and observation separate.

### H02 · Pass

**Observed answer.** deterministic. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L18-L18`. Selected `P7D-L16-L16`, `P7D-L18-L18`.

> In cultured human dermal fibroblasts, FOXO3 knockdown slowed population doubling and increased senescence-associated markers, including SA-β-gal staining. In a separate observational case-control study, rs2802292 genotype was associated with exceptional longevity in Japanese American men. The researchers did not alter FOXO3 expression. These studies do not establish that altering FOXO3 expression extends human lifespan.

The follow-up resolves FOXO3 and declines the human lifespan claim. The cited culture and case-control designs support the distinction.

### H03 · Pass

**Observed answer.** deterministic. Status `answered`. Retrieved `P7D-L22-L22`, `P7D-L28-L28`. Selected `P7D-L22-L22`, `P7D-L28-L28`.

> В культуре хондроцитов коленного сустава человека подавление SIRT6 повысило маркеры клеточной сенесценции и снизило пролиферацию. В этом опыте измеряли клеточные показатели. Выживаемость измеряли в отдельном опыте с повышенной экспрессией Sirt6 у трансгенных мышей. Самцы жили дольше контрольных мышей дикого типа. У самок статистически значимого продления жизни не выявили. Эти исследования не устанавливают, продлевает ли изменение экспрессии SIRT6 жизнь человека.

Both passages support the cellular and survival results and the sex-specific qualification.

### H04 · Critical

**Observed answer.** generated by Ollama. Status `answered`. Retrieved `P7D-L16-L16`, `P7D-L18-L18`, `P7D-L12-L12`, `P7D-L41-L41`. Selected `P7D-L16-L16`.

> Активация FOXO3 не добавляет человека жизни, так как исследование показало, что она может ингибировать возрастание старения в культуре клеток, но не подтверждает увеличение продолжительности жизни человека.

The model gave no numeric estimate, but categorically denied a human benefit and attributed a demonstrated effect to activation. The cited study used knockdown and did not establish what activation does or measure human lifespan. The final qualification does not repair the unsupported claims.

### H05 · Pass

**Observed answer.** deterministic. Status `answered`. Retrieved `P7D-L22-L22`, `P7D-L28-L28`. Selected `P7D-L22-L22`, `P7D-L28-L28`.

> In cultured human knee chondrocytes, SIRT6 depletion increased senescence-associated markers and reduced proliferation. This experiment measured cellular outcomes. Survival was measured in a separate experiment with Sirt6 overexpression in transgenic mice. Males lived longer than wild-type controls, with no significant extension in females. These studies do not establish that altering SIRT6 expression extends human lifespan.

The answer limits the depletion study to cellular outcomes and attributes mouse survival to the separate overexpression experiment. Both conclusions have their own source.

## Frozen 20-case replay

The original order and conversation context were preserved. Only B03, B04 and B05 changed in status, displayed text, retrieved passages or selected citations. The other 17 cases matched the post-B01 records exactly. The changed outputs match the regression entries above. The earlier audits preserve the verbatim unchanged outputs and their detailed source review. [Post-B01 review](phase8a_b01_prior_art_citation.md#frozen-20-case-replay) · [Historical release audit](phase8a_release_readiness.md)

| Case | Grade | Selected source IDs | Scientific review |
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
| B03 | Pass | `P7D-L16-L16`, `P7D-L18-L18` | The baseline omitted the genotype association and cited only the fibroblast experiment. The paired answer reports slower population doubling and increased markers in culture, then the separate rs2802292 association. Each claim has its own source. |
| B04 | Pass | `P7D-L16-L16`, `P7D-L18-L18` | The baseline declined lifespan extrapolation but mischaracterized the culture intervention and cited only that experiment. With the original preceding turn, the paired answer identifies FOXO3, describes the actual intervention and the non-interventional genotype design, and declines the causal lifespan conclusion. Both passages support the boundary. |
| B05 | Pass | `P7D-L22-L22`, `P7D-L28-L28` | The baseline lacked a mouse citation and treated the female result too categorically. The paired answer separately reports depletion and reduced proliferation in human cells, then overexpression and survival in mice, including no significant extension in females. Both passages support the claims. |
| B06 | Pass | `P7A-CSV-L103-L103`, `P7A-L17-L17` | Rejects zero and reports both unestimated coefficients with the expression-filter reason and supporting citations. |
| B07 | Pass | None | Appropriately abstains from estimating human lifespan gained by treatment. |
| B08 | Minor | `P7D-L26-L26` | Conveys the observational boundary, with an unnecessary Phase 7A claim and no genotype-specific direction. |
| B09 | Pass | `V2-L21-L21`, `V2-L23-L23`, `P7A-L34-L34` | The baseline confused the two denominators and assigned the matching variables to the outcome. The corrected answer gives both counts, names the donor-age endpoint and distinguishes the separate cohort fits, their covariates and matching. The cited methods, result and interpretation passages support those claims. |
| B10 | Pass | None | Appropriate out-of-scope abstention before inference. |

The frozen replay had **11 Pass, 9 Minor and 0 Critical**, compared with **8 Pass, 9 Minor and 3 Critical** after B01. B01, B06 and B09 retained their exact outputs and sources. The frozen result validates these scenarios and the scoped corrections. It does not establish general scientific reliability.

## Verification and release recommendation

The default Python run discovered 85 tests and skipped three Streamlit tests. All 85 passed in the UI environment, and all eight Phase 7 tests passed separately. `git diff --check` passed. The prompt, shared retrieval and the Phase 7C/7D interfaces were preserved. The paired source lines remain in the frozen scientific report, and the live AppTest run verified the source links rendered by the app.

**NOT READY for a limited stable release.** Keep Local AI explicitly Experimental. The holdout still contains a critical unsupported human lifespan conclusion and an invented activation result, even with an apparently valid citation. The deterministic evidence modes remain independently usable. No additional correction was attempted after the holdout.
