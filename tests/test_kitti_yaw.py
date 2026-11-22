import math

import numpy as np

from ic001.geometry import wrap_angle
from ic001.kitti_yaw import (
    axis_yaw_from_ry,
    axis_yaw_to_gt_yaw,
    ry_from_axis_yaw,
    velo_rotation_block,
)

# Tr_velo_cam of KITTI tracking training calib 0019 (near axis permutation, small tilt).
TR = np.array([
    [7.755449e-03, -9.999694e-01, -1.014303e-03, -7.275538e-03],
    [2.294056e-03, 1.032122e-03, -9.999968e-01, -6.324057e-02],
    [9.999673e-01, 7.753097e-03, 2.301990e-03, -2.670414e-01],
])


def test_rotation_block_inverse():
    A = velo_rotation_block(TR)
    full = np.vstack([TR, [0, 0, 0, 1]])
    assert np.allclose(A @ full[:3, :3], np.eye(3), atol=1e-6)


def test_roundtrip_ry():
    A = velo_rotation_block(TR)
    for ry in np.linspace(-math.pi + 1e-3, math.pi - 1e-3, 721):
        f = axis_yaw_from_ry(float(ry), A)
        back = ry_from_axis_yaw(f, A)
        assert abs(wrap_angle(back - ry)) < 1e-10


def test_gt_convention_and_offset_size():
    A = velo_rotation_block(TR)
    worst = 0.0
    for ry in np.linspace(-3.1, 3.1, 301):
        f = axis_yaw_from_ry(float(ry), A)
        gt = wrap_angle(-(ry + math.pi / 2))
        assert abs(wrap_angle(axis_yaw_to_gt_yaw(f, A) - gt)) < 1e-10
        worst = max(worst, abs(wrap_angle(f - gt)))
    # the uncorrected axis yaw differs from the GT convention by a few mrad
    assert 1e-3 < worst < 2e-2


def test_ideal_permutation_is_identity():
    # exact KITTI axis permutation: correction is a no-op
    P = np.array([[0, -1, 0, 0], [0, 0, -1, 0], [1, 0, 0, 0]], float)
    A = velo_rotation_block(P)
    for ry in (-2.0, -0.3, 0.0, 1.1, 3.0):
        f = axis_yaw_from_ry(ry, A)
        assert abs(wrap_angle(f - axis_yaw_to_gt_yaw(f, A))) < 1e-12
