"""Tests for the SOT-M2 Stage 1 helpers (numpy only)."""
import csv, io
import numpy as np
import pytest
from pyquaternion import Quaternion

from gpu_jobs.sotm2 import geom, select_scenes, decide
from ic001.metrics import success_auc, precision_auc


def _box(c, yaw, wlh=(2.0, 4.0, 1.5)):
    return (np.array(c, float), np.array(wlh, float), Quaternion(axis=[0, 0, 1], angle=yaw).elements)


def test_interp_endpoints_and_midpoint():
    a, b = _box([0, 0, 0], 0.0), _box([2, 4, 0], np.pi / 2)
    c0, w0, q0 = geom.interp_box(a[0], a[2], a[1], b[0], b[2], 0.0)
    c1, _, q1 = geom.interp_box(a[0], a[2], a[1], b[0], b[2], 1.0)
    cm, wm, qm = geom.interp_box(a[0], a[2], a[1], b[0], b[2], 0.5)
    assert np.allclose(c0, a[0]) and np.allclose(c1, b[0]) and np.allclose(cm, [1, 2, 0])
    assert np.allclose(wm, a[1])
    assert abs(Quaternion(qm).yaw_pitch_roll[0] - np.pi / 4) < 1e-9
    assert abs(abs(np.dot(q1, b[2])) - 1) < 1e-9


def test_crop_and_region():
    c, wlh, q = _box([10, 0, 0], 0.0)
    p = np.array([[10, 0, 0], [16.9, 0, 0], [17.1, 0, 0], [10, 3.0, 0]], float).T
    kept = geom.crop_axis_aligned(p, c, wlh, q, offset=5.0)  # x bound 10+2+5 = 17
    assert kept.shape[1] == 3
    m = geom.in_region(p, c, wlh, q, scale=1.25, offset=2.0)  # half x = 4*1.25/2+2 = 4.5, half y = 3.25
    assert m.tolist() == [True, False, False, True]


def test_align_roundtrip_and_rigid():
    rng = np.random.default_rng(1)
    p = rng.normal(size=(3, 50))
    s, d = _box([1, 2, 0], 0.3), _box([-4, 7, 1], -1.1)
    q = geom.align(p, s[0], s[2], d[0], d[2])
    back = geom.align(q, d[0], d[2], s[0], s[2])
    assert np.allclose(back, p)
    assert np.allclose(np.linalg.norm(p[:, 0] - p[:, 1]), np.linalg.norm(q[:, 0] - q[:, 1]))


def test_buffer_points_moving_target_is_aligned():
    # a target moving +1 m/sweep in x: D aligns all past target points onto the current box, C smears them
    boxes = [_box([float(j), 0, 0], 0.0) for j in range(12)]
    sweeps = [np.array([[float(j)], [0.0], [0.0]]) for j in range(12)]
    D = geom.buffer_points(sweeps, 11, 0, boxes, 10, 1.25, 2.0, aligned=True)
    C = geom.buffer_points(sweeps, 11, 0, boxes, 10, 1.25, 2.0, aligned=False)
    assert D.shape[1] == 10 and C.shape[1] == 10
    assert np.allclose(D[0], 11.0)
    assert sorted(C[0].tolist()) == [float(j) for j in range(2, 12)]
    # never before the first keyframe
    assert geom.buffer_points(sweeps, 3, 2, boxes, 10, 1.25, 2.0, True).shape[1] == 2


def test_rank_is_deterministic_and_pick_rules():
    names = [f"scene-{i:04d}" for i in range(100)]
    r1 = select_scenes.rank(names[::-1]); r2 = select_scenes.rank(names)
    assert r1 == r2 and sorted(r1) == names and r1 != names
    complete = set(r1[::2])
    chosen = select_scenes.pick(r1, complete, n_target=40, n_min=30)
    assert len(chosen) == 40 and all(c in complete for c in chosen)
    assert chosen == [s for s in r1 if s in complete][:40]
    with pytest.raises(SystemExit):
        select_scenes.pick(r1, set(r1[:10]), n_target=40, n_min=30)


def test_committed_rank_file_matches_rule():
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tt = select_scenes._read(os.path.join(root, "data_manifest/nuscenes_train_track_scenes.txt"))
    rk = select_scenes._read(os.path.join(root, "data_manifest/sotm2_stage1_train_track_rank.txt"))
    assert len(tt) == 350 and rk == select_scenes.rank(tt)


def _synthetic(delta_d, n_trk=60, n_k=12, seed=3):
    rng = np.random.default_rng(seed)
    rows, bins = [], {}
    for t in range(n_trk):
        base = rng.uniform(0.2, 0.8)
        for k in range(n_k):
            bins[(t, k)] = {"moving": str(int(k % 2 == 0)), "pts_lt10": str(int(k % 3 != 0))}
            for arm, shift in (("C", 0.0), ("I", -0.02), ("D", delta_d), ("A", -0.05)):
                iou = 1.0 if k == 0 else float(np.clip(base + shift + rng.normal(0, 0.05), 0, 1))
                dist = 0.0 if k == 0 else float(abs(rng.normal(0.5 - shift, 0.1)))
                rows.append(dict(tid=t, k=k, arm=arm, iou=iou, dist=dist))
    return rows, bins


def test_decide_success_matches_ic001_metric():
    rows, bins = _synthetic(0.0)
    res = decide.decide(rows, bins, n_boot=200)
    sel = [r for r in rows if r["arm"] == "C" and r["k"] != 0 and bins[(r["tid"], r["k"])]["pts_lt10"] == "1"]
    assert abs(res["per_arm"]["C"]["pts_lt10"]["success"] - success_auc([r["iou"] for r in sel])) < 1e-3
    assert abs(res["per_arm"]["C"]["pts_lt10"]["precision"] - precision_auc([r["dist"] for r in sel])) < 1e-3


@pytest.mark.parametrize("delta,verdict", [(0.10, "GO"), (-0.05, "KILL"), (0.012, "INCONCLUSIVE")])
def test_decide_verdicts(delta, verdict):
    rows, bins = _synthetic(delta)
    res = decide.decide(rows, bins, n_boot=500)
    assert res["verdict"] == verdict, res["cells"]


def test_decide_max_inside_resample_is_conservative():
    rows, bins = _synthetic(0.05)
    r = decide.decide(rows, bins, n_boot=500)["cells"]["pts_lt10"]
    assert r["binding_baseline"] == "C" and r["ci95"][0] <= r["point"] <= r["ci95"][1]
