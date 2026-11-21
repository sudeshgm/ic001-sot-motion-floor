"""End-to-end floor -> evaluate on SYNTHETIC tracklets, guard monkeypatched."""
import csv
import json

import numpy as np

from ic001 import run
from ic001.bins import KITTI_BINS
from synth import make_tracklet


def test_floor_and_evaluate_synthetic(tmp_path, monkeypatch):
    trs = [make_tracklet(n=12, v=(0.3 * (k % 3), 0.1, 0), tid=f"0019_{k}", seed=k,
                         n_pts=30 if k % 2 else 300) for k in range(6)]
    monkeypatch.setattr(run, "require_frozen_prereg", lambda: "synthetic")
    monkeypatch.setattr(run, "_index", lambda a: (trs, KITTI_BINS))
    floor = tmp_path / "floor.csv"
    run.main(["floor", "--dataset", "kitti", "--root", "x", "--out", str(floor)])
    # fake "learned" tracker = GT boxes, in the GPU-job return format
    learned = tmp_path / "learned.csv"
    with open(learned, "w", newline="") as f:
        w = csv.writer(f); w.writerow(run.FIELDS)
        for tr in trs:
            for proto in ("ope", "reinit"):
                for i, fr in enumerate(tr.frames):
                    w.writerow(["kitti", "Car", tr.tracklet_id, i, proto, "oracle",
                                *fr.gt.center, *fr.gt.size, fr.gt.yaw])
    out = tmp_path / "eval.json"
    run.main(["evaluate", "--dataset", "kitti", "--root", "x", "--floor", str(floor),
              "--learned", str(learned), "--out", str(out), "--n-boot", "200"])
    rep = json.load(open(out))
    ope = rep["protocols"]["ope"]
    # identical boxes can give IoU = 1 - 1e-16 (shapely), missing th = 1.0 as in Open3DSOT
    assert ope["overall_success"]["oracle"] >= 97.5
    assert np.isclose(ope["overall_precision"]["oracle"], 100.0)
    assert set(ope["overall_success"]) == {"last_box", "cv", "cv_snap", "cv_snap_noego", "oracle"}
    assert all(v["best_family"] == "oracle" and v["gap"] >= 0 for v in ope["gap_vs_floor"].values())
    assert rep["n_frames"] == 6 * 11  # frame 0 excluded from per-bin analysis by default
