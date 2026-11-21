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
    assert ope["success"]["overall_incl_frame0"]["oracle"] >= 97.5
    assert np.isclose(ope["precision"]["overall_incl_frame0"]["oracle"], 100.0)
    ov = ope["success"]["overall_incl_frame0"]
    assert "cv" not in ov  # choice d: CV control not reported under OPE
    assert "cv" in rep["protocols"]["reinit"]["success"]["overall_incl_frame0"]
    assert all(v["best_family"] == "oracle" and v["gap"] >= 0
               for v in ope["gap_vs_floor_primary"].values())
    assert rep["n_frames_total"] == 6 * 12 and rep["n_frames_binned"] == 6 * 11  # choice g
    assert ope["success"]["overall_incl_frame0"]["n_frames"] == 72
    assert any(k.startswith("pts:") for k in ope["success"]) and "mot:motLo" in ope["success"]
    assert ope["R_secondary_floor_to_best_learned"]["late"] == "oracle"


def test_shards_merge_to_identical_output(tmp_path, monkeypatch):
    import subprocess, sys, os
    fresh = lambda: [make_tracklet(n=6, v=(0.2 * k, 0, 0), tid=f"0019_{k}", seed=k) for k in range(5)]
    monkeypatch.setattr(run, "require_frozen_prereg", lambda: "synthetic")
    monkeypatch.setattr(run, "_index", lambda a: (fresh(), KITTI_BINS))  # cmd_floor frees points
    full = tmp_path / "full.csv"
    run.main(["floor", "--dataset", "kitti", "--root", "x", "--out", str(full)])
    parts = []
    for k in range(3):
        p = tmp_path / f"s{k}.csv"; parts.append(str(p))
        run.main(["floor", "--dataset", "kitti", "--root", "x", "--out", str(p), "--shard", f"{k}/3"])
    merged = tmp_path / "merged.csv"
    script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "merge_shards.py")
    subprocess.run([sys.executable, script, str(merged), *parts], check=True)
    assert merged.read_bytes() == full.read_bytes()
