"""SOT-M2 Stage 1 decision rule (PREREG_SOTM2_STAGE1.md section 7). CPU only, numpy.

Success = Open3DSOT TorchSuccess (trapz over 21 IoU thresholds in [0, 1], x100, 3D IoU);
Precision = trapz over 21 distance thresholds in [0, 2] m, x100. Cells use non-first keyframes and the fixed
bins.csv (single-sweep keyframe GT): ``pts_lt10`` and ``moving`` (keyframe step >= 0.5 m).
Paired tracklet bootstrap: one multinomial tracklet draw per resample shared by all arms, B = 10,000, seed 0,
95 % percentile CI. The contrast per cell is D - max(C, I), with the max taken inside every resample.

    python -m gpu_jobs.sotm2.decide FRAMES_CSV BINS_CSV OUT_JSON
"""
import csv, json, sys
import numpy as np

B, SEED = 10000, 0
TH_S = np.linspace(0, 1, 21)
TH_P = np.linspace(0, 2, 21)
CELLS = ["pts_lt10", "moving"]
SETS = ["overall_o3d", "overall_nonfirst", "pts_lt10", "moving", "moving_and_pts_lt10"]
GO_POINT, GO_SE = 2.0, 2.0
KILL_POINT, KILL_UPPER = 0.5, 2.0


def _trapz(y, x):
    y = np.asarray(y, float)
    return np.sum((y[..., 1:] + y[..., :-1]) / 2 * np.diff(x), axis=-1)


def in_set(name, key, bins):
    if name == "overall_o3d":
        return True
    if key[1] == 0:
        return False
    b = bins[key]
    return {"overall_nonfirst": True, "moving": b["moving"] == "1", "pts_lt10": b["pts_lt10"] == "1",
            "moving_and_pts_lt10": b["moving"] == "1" and b["pts_lt10"] == "1"}[name]


def counts(rows, bins, arms, sets):
    tids = sorted({int(r["tid"]) for r in rows}); ti = {t: i for i, t in enumerate(tids)}
    C = {(a, s, m): np.zeros((len(tids), 21)) for a in arms for s in sets for m in "sp"}
    N = {(a, s): np.zeros(len(tids)) for a in arms for s in sets}
    for r in rows:
        a = r["arm"]
        if a not in arms:
            continue
        key = (int(r["tid"]), int(r["k"])); i = ti[key[0]]
        iou, dist = float(r["iou"]), float(r["dist"])
        for s in sets:
            if in_set(s, key, bins):
                C[(a, s, "s")][i] += iou >= TH_S; C[(a, s, "p")][i] += dist <= TH_P; N[(a, s)][i] += 1
    return tids, C, N


def score(Cm, n, th):
    return _trapz(Cm / n[..., None], th) * 100 / th[-1]


def decide(frames_rows, bins, n_boot=B, seed=SEED):
    arms = sorted({r["arm"] for r in frames_rows})
    tids, C, N = counts(frames_rows, bins, arms, SETS)
    T = len(tids)
    W = np.random.default_rng(seed).multinomial(T, np.full(T, 1 / T), size=n_boot).astype(float)
    res = {"per_arm": {a: {s: {"success": round(float(score(C[(a, s, "s")].sum(0), N[(a, s)].sum(), TH_S)), 3),
                                "precision": round(float(score(C[(a, s, "p")].sum(0), N[(a, s)].sum(), TH_P)), 3)}
                            for s in SETS} for a in arms},
           "n_frames": {s: int(N[(arms[0], s)].sum()) for s in SETS}, "n_tracklets": T, "cells": {}}
    for s in CELLS:
        pt = {a: float(score(C[(a, s, "s")].sum(0), N[(a, s)].sum(), TH_S)) for a in ("C", "I", "D")}
        bt = {a: score(W @ C[(a, s, "s")], W @ N[(a, s)], TH_S) for a in ("C", "I", "D")}
        point = pt["D"] - max(pt["C"], pt["I"])
        bd = bt["D"] - np.maximum(bt["C"], bt["I"])
        lo, hi = np.nanpercentile(bd, [2.5, 97.5]); se = float(np.nanstd(bd, ddof=1))
        res["cells"][s] = dict(point=round(point, 3), ci95=[round(float(lo), 3), round(float(hi), 3)], se=round(se, 3),
                               binding_baseline="C" if pt["C"] >= pt["I"] else "I",
                               go=bool(point >= GO_POINT and lo > 0 and point >= GO_SE * se),
                               kill=bool(point <= KILL_POINT and hi < KILL_UPPER))
    cs = res["cells"].values()
    if any(c["go"] for c in cs):
        v = "GO"
    elif all(c["kill"] for c in cs):
        v = "KILL"
    else:
        v = "INCONCLUSIVE"
    res["verdict"] = v
    res["bootstrap"] = dict(B=n_boot, seed=seed, unit="tracklet (paired across arms)", ci="percentile 95%")
    return res


def main(argv):
    frames, bins_path, out = argv
    rows = list(csv.DictReader(open(frames)))
    bins = {(int(r["tid"]), int(r["k"])): r for r in csv.DictReader(open(bins_path))}
    res = decide(rows, bins)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({"verdict": res["verdict"], "cells": res["cells"]}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
