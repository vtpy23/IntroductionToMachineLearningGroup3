# Introduction to Machine Learning — Never-Ending Learning

**Team:** Vũ · Nam · Đạt  
**Project theme:** Continual Learning / Online Learning / Lifelong Learning  
**Status:** DS-AL accepted; core CIFAR-100 comparisons completed for seeds 0, 1 and 2 with verified public W&B histories. The current 40-slide deck reports three-seed mean ± sample SD. Instructor acceptance of the adapted ablation scope remains unconfirmed.

> This is the semester-long team repository for reading, independently reimplementing, reproducing, critiquing, and empirically stress-testing one published Machine Learning paper.

## 1. Selected paper

Registration has been **Accepted**, as confirmed by the team. See [project status](docs/STATUS.md).

| Field | Value |
| --- | --- |
| Title | DS-AL: A Dual-Stream Analytic Learning for Exemplar-Free Class-Incremental Learning |
| Authors | Huiping Zhuang, Run He, Kai Tong, Ziqian Zeng, Cen Chen, Zhiping Lin |
| Venue / year | AAAI 2024, 38(15), 17237–17244 |
| Official URL | https://doi.org/10.1609/aaai.v38i15.29670 |
| Paper registration status | Accepted, confirmed by the team |
| Reproduction scope | Core: CIFAR-100 / ResNet-32; comparisons, ablations, phase-count and buffer-width analyses |

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

Tested with **Python 3.11.8**, PyTorch 2.5.1+cu121, torchvision 0.20.1+cu121 on an RTX 4050 Laptop 6 GB / 16 GB RAM. Dependencies are pinned in requirements.txt. See [run guide](docs/REPRODUCTION.md).

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

The pipeline downloads **uoft-cs/cifar100 from Hugging Face** programmatically and pins its resolved revision. Images are normalized automatically and fine labels are remapped to an explicitly recorded class order. The dataset card declares its license unknown; do not assign a license to the data. See [dataset and preprocessing](docs/DATA.md).

## 7. Reading (Milestone 2) + Reproduction (Lab 1)

Read: abstract → introduction → conclusion → background/related work → experiments → method. Explain the problem with a concrete example; at least 2 predecessor approaches and their practical limitations; theoretical, technical and empirical contributions; notation, pipeline, components, formulas, lemmas/theorems, and time/space complexity.

**Reproduction scope (choose and justify):**
- **Full:** reproduce all main reported experiments using the same/equivalent datasets.
- **Core:** reproduce at least 2 key experiments including the headline comparison, plus 1 additional analysis designed by the team.

Compare the paper's numbers with measured results and report relative deviations, explanations for meaningful gaps, and original-implementation comparisons where available. Scripts may use standard loaders and models; core research contribution must be independently implemented.

### W&B tracking — Lab 1

Use **one public W&B project** for both labs; tag reproduction runs `lab1-reproduction`.

Project and verified run URLs: [W&B on Forge](docs/WANDB.md). [Three-seed results and each run](experiments/multiseed/20261119/RESULTS.md), [completion audit](experiments/multiseed/20261119/COMPLETION_REPORT.md), and [slide statistics](reports/milestone2_final/THREE_SEEDS_RESULTS.md) cover ACIL, DAC without PLC and DS-AL at K=5. Phase-count and buffer sweeps below remain seed 0; synthetic tests are separate evidence.

