import numpy as np
import pytest

from ic001.geometry import Box, iou_3d, center_distance, points_in_box
from ic001.metrics import (success_auc, precision_auc, frame_success,
                           frame_precision, score_boxes)


def test_iou_identity_and_shift():
    b = Box((0, 0, 0), (2, 4, 2), 0.3)
    assert iou_3d(b, b) == pytest.approx(1.0)
    # shift along length by half the length -> BEV overlap 1/2 -> IoU 1/3
    b0 = Box((0, 0, 0), (2, 4, 2), 0.0)
    b1 = Box((2, 0, 0), (2, 4, 2), 0.0)
    assert iou_3d(b0, b1) == pytest.approx(1 / 3)
    # z shift by half height -> 1/3 as well
    b2 = Box((0, 0, 1), (2, 4, 2), 0.0)
    assert iou_3d(b0, b2) == pytest.approx(1 / 3)
    assert iou_3d(b0, Box((10, 0, 0), (2, 4, 2), 0.0)) == 0.0
    assert iou_3d(b0, b2, open3dsot_compat=False) == pytest.approx(1 / 3)
    # different heights: Open3DSOT quirk vs true overlap
    tall = Box((0, 0, 0), (2, 4, 4), 0.0)  # z in [-2, 2]
    up = Box((0, 0, 1), (2, 4, 2), 0.0)  # z in [0, 2]
    assert iou_3d(up, tall, open3dsot_compat=False) == pytest.approx(16 / 32)
    # Open3DSOT uses [c-h, c]: [-1, 1] vs [-4, 0] -> overlap 1 -> 8 / 40
    assert iou_3d(up, tall, open3dsot_compat=True) == pytest.approx(8 / 40)
    # 90 deg rotated square footprint box is identical
    s = Box((0, 0, 0), (2, 2, 2), 0.0)
    assert iou_3d(s, s.with_yaw(np.pi / 2)) == pytest.approx(1.0)


def test_center_distance_and_points_in_box():
    a, b = Box((0, 0, 0), (1, 1, 1), 0), Box((3, 4, 0), (1, 1, 1), 0)
    assert center_distance(a, b) == pytest.approx(5.0)
    box = Box((0, 0, 0), (2, 4, 2), np.pi / 2)  # length along y
    pts = np.array([[0, 1.9, 0], [1.9, 0, 0], [0, 0, 1.1]])
    assert points_in_box(pts, box).tolist() == [True, False, False]
    assert points_in_box(pts, box, bev_margin=1.0).tolist() == [True, True, False]


def test_transform_roundtrip():
    from ic001.geometry import rot_z
    T = np.eye(4); T[:3, :3] = rot_z(0.7); T[:3, 3] = [5, -2, 1]
    b = Box((1, 2, 3), (2, 4, 1.5), 0.2)
    b2 = b.transform(T).transform(np.linalg.inv(T))
    assert np.allclose(b2.c, b.c) and b2.yaw == pytest.approx(b.yaw)


def test_success_precision_auc():
    assert success_auc([1.0] * 5) == pytest.approx(100.0)
    # Open3DSOT uses IoU >= th, so th=0 always counts: all-zero IoU -> 2.5
    assert success_auc([0.0] * 5) == pytest.approx(2.5)
    assert precision_auc([0.0] * 5) == pytest.approx(100.0)
    assert precision_auc([5.0] * 5) == pytest.approx(0.0)
    # IoU 0.5 everywhere: curve 1 for th<=0.5 (11 pts), 0 after
    assert success_auc([0.5]) == pytest.approx(52.5)
    rng = np.random.default_rng(0)
    o, d = rng.uniform(0, 1, 200), rng.uniform(0, 3, 200)
    assert frame_success(o).mean() == pytest.approx(success_auc(o))
    assert frame_precision(d).mean() == pytest.approx(precision_auc(d))


def test_score_boxes():
    g = [Box((0, 0, 0), (2, 4, 2), 0)] * 3
    ious, dists = score_boxes(g, g)
    assert np.allclose(ious, 1) and np.allclose(dists, 0)
