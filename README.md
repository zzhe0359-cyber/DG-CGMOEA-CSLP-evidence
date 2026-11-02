# DG-CGMOEA for Construction Site Layout Planning

**Zhe Zhang and Jin Wang**  
School of Civil Engineering, Central South University

This repository contains the research data and statistical verification script for our study, *DG-CGMOEA: Knowledge-informed construction site layout planning using dynamic conflict graphs and multi-objective evolutionary optimization*.

We develop a dynamic graph and constraint-guided multi-objective evolutionary algorithm (DG-CGMOEA) to plan temporary facilities, tower cranes, and material hoists on space-constrained construction sites. The method identifies active spatial conflicts and applies constraint-specific geometric repairs within a genetic--particle-swarm search, generating feasible alternatives that balance receiver noise, facility closeness, and material transportation cost.

## Experiments

| Experiment | Cases | Runs or layouts | Purpose |
| --- | ---: | ---: | --- |
| Development comparison | 15 | 315 runs | Compare constrained optimizers and examine repair mechanisms |
| Additional project comparison | 10 | 150 runs | Examine performance on additional projects |
| Canteen planning case | 1 | 20,100 evaluated layouts; 47 feasible Pareto alternatives | Examine the search process and preference-based selection |
| Noise-source sensitivity | 24 | 948 fixed layouts | Assess ranking and Pareto-set changes under source-level perturbations |

The project comparisons use three random seeds and a budget of 1,050 complete evaluations per run. Across the 25 projects, DG-CGMOEA produces feasible fronts in 69 of 75 runs, compared with 29 of 75 for the same hybrid without conflict-guided repair and 19 of 75 for each constrained NSGA baseline. Project-level effects and statistical tests are supplied alongside the run metrics.

The canteen case is reported separately from these comparisons. The sensitivity analysis uses one nominal scenario and 30 scenarios for each of two perturbation structures per covered case; `sensitivity_coverage.csv` also records the two Development cases without feasible candidate sets.

## Data Guide

All data tables are in [`data/`](data/).

| Files | Contents |
| --- | --- |
| `case_manifest.csv` | Case identifiers, object counts, decision-variable counts, and sensitivity coverage |
| `run_metrics.csv`, `project_metrics.csv` | Run outcomes and project-level summaries |
| `paired_project_effects.csv`, `paired_summary.csv` | Paired effects, intervals, exact signed-rank tests, and Holm-adjusted p-values |
| `attained_objective_fronts.csv` | Objective values of the feasible fronts obtained in each run |
| `reference_bounds.csv`, `reference_fronts.csv` | Shared normalization bounds and empirical reference fronts for each project |
| `sensitivity_candidate_objectives.csv` | Nominal objective values of the fixed candidate layouts |
| `sensitivity_coverage.csv`, `sensitivity_scenario_results.csv` | Case coverage and scenario-level ranking and front-membership results |
| `sensitivity_case_summary.csv`, `sensitivity_panel_summary.csv` | Case- and panel-level sensitivity summaries |
| `sensitivity_source_offsets.csv` | Source-level perturbations used in the sensitivity analysis |
| `illustrative_pareto_alternatives.csv`, `illustrative_recorded_objectives.csv` | Canteen alternatives and the evaluated recorded layout |
| `illustrative_evaluation_outcomes.csv`, `illustrative_search_history.csv` | Canteen evaluation outcomes and population-search history |
| `illustrative_repair_examples.csv` | Numerical before-and-after results for selected repair examples |

[`data_dictionary.csv`](data_dictionary.csv) describes the fields, data types, and missing values. [`metadata.json`](metadata.json) provides the table inventory, and [`SHA256SUMS.csv`](SHA256SUMS.csv) records file checksums.

### Case and Method Identifiers

`D001`-style identifiers refer to Development projects, `H001`-style identifiers to additional projects, and `C001` to the canteen case. Identifiers are consistent across tables. The additional panel is stored as `opened_heldout`, denoting a post hoc confirmation on projects examined in earlier work. Solution identifiers are case-specific, and `paper_solution_id` connects canteen alternatives to the labels used in the article.

| Method identifier | Configuration |
| --- | --- |
| `NSGA2`, `NSGA3` | Constrained NSGA-II and NSGA-III |
| `CTAEA` | Constrained two-archive evolutionary algorithm |
| `D5R1` | Genetic--particle-swarm hybrid with geometry-aware initialization and feasibility-first survival |
| `D5R2` | DG-CGMOEA, adding dynamic conflict diagnosis and geometric repair to D5R1 |
| `D5R2_NO_STATIC` | D5R2 with static relation weights removed from repair |
| `D5R2_AGGREGATE_GRADIENT` | D5R2 with aggregate numerical repair using finite-difference pseudoinverse steps |

The Development panel includes all seven configurations; the additional panel includes `NSGA2`, `NSGA3`, `CTAEA`, `D5R1`, and `D5R2`.

### Metric Conventions

- `F1` is modeled receiver noise in dB(A), `F2` is the facility-closeness score in minimization form, and `F3` is the material transportation-cost score. All three objectives are minimized; F2 and F3 are planning scores.
- A run without a feasible front has HV equal to zero and undefined IGD. Undefined values are blank in the CSV files. The normalized HV reference point is `(1.1, 1.1, 1.1)`, so HV may exceed one.
- Panel HV is calculated by taking the median across seeds within each project, then the median across projects. Panel runtime is the median across runs; the `elapsed_seconds` column in `project_metrics.csv` gives within-project seed medians.
- Positive paired effects favor D5R2. For runtime and IGD, the effect is comparator minus D5R2; for HV and feasible-run rate, it is D5R2 minus comparator. Conditional IGD uses same-seed jointly feasible pairs before project aggregation.
- Boundary, non-overlap, and unavailable-zone violations are areas in square meters; crane-coverage violations are distance shortfalls in meters. Their sum is the aggregate violation score used by the implementation.
- Runtime is measured in seconds. NFE counts complete objective-and-constraint evaluations; constraint-only repair checks contribute to runtime separately.

Tables use UTF-8 CSV and retain round-trip numerical precision. Site and source identifiers are pseudonymized. The shared materials comprise objective values and numerical logs; raw drawings and site coordinates are not distributed in this repository.

## Reproduce the Statistical Results

Use Python 3.10 or later. The following command checks file integrity and reproduces method summaries using the Python standard library:

```bash
python verify_and_reproduce.py
```

To also recalculate HV, IGD, exact signed-rank tests, and Holm corrections:

```bash
python -m pip install numpy scipy pymoo==0.6.1.5
python verify_and_reproduce.py --full-check
```

The full check covers indicators for all 465 comparison runs and the 40 paired tests. It returns a JSON report containing method summaries and the differences between the supplied and recalculated indicators.

## Citation

Please cite this dataset when using the data or reporting analyses based on them. Author and dataset information are provided in [`CITATION.cff`](CITATION.cff).