| Experiment | Script | Published config / history | W&B run | Result / scope |
| --- | --- | --- | --- | --- |
| base-training | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/base-training/config.json), [history](experiments/evidence/base-training/metrics.jsonl) | [zuc29egg](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/zuc29egg) | 160 epochs; final base test 76.92% |
| acil-k5 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/acil-k5/config.json), [history](experiments/evidence/acil-k5/metrics.jsonl) | [h2sljkd5](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/h2sljkd5) | A-bar 65.7880%; A_K 56.56% (CIFAR seed 0) |
| dac-no-plc-k5 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/dac-no-plc-k5/config.json), [history](experiments/evidence/dac-no-plc-k5/metrics.jsonl) | [gpx1ehdu](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/gpx1ehdu) | A-bar 65.4830%; A_K 56.24% (CIFAR seed 0) |
| dsal-k5 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/dsal-k5/config.json), [history](experiments/evidence/dsal-k5/metrics.jsonl) | [i0kiycme](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/i0kiycme) | A-bar 65.8219%; A_K 56.87% (CIFAR seed 0) |
| dsal-k25 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/dsal-k25/config.json), [history](experiments/evidence/dsal-k25/metrics.jsonl) | [c0niqv2k](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/c0niqv2k) | A-bar 65.5433%; A_K 56.83% (CIFAR seed 0) |
| dsal-k50 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/dsal-k50/config.json), [history](experiments/evidence/dsal-k50/metrics.jsonl) | [mb9xncbl](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/mb9xncbl) | A-bar 65.5361%; A_K 56.87% (CIFAR seed 0) |
| buffer-512 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/buffer-512/config.json), [history](experiments/evidence/buffer-512/metrics.jsonl) | [k64nfaxk](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/k64nfaxk) | A-bar 62.7726%; A_K 51.46% (CIFAR seed 0) |
| buffer-1024 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/buffer-1024/config.json), [history](experiments/evidence/buffer-1024/metrics.jsonl) | [ec7ki95r](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/ec7ki95r) | A-bar 63.8973%; A_K 53.36% (CIFAR seed 0) |
| buffer-2048 | [scripts/run.py](scripts/run.py) | [Config](experiments/evidence/buffer-2048/config.json), [history](experiments/evidence/buffer-2048/metrics.jsonl) | [rugifzey](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/rugifzey) | A-bar 65.1099%; A_K 54.97% (CIFAR seed 0) |
| reference-comparison | [scripts/compare_reference.py](scripts/compare_reference.py) | [Config](experiments/evidence/reference-comparison/config.json), [history](experiments/evidence/reference-comparison/metrics.jsonl) | [nv8x5tld](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/nv8x5tld) | Synthetic equation/mechanism test; not CIFAR benchmark |
| phase-dependence | [scripts/empirics.py](scripts/empirics.py) | [Config](experiments/evidence/phase-dependence/config.json), [history](experiments/evidence/phase-dependence/metrics.jsonl) | [hh31425p](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/hh31425p) | Synthetic equation/mechanism test; not CIFAR benchmark |
| ridge-residue | [scripts/empirics.py](scripts/empirics.py) | [Config](experiments/evidence/ridge-residue/config.json), [history](experiments/evidence/ridge-residue/metrics.jsonl) | [is6rnul0](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/is6rnul0) | Synthetic equation/mechanism test; not CIFAR benchmark |
| scaling | [scripts/empirics.py](scripts/empirics.py) | [Config](experiments/evidence/scaling/config.json), [history](experiments/evidence/scaling/metrics.jsonl) | [p343muf2](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/p343muf2) | Synthetic equation/mechanism test; not CIFAR benchmark |

**Presentation:** one **PPTX 20–40 slides**, appendix included, **under 20 MB**. Every slide contains speaker notes **≤ 500 words**; slides should use team-created figures, visual diagrams/tables (no pasted original figures or raw code dumps). IEEE numbered citations at the **bottom of each citing slide**, with **no separate references slide**. Deck PPTX and public repo URL are submitted as separate Moodle entries.

## 8. Critical Analysis (Milestone 3)

Critique only **the theory**: hidden assumptions, proof/claim soundness, formulation/objective, complexity and generalizability. Develop evidence-backed:
- **At least 3 strengths**.
- **At least 2 theoretical limitations**, stated so an experiment can test each.
- **At least 2 future directions**, each tied to an identified limitation.

### Working draft

| Item | Theoretical argument and reference | Status |
| --- | --- | --- |
| Strengths | Exact fixed-feature ridge solution, exemplar-free sufficient statistics, complementary residual fitting | Argued in [theory critique](docs/THEORY_CRITIQUE.md) |
| Limitation 1 | Main-stream equivalence does not imply exact phase invariance of DAC targets | Controlled synthetic measurements available |
| Limitation 2 | Ridge residual satisfies X^T E = gamma W, requiring care with the null-space interpretation | Controlled synthetic measurements available |
| Future directions | Recompute residual targets with cross moments; formally specified orthogonal/residual compensation | Proposals, not implemented method improvements |

## 9. Empirical Demonstration (Lab 2)

Design controlled experiments showing whether theoretically identified weaknesses occur (assumption-violating data, out-of-distribution/adversarial setups, ablations, replacement baselines, scaling, or parameter sensitivity). Maintain documented seeds and exact W&B runs, tagged `lab2-empirics`.

### W&B tracking — Lab 2

