"""KITTI yaw-convention helper for per-frame dumps converted camera -> velodyne.

Some dump harnesses convert a KITTI camera-frame box to the velodyne frame by
rotating the full box orientation with the rotation block ``A`` of
``inv(Tr_velo_cam)`` and reading the yaw of the rotated length axis::

    yaw_axis = atan2((A @ d)[1], (A @ d)[0]),   d = (cos ry, 0, -sin ry)

where ``ry`` is the camera ``rotation_y`` of the box (KITTI / Open3DSOT boxes
are a rotation about the camera y axis). The ic001 GT (and Open3DSOT) instead
use ``yaw_gt = -(ry + pi/2)``. Because ``A`` is not an exact axis permutation,
the two differ by up to ~8e-3 rad.

``axis_yaw_to_gt_yaw`` inverts the harness formula in closed form to recover
``ry`` from ``yaw_axis`` and the calibration only (no GT, no scores), then
returns the GT-convention yaw. This is the same quantity the MBPTrack
"GT-convention yaw" rescore derived from the raw camera quaternion.
"""
from __future__ import annotations

import math

import numpy as np

from .geometry import wrap_angle


def velo_rotation_block(velo_to_cam: np.ndarray) -> np.ndarray:
    """Rotation block of inv(Tr_velo_cam) (velo_to_cam is 3x4 or 4x4)."""
    m = np.asarray(velo_to_cam, dtype=float)
    if m.shape == (3, 4):
        m = np.vstack([m, [0.0, 0.0, 0.0, 1.0]])
    return np.linalg.inv(m)[:3, :3]


def axis_yaw_from_ry(ry: float, A: np.ndarray) -> float:
    """Forward harness formula (for tests): yaw of A @ (cos ry, 0, -sin ry)."""
    v = A @ np.array([math.cos(ry), 0.0, -math.sin(ry)])
    return float(math.atan2(v[1], v[0]))


def ry_from_axis_yaw(yaw_axis: float, A: np.ndarray) -> float:
    """Closed-form inverse of ``axis_yaw_from_ry``."""
    a0, a2 = A[:, 0], A[:, 2]
    cf, sf = math.cos(yaw_axis), math.sin(yaw_axis)
    num = a0[1] * cf - a0[0] * sf
    den = a2[1] * cf - a2[0] * sf
    ry = math.atan2(num, den)  # one of the two solutions (mod pi)
    v = math.cos(ry) * a0 - math.sin(ry) * a2
    if v[0] * cf + v[1] * sf < 0:  # wrong half-turn: flip
        ry += math.pi
    return wrap_angle(ry)


def axis_yaw_to_gt_yaw(yaw_axis: float, A: np.ndarray) -> float:
    """Harness length-axis yaw -> ic001 GT-convention yaw -(ry + pi/2)."""
    return wrap_angle(-(ry_from_axis_yaw(yaw_axis, A) + math.pi / 2.0))
