# DG-CGMOEA: Numerical Evidence for Construction Site Layout Planning

Author-approved numerical evidence release, version 1.0.0. Repository: https://github.com/zzhe0359-cyber/DG-CGMOEA-CSLP-evidence

Authors: Zhe Zhang and Jin Wang, School of Civil Engineering, Central South University. This repository accompanies a research manuscript; it does not imply journal acceptance. No DOI or reuse license has been assigned. Public accessibility does not by itself grant a reuse license.

This package selects only the current geometric-spreading evidence used by manuscript V10. Historical learning-guidance, earlier acoustic-model, and superseded experiment families are not included.

## Contents and boundaries

- 465 comparison runs: 15 development projects with seven methods and 10 additional projects with five methods, all at three seeds.
- The additional panel is named `opened_heldout`: it is post hoc confirmation on previously examined projects, not an untouched blind test.
- One separate illustrative case: 20,100 evaluated layouts, 47 Pareto alternatives, population-search summaries, and numerical repair examples. It is not part of the 25-project comparison denominator.
- Fixed-set noise-source sensitivity: 948 layouts in 24 covered cases. The coverage table retains two development cases without feasible layouts. Each covered case has one nominal scenario and 30 scenarios for each of two perturbation structures.
- Per-run attained objective fronts and shared normalization/reference definitions permit independent HV/IGD recalculation. Raw objective values are retained without privacy noise, scaling or numerical rounding for presentation.

This is not a complete optimization benchmark. Raw CAD, full input workbooks, object coordinates, site polygons, receiver coordinates, original case identifiers, local paths and private crosswalks are excluded. It cannot independently regenerate layouts, validate geometry/A* transport, or recompute new acoustic scenarios. Those require permitted model inputs. Existing scientific numbers may match figures or other records, so the package is pseudonymized, not guaranteed anonymous.

## Data conventions

CSV uses UTF-8, a decimal point and one header row. Missing/undefined values are blank, not zero. Zero HV for a run without a feasible front is the published analysis convention; its IGD remains undefined. Numeric values are exported at round-trip precision.

`D001`-style identifiers denote development projects, `H001`-style identifiers the additional projects, and `C001` the separate illustrative case. Run identifiers combine the pseudonymous case, method and random seed. A case has the same identifier in all tables. Solution identifiers are case-scoped and consistent between sensitivity and illustrative Pareto data; `paper_solution_id` links the latter to labels already used in the paper.

`F1`/`F1_noise` is modeled receiver noise in dB(A). `F2`/`F2_closeness` is the minimization-form facility-closeness planning score; `F3`/`F3_transportation` is the modeled transportation-cost score. All three are minimized. Do not infer a calibrated currency from the exported score alone. A normalized HV can exceed one because its reference point is (1.1, 1.1, 1.1).

Constraint components `boundary`, `non_overlap` and `unavailable_zone` report implementation area violations, whereas `tower_crane_coverage` reports a distance shortfall. Their implementation sum is a violation score, not a single physical measurement with common units. Runtime columns are seconds; NFE is a count of complete objective-and-constraint evaluations. Constraint-only repair probes consume time but do not increment that NFE.

In `project_metrics`, `elapsed_seconds` is the median of seed runtimes within the project. The paper's panel runtime is the run-level median, reconstructed directly from `run_metrics`; these are distinct aggregations. Paired effects are positive in favor of D5R2. Runtime and IGD effects reverse the subtraction direction accordingly. Conditional IGD comparisons use same-seed jointly feasible pairs before project aggregation, not unmatched feasible-run medians.

`data_dictionary.csv` lists fields, inferred types and missing counts. `metadata.json` lists table sizes and the scope of reproducibility. Source offsets are retained exactly with neutral case/source identifiers; they do not provide the underlying source-to-receiver geometry needed for new propagation calculations.

## Local verification

With Python 3.10 or later:

```text
python verify_and_reproduce.py
```

This checks every release file hash and reproduces method counts and summary values using the standard library. The Git metadata directory and Python bytecode caches are ignored. For independent HV/IGD and exact paired-test checks, install compatible NumPy and SciPy plus pymoo 0.6.1.5, then run:

```text
python verify_and_reproduce.py --full-check
```

The check does not rerun any optimizer or perform independent physics validation. No network operation or publication is performed by the script. Hashes establish package consistency, not measurement validity or publication permission.
