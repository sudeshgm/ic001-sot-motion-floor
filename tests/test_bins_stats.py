import numpy as np
import pytest

from ic001.bins import (KITTI_BINS, NUSCENES_BINS, assign_bins, gt_motion,
                        gt_point_counts, needs_merge, tracklet_tertile_edges)
from ic001.stats import (FrameTable, per_cell, bootstrap_gap, concentration_ratio,
                         bootstrap_concentration, decide_first_test)
from synth import make_tracklet


def test_point_bins_edges():
    assert [KITTI_BINS.point_bin(x) for x in (0, 49, 50, 199, 200)] == [0, 0, 1, 1, 2]
    assert [NUSCENES_BINS.point_bin(x) for x in (9, 10, 24, 25)] == [0, 1, 1, 2]


def test_assign_bins_and_hard():
    n = np.array([10, 100, 300, 300])
    m = np.array([np.nan, 0.1, 0.1, 0.6])
    fb = assign_bins(n, m, KITTI_BINS)
    assert fb.point_bin.tolist() == [0, 1, 2, 2]
    assert fb.high_motion.tolist() == [False, False, False, True]
    assert fb.hard.tolist() == [True, False, False, True]


def test_gt_counts_and_motion_world_frame():
    tr = make_tracklet(n=5, v=(0.6, 0, 0), ego_v=(1.0, 0, 0), n_pts=120, ground=False)
    assert np.all(gt_point_counts(tr) == 120)
    m = gt_motion(tr)
    assert np.isnan(m[0]) and np.allclose(m[1:], 0.6)


def test_merge_and_tertiles():
    labels = ["a"] * 40 + ["b"] * 5
    tids = list(range(40)) + list(range(5))
    assert needs_merge(labels, tids)
    lo, hi = tracklet_tertile_edges(np.arange(1, 10))
    assert lo < hi


def _table(n_trk=60, frames=20, gap_easy=2.0, gap_hard=20.0, seed=0):
    rng = np.random.default_rng(seed)
    tr, cell, hard, f, l1, l2 = [], [], [], [], [], []
    for t in range(n_trk):
        for k in range(frames):
            h = k % 4 == 0
            base = rng.normal(60, 10)
            tr.append(t); cell.append("hard" if h else "easy"); hard.append(h)
            f.append(base)
            l1.append(base + (gap_hard if h else gap_easy) + rng.normal(0, 2))
            l2.append(base + rng.normal(0, 2))
    return FrameTable(np.array(tr), np.array(cell), np.array(hard),
                      dict(floor=np.array(f), m2=np.array(l1), mbp=np.array(l2)))


def test_bootstrap_gap_and_best_family():
    tab = _table()
    res = bootstrap_gap(tab, ["m2", "mbp"], "floor", n_boot=500, seed=0)
    assert res["hard"]["best_family"] == "m2"
    assert res["hard"]["gap"] == pytest.approx(20, abs=1.5)
    assert res["hard"]["lo"] > 15 and res["easy"]["hi"] < 5
    # reproducible with fixed seed
    res2 = bootstrap_gap(tab, ["m2", "mbp"], "floor", n_boot=500, seed=0)
    assert res == res2


def test_concentration_ratio():
    tab = _table(gap_easy=0.0, gap_hard=20.0)
    # all gain in hard frames (25% of frames) -> R = 1/0.25 = 4
    r = concentration_ratio(tab, "floor", "m2")
    assert r == pytest.approx(4.0, rel=0.1)
    b = bootstrap_concentration(tab, "floor", "m2", n_boot=300)
    assert b["P5_supported"] and b["lo"] > 1.0
    # uniform gain -> R ~ 1, not supported
    tab2 = _table(gap_easy=10.0, gap_hard=10.0)
    assert bootstrap_concentration(tab2, "floor", "m2", n_boot=300)["P5_supported"] is False
    # gain <= 2 Success -> undefined
    assert concentration_ratio(tab, "floor", "mbp") is None


def _cell(gap, lo, hi, share, ntr=40):
    return dict(gap=gap, lo=lo, hi=hi, frame_share=share, n_tracklets=ntr)


def test_decision_rule():
    big = {"a": _cell(15, 8, 20, 0.6), "b": _cell(12, 6, 18, 0.4)}
    assert decide_first_test({"kitti": big, "nuscenes": big}) == "KILL"
    go = {"a": _cell(3, 0, 7, 0.5), "b": _cell(15, 8, 20, 0.5)}
    assert decide_first_test({"kitti": go, "nuscenes": go}) == "GO"
    assert decide_first_test({"kitti": go, "nuscenes": big}) == "GO"  # KITTI bin >=40%
    small_go = {"a": _cell(3, 0, 7, 0.25), "b": _cell(15, 8, 20, 0.75)}
    assert decide_first_test({"kitti": small_go, "nuscenes": big}) == "INCONCLUSIVE"
    # under-powered cells cannot drive a decision
    weak = {"a": _cell(15, 8, 20, 1.0, ntr=10)}
    assert decide_first_test({"kitti": weak, "nuscenes": weak}) == "INCONCLUSIVE"
    # KITTI-only can never KILL
    assert decide_first_test({"kitti": big}) == "INCONCLUSIVE"