| Limitation tested | Script/notebook | Config/dataset | W&B run URL | Evidence |
| --- | --- | --- | --- | --- |
| Phase dependence of DAC | `python -m scripts.empirics` | Same synthetic data and projection, varying phase partitions | [Verified run](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/hh31425p) | [Measured records](experiments/empirics/phase-dependence.json) |
| Ridge residual geometry | `python -m scripts.empirics` | Fixed synthetic features, gamma sweep | [Verified run](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/is6rnul0) | [Measured records](experiments/empirics/ridge-residue.json) |
| Buffer scaling (supporting analysis) | `python -m scripts.empirics` | Synthetic data, width sweep | [Verified run](https://forge.coreweave.com/wandb/vu-lam-vnuhcm-university-of-science/intro-ml-group3-dsal/runs/p343muf2) | [Measured records](experiments/empirics/scaling.json) |

**Poster:** one **PPTX containing a single portrait A2 slide**. Place the argued theoretical weakness beside its supporting empirical measurement. If >2 weaknesses are established both theoretically and empirically, display the **two most notable** on the poster and explain other proven weaknesses with W&B links **in this README**. Upload poster via Moodle and defend it at the final oral workshop.

## 10. Integrity and references

- Do not copy paper text, figures or code, or another team's work.
- AI assistance is allowed; team members are responsible for every result.
- Keep the history of meaningful commits visible and experiments traceable.
- Record reused libraries, datasets, models, references and licenses here as work progresses.

**References and reused software:** DS-AL main paper and Supplement A–C, ACIL (NeurIPS 2022), standard CIFAR ResNet architecture, torchvision transforms, HF hub/pyarrow, Pillow, W&B and matplotlib. Method equations are independently implemented in `src/methods/analytic.py`; the official implementation is isolated under gitignored `artifacts/reference/official` for comparison only. See [reading notes](docs/READING_NOTES.md) and [reproduction decisions](docs/REPRODUCTION.md).

---

## 11. Automated workflow

Current Vietnamese deck: [submission 03.pptx](reports/milestone2_final/submission_3seeds/03.pptx), [full-name PPTX](reports/milestone2_final/DSAL_Milestone2_Lab1_3Seeds_Final.pptx), [PDF preview](reports/milestone2_final/DSAL_Milestone2_Lab1_3Seeds_Final.pdf), and [PptxGenJS source](reports/milestone2_final/build_three_seeds.mjs).
The deck contains 40 slides, speaker notes, IEEE citations, nine native charts, twenty native tables and per-seed W&B hyperlinks. Main comparisons use three-seed mean ± sample SD (ddof=1); K/buffer sweeps retain seed 0. [Validation and rebuild guide](reports/milestone2_final/FINAL_VALIDATION_REPORT.md) records the limits, including seed0's CUDA-to-CPU resume. The earlier seed0 decks and `reports/output/` remain **legacy / draft**, not the current submission.

Trace every reported number through the [experiment mapping](reports/milestone2_final/EXPERIMENT_TRACEABILITY.md), [byte-identical config/summary/history snapshots](experiments/evidence/README.md), [source hashes and verified W&B snapshot](reports/milestone2_final/assets/verified_evidence.json), and [academic content / notes](reports/milestone2_final/SLIDE_CONTENT.md). See the [review report](reports/milestone2_final/SLIDE_REVIEW_REPORT.md) and [update guide](reports/milestone2_final/HOW_TO_UPDATE_SLIDES.md).

**Scope limitation:** DAC/PLC ablation adapts the paper's ImageNet-Full experiment to CIFAR-100; it is not an exact reproduction of Table 2 and requires instructor acceptance of this scope. Benchmark mean/std is not yet available. The repository is public; do not interpret published slides as completion of the later poster/Lab 2 assessment.

```powershell
./scripts/bootstrap.ps1 -Cuda
./scripts/start_pipeline.ps1 -Tracking offline
.venv/Scripts/python.exe -X utf8 -m scripts.status
```

The unattended pipeline runs mathematical checks, a reduced-data smoke suite, controlled mechanism tests, full CIFAR-100 base training and the configured core suite, then generates result tables. It checkpoints each training epoch and skips completed matching analytic runs. Create `.stop-project` to request a pause after the current epoch/run; remove it before restarting.

For the completed paired core three-seed study and safe resume: [study guide](experiments/multiseed/20261119/README.md). The generic `scripts.multiseed` command expands the entire K/buffer suite; it was not used for the restricted seed1/2 study.
For cloud execution: [Colab/Kaggle notebook](notebooks/Colab_Kaggle.ipynb).
After W&B login: `python -m scripts.sync_wandb --entity YOUR_ENTITY`, followed by `python -m scripts.summarize`.

**Evidence policy:** smoke tests, synthetic mechanism tests and paper-protocol image experiments are labeled separately. Offline measurements are real but do not meet the public tracking requirement until synced and verified. No incomplete experiment is filled with estimated or invented results. AI-assisted code/document preparation is recorded honestly; each team member must independently understand and defend the work.
