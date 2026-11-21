import numpy as np
import pytest

from ic001.metrics import score_boxes, success_auc
from ic001.trackers import (FloorConfig, track, nonground_in_box,
                            ground_filter_removed_fraction)
from ic001.geometry import Box
from synth import make_tracklet


def gts(tr):
    return [f.gt for f in tr.frames]


def test_last_box_exact_on_static_object():
    tr = make_tracklet(v=(0, 0, 0))
    preds, _ = track(tr, "last_box")
    ious, d = score_boxes(preds, gts(tr))
    assert np.allclose(ious, 1) and np.allclose(d, 0, atol=1e-9)


def test_cv_exact_on_constant_velocity_after_frame2():
    tr = make_tracklet(v=(1.0, 0.5, 0.0), yaw=0.3)
    preds, _ = track(tr, "cv", protocol="reinit")
    _, d = score_boxes(preds, gts(tr))
    assert np.allclose(d[2:], 0, atol=1e-9)
    assert d[1] == pytest.approx(np.hypot(1.0, 0.5))  # frame 2 = zero-velocity copy


def test_heading_always_from_previous_box():
    # PREREG choice k: never from velocity, even when fast
    tr = make_tracklet(v=(1.0, 0.5, 0.0), yaw=0.4)  # 11 m/s, moving off-axis
    for proto in ("ope", "reinit"):
        for m in ("last_box", "cv", "cv_snap"):
            preds, _ = track(tr, m, protocol=proto)
            assert all(p.yaw == pytest.approx(0.4) for p in preds)


def test_reinit_uses_previous_gt_size_and_yaw():
    from ic001.geometry import Box
    from ic001.tracklet import Frame, Tracklet
    fr = [Frame(gt=Box((t * 1.0, 0, 0), (1.8, 4.0 + 0.1 * t, 1.5), 0.1 * t),
                T_world_sensor=np.eye(4), timestamp=0.1 * t, points=np.zeros((0, 3)))
          for t in range(5)]
    tr = Tracklet("synthetic", "s", "Car", fr)
    p_re, _ = track(tr, "cv", protocol="reinit")
    for t in range(1, 5):
        assert p_re[t].size == fr[t - 1].gt.size  # choice j
        assert p_re[t].yaw == pytest.approx(fr[t - 1].gt.yaw)  # choice k
    p_ope, _ = track(tr, "cv", protocol="ope")
    assert all(p.size == fr[0].gt.size for p in p_ope)  # OPE keeps frame-1 size


def test_ope_cv_without_snap_degenerates_to_last_box():
    """DRAFT spec consequence (flagged as an open point): in OPE, frame 2 is a
    zero-velocity copy and velocity comes from the floor's OWN last two
    centres, so without snap the velocity stays 0 forever: control 2 (CV, no
    snap) == control 1 (last box) under protocol (a). They differ under (b)."""
    tr = make_tracklet(v=(1.0, 0.0, 0.0), yaw=0.0)
    p_last, _ = track(tr, "last_box")
    p_cv, _ = track(tr, "cv")
    for a, b in zip(p_last, p_cv):
        assert np.allclose(a.c, b.c) and a.yaw == pytest.approx(b.yaw)
    r_last, _ = track(tr, "last_box", protocol="reinit")
    r_cv, _ = track(tr, "cv", protocol="reinit")
    assert score_boxes(r_cv, gts(tr))[1][2:].max() < 1e-9
    assert score_boxes(r_last, gts(tr))[1][2:].min() > 0.99


def test_snap_recovers_lag():
    tr = make_tracklet(v=(1.0, 0.0, 0.0), yaw=0.0, n_pts=500)
    p_cv, _ = track(tr, "cv")
    p_snap, infos = track(tr, "cv_snap")
    d_cv = score_boxes(p_cv, gts(tr))[1]
    d_snap = score_boxes(p_snap, gts(tr))[1]
    assert d_snap[3:].mean() < 0.25 * d_cv[3:].mean()
    assert sum(i.snapped for i in infos) >= len(tr) - 2


def test_snap_skipped_without_points():
    tr = make_tracklet(v=(1.0, 0.0, 0.0), n_pts=0, ground=True)
    p_cv, _ = track(tr, "cv")
    p_snap, infos = track(tr, "cv_snap")
    assert not any(i.snapped for i in infos)  # ground points are filtered out
    for a, b in zip(p_cv, p_snap):
        assert np.allclose(a.c, b.c)


def test_ground_filter_fix_a():
    cfg = FloorConfig()
    box = Box((0, 0, 0.75), (2, 4, 1.5), 0.0)  # bottom at z=0
    pts = np.array([[0, 0, 0.0], [0, 0, 0.2], [0, 0, 0.26], [0, 0, 1.0], [2.4, 0, 1.0]])
    kept = nonground_in_box(pts, box, cfg)
    # 0.0 and 0.2 removed (<= 0.25 above bottom); 2.4 m along x is within 0.5 BEV margin
    assert kept.shape[0] == 3
    assert ground_filter_removed_fraction(pts, box, cfg) == pytest.approx(2 / 5)


def test_ego_compensation_matters():
    # static object, moving + turning ego: in sensor frame the object moves
    tr = make_tracklet(v=(0, 0, 0), ego_v=(1.0, 0.0, 0.0), ego_yaw_rate=0.02)
    p_ego, _ = track(tr, "last_box", cfg=FloorConfig(ego_comp=True))
    p_noego, _ = track(tr, "last_box", cfg=FloorConfig(ego_comp=False))
    d_ego = score_boxes(p_ego, gts(tr))[1]
    d_no = score_boxes(p_noego, gts(tr))[1]
    assert np.allclose(d_ego, 0, atol=1e-9)
    assert d_no[1:].mean() > 0.5


def test_determinism_v3():
    tr = make_tracklet(v=(0.8, 0.3, 0.0))
    a, _ = track(tr, "cv_snap")
    b, _ = track(tr, "cv_snap")
    assert all(np.array_equal(x.c, y.c) and x.yaw == y.yaw for x, y in zip(a, b))


def test_no_icp_variant():
    import ic001.trackers as T
    assert not hasattr(T, "track_icp_yaw")  # choice p: dropped


def test_frame1_size_fixed_and_frame0_is_gt():
    tr = make_tracklet()
    preds, _ = track(tr, "cv_snap")
    assert preds[0] == tr.frames[0].gt or np.allclose(preds[0].c, tr.frames[0].gt.c)
    assert all(tuple(p.size) == tuple(tr.frames[0].gt.size) for p in preds)


def test_bad_args():
    tr = make_tracklet(n=3)
    with pytest.raises(ValueError):
        track(tr, "kalman")
    with pytest.raises(ValueError):
        track(tr, "cv", protocol="x")
