"""Check dataset integrity and reproduce the reported statistical results."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def rows(root: Path, name: str) -> list[dict]:
    with (root / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_hashes(root: Path) -> int:
    """Reject missing, extra, changed or out-of-package files."""
    entries = rows(root, "SHA256SUMS.csv")
    expected = {item["path"] for item in entries} | {"SHA256SUMS.csv"}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and ".git" not in p.parts}
    if actual != expected:
        raise ValueError("File inventory differs from the release snapshot")
    for item in entries:
        path = (root / item["path"]).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError("Invalid package member")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("File hash mismatch: " + item["path"])
    return len(entries)


def summary(root: Path) -> list[dict]:
    """Follow the manuscript: seed medians within project, then project medians."""
    runs = rows(root, "data/run_metrics.csv")
    groups = defaultdict(list)
    for item in runs:
        groups[(item["panel"], item["method"])].append(item)
    result = []
    for (panel, method), group in sorted(groups.items()):
        projects = defaultdict(list)
        for item in group:
            projects[item["case_id"]].append(float(item["hv_norm"]))
        result.append({"panel": panel, "method": method, "runs": len(group),
                       "successful_runs": sum(item["run_feasible"].lower() == "true" for item in group),
                       "project_median_hv": statistics.median(statistics.median(values) for values in projects.values()),
                       "run_median_seconds": statistics.median(float(item["elapsed_seconds"]) for item in group)})
    return result


def full_check(root: Path) -> dict:
    """Recompute indicators and exact signed-rank/Holm tests from exported values."""
    import numpy as np
    from pymoo.indicators.hv import HV
    from pymoo.indicators.igd import IGD
    from scipy.stats import rankdata

    runs = rows(root, "data/run_metrics.csv")
    bounds = {r["case_id"]: r for r in rows(root, "data/reference_bounds.csv")}
    references = defaultdict(list)
    fronts = defaultdict(list)
    for r in rows(root, "data/reference_fronts.csv"):
        references[r["case_id"]].append([float(r[f"F{i}_norm"]) for i in [1, 2, 3]])
    for r in rows(root, "data/attained_objective_fronts.csv"):
        fronts[r["run_id"]].append([float(r[f"F{i}"]) for i in [1, 2, 3]])
    max_hv_error = max_igd_error = 0.0
    for r in runs:
        values = fronts[r["run_id"]]
        if not values:
            if float(r["hv_norm"]) != 0.0 or r["igd_norm"] != "":
                raise ValueError("Empty-front metric convention differs")
            continue
        scale = bounds[r["case_id"]]
        low = np.array([float(scale[f"lower_F{i}"]) for i in [1, 2, 3]])
        span = np.array([float(scale[f"span_F{i}"]) for i in [1, 2, 3]])
        normalized = (np.asarray(values) - low) / span
        hv = float(HV(ref_point=np.array([1.1, 1.1, 1.1]))(normalized))
        igd = float(IGD(np.array(references[r["case_id"]]))(normalized))
        max_hv_error = max(max_hv_error, abs(hv - float(r["hv_norm"])))
        max_igd_error = max(max_igd_error, abs(igd - float(r["igd_norm"])))
    if max(max_hv_error, max_igd_error) > 1e-10:
        raise ValueError("Recomputed objective-set indicators differ")

    effects = defaultdict(list)
    for item in rows(root, "data/paired_project_effects.csv"):
        effects[(item["panel"], item["comparator"], item["metric"])].append(float(item["effect"]))
    tests = rows(root, "data/paired_summary.csv")
    computed = []
    for item in tests:
        key = (item["panel"], item["comparator"], item["metric"])
        differences = np.array(effects[key])
        differences = differences[np.abs(differences) > 1e-9]
        if len(differences):
            ranks = rankdata(np.abs(differences), method="average")
            observed = abs(np.sum(np.sign(differences) * ranks))
            signs = 2 * ((np.arange(2 ** len(ranks))[:, None] >> np.arange(len(ranks))) & 1) - 1
            p = float(np.mean(np.abs(signs @ ranks) >= observed - 1e-10))
        else:
            p = 1.0
        if not math.isclose(p, float(item["p_raw_exact_signed_rank"]), abs_tol=1e-12):
            raise ValueError("Exact paired-test result differs")
        computed.append((item, p))
    for panel in sorted({item["panel"] for item in tests}):
        selected = [(item, p) for item, p in computed if item["panel"] == panel]
        ps = np.array([p for _, p in selected])
        order = np.argsort(ps)
        adjusted = np.empty_like(ps)
        adjusted[order] = np.minimum(1, np.maximum.accumulate(ps[order] * np.arange(len(ps), 0, -1)))
        for (item, _), value in zip(selected, adjusted):
            if not math.isclose(float(value), float(item["p_holm"]), abs_tol=1e-12):
                raise ValueError("Holm correction differs")
    return {"runs_with_indicators_checked": len(runs), "paired_tests_checked": len(tests),
            "maximum_hv_absolute_error": max_hv_error, "maximum_igd_absolute_error": max_igd_error,
            "physics_or_optimization_rerun": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--full-check", action="store_true", help="Requires NumPy, SciPy and pymoo")
    args = parser.parse_args()
    result = {"status": "PASS", "files_hashed": verify_hashes(args.root), "summaries": summary(args.root)}
    if args.full_check:
        result["independent_checks"] = full_check(args.root)
    print(json.dumps(result, indent=2, allow_nan=False))
