# Introduction to Machine Learning — Never-Ending Learning

**Team:** Vũ · Nam · Đạt  
**Project theme:** Continual Learning / Online Learning / Lifelong Learning  
**Status:** Paper selection — waiting for Moodle acceptance

> This is the semester-long team repository for reading, independently reimplementing, reproducing, critiquing, and empirically stress-testing one published Machine Learning paper.

## 1. Selected paper

Complete this section **only after registration is marked Accepted** in Moodle's Topics sheet.

| Field | Value |
| --- | --- |
| Title | TBD |
| Authors | TBD |
| Venue / year | TBD |
| Official URL | TBD |
| Paper registration status | Pending |
| Reproduction scope | To choose: Full or Core |

**Selection checklist:** publication within 60 months; never chosen by another team; research fits Never-Ending Learning and ML material; conference CORE A/A*, journal SCIE Q1, or qualifying Google Scholar citations; sufficient datasets and computation. Paper registration is via Moodle, and instructor acceptance is needed before proceeding.

## 2. Team

| Member | Initial area of responsibility |
| --- | --- |
| Vũ | Coordinator, literature and theoretical analysis, README, slides and poster |
| Nam | Reimplementation, experiments, configuration, tests |
| Đạt | Evaluation, W&B tracking, empirical stress tests, plots |

All team members must understand **all** project components for the poster workshop. Record real contributions through commits and pull requests.

## 3. Deadlines

| Date | Deliverable |
| --- | --- |
| 07 Nov 2026 | Public repository link on Moodle |
| 21 Nov 2026 | Reading + reproduction slide deck (Milestone 2 + Lab 1) |
| 05 Dec 2026 | Critique + empirical-demonstration poster (Milestone 3 + Lab 2) |

Dates provided by the team; official Moodle notices prevail.

## 4. Repository map

```text
configs/                    Experiment settings, fixed random seeds
data/                       Dataset access instructions (not large datasets)
src/methods/                Independently implemented core method
src/models/                 Standard supporting model parts
src/datasets/               Programmatic HF/Kaggle downloads and preprocessing
src/utils/                  Metrics, seeding, logging utilities
scripts/                    Reproduction and empirical test entry points
notebooks/                  Exploratory notebooks
experiments/reproduction/   Lab 1 configuration and lightweight results
experiments/empirics/       Lab 2 configurations and evidence
docs/                       Reading notes and critical analysis
reports/                    Slides and poster
tests/                      Unit/regression tests
```

## 5. Environment and running

Use **Python >= 3.9**; record and pin tested package versions after paper acceptance.

```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
# source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Reproducibility:** document software/hardware, config, random seeds, command, output and corresponding W&B run for **every** experiment. Important functions need docstrings (purpose, parameters, returns). Document and cite any third-party/standard components reused. Do not copy the selected paper's core implementation; original code may be inspected/run only for verification/comparison.

## 6. Dataset preparation

Datasets must be fetched **programmatically** during the run from **Hugging Face or Kaggle**, with automatic preprocessing and split construction. Prefer existing public versions. If unavailable, upload a prepared version to one of these platforms so scripts can download it end to end. Dataset ID, license, version and preprocessing: **TBD**.

## 7. Reading (Milestone 2) + Reproduction (Lab 1)

Read: abstract → introduction → conclusion → background/related work → experiments → method. Explain the problem with a concrete example; at least 2 predecessor approaches and their practical limitations; theoretical, technical and empirical contributions; notation, pipeline, components, formulas, lemmas/theorems, and time/space complexity.

**Reproduction scope (choose and justify):**
- **Full:** reproduce all main reported experiments using the same/equivalent datasets.
- **Core:** reproduce at least 2 key experiments including the headline comparison, plus 1 additional analysis designed by the team.

Compare the paper's numbers with measured results and report relative deviations, explanations for meaningful gaps, and original-implementation comparisons where available. Scripts may use standard loaders and models; core research contribution must be independently implemented.

### W&B tracking — Lab 1

Use **one public W&B project** for both labs; tag reproduction runs `lab1-reproduction`.

| Experiment | Script/notebook | Config/dataset | W&B run URL | Observation |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

**Presentation:** one **PPTX 20–40 slides**, appendix included, **under 20 MB**. Every slide contains speaker notes **≤ 500 words**; slides should use team-created figures, visual diagrams/tables (no pasted original figures or raw code dumps). IEEE numbered citations at the **bottom of each citing slide**, with **no separate references slide**. Deck PPTX and public repo URL are submitted as separate Moodle entries.

## 8. Critical Analysis (Milestone 3)

Critique only **the theory**: hidden assumptions, proof/claim soundness, formulation/objective, complexity and generalizability. Develop evidence-backed:
- **At least 3 strengths**.
- **At least 2 theoretical limitations**, stated so an experiment can test each.
- **At least 2 future directions**, each tied to an identified limitation.

### Working draft

| Item | Theoretical argument and reference | Status |
| --- | --- | --- |
| Strength 1 / 2 / 3 | TBD | Not started |
| Limitation 1 / 2 | TBD | Not started |
| Future direction 1 / 2 | TBD | Not started |

## 9. Empirical Demonstration (Lab 2)

Design controlled experiments showing whether theoretically identified weaknesses occur (assumption-violating data, out-of-distribution/adversarial setups, ablations, replacement baselines, scaling, or parameter sensitivity). Maintain documented seeds and exact W&B runs, tagged `lab2-empirics`.

### W&B tracking — Lab 2

| Limitation tested | Script/notebook | Config/dataset | W&B run URL | Evidence |
| --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD |

**Poster:** one **PPTX containing a single portrait A2 slide**. Place the argued theoretical weakness beside its supporting empirical measurement. If >2 weaknesses are established both theoretically and empirically, display the **two most notable** on the poster and explain other proven weaknesses with W&B links **in this README**. Upload poster via Moodle and defend it at the final oral workshop.

## 10. Integrity and references

- Do not copy paper text, figures or code, or another team's work.
- AI assistance is allowed; team members are responsible for every result.
- Keep the history of meaningful commits visible and experiments traceable.
- Record reused libraries, datasets, models, references and licenses here as work progresses.

**References and reused software:** TBD.

---

**Initial scaffold only.** Do not invent experiment results; replace TBD entries once the paper is accepted and experiments have been run.
