import numpy as np
import pytest

from ic001.geometry import (Box, compensate_box, compensate_points,
                            relative_sensor_transform, rot_z, wrap_angle)


def _T(R=None, t=(0, 0, 0)):
    T = np.eye(4)
    if R is not None:
        T[:3, :3] = R
    T[:3, 3] = t
    return T


def test_identity_leaves_box_and_points_unchanged():
    b = Box((3.0, -1.0, 0.5), (1.8, 4.2, 1.5), 0.4)
    I = np.eye(4)
    out = compensate_box(b, I, I)
    assert np.allclose(out.c, b.c) and out.yaw == pytest.approx(b.yaw)
    assert out.size == b.size
    pts = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0]])
    assert np.allclose(compensate_points(pts, I, I), pts)


def test_ego_translation_shifts_static_box_by_minus_translation():
    # Ego moves +5 m along +x; a static world object must appear 5 m closer.
    T0, T1 = _T(t=(0, 0, 0)), _T(t=(5, 0, 0))
    b = Box((20.0, 1.0, 0.0), (2.0, 4.0, 1.6), 0.2)
    out = compensate_box(b, T0, T1)
    assert np.allclose(out.c, [15.0, 1.0, 0.0])
    assert out.yaw == pytest.approx(b.yaw)
    assert out.size == b.size
    pts = np.array([[20.0, 1.0, 0.0]])
    assert np.allclose(compensate_points(pts, T0, T1), [[15.0, 1.0, 0.0]])


def test_ego_yaw_rotates_centre_and_adds_yaw():
    # Ego yaws +90 deg in place. A box at (1, 0, 0), yaw 0, maps by
    # inv(R_z(pi/2)) = R_z(-pi/2) to (0, -1, 0), yaw -pi/2.
    T0, T1 = np.eye(4), _T(R=rot_z(np.pi / 2))
    b = Box((1.0, 0.0, 0.0), (2.0, 4.0, 1.6), 0.0)
    out = compensate_box(b, T0, T1)
    assert np.allclose(out.c, [0.0, -1.0, 0.0])
    assert out.yaw == pytest.approx(-np.pi / 2)
    assert np.allclose(compensate_points(np.array([[1.0, 0.0, 0.0]]), T0, T1),
                       [[0.0, -1.0, 0.0]])


def test_pitch_uses_full_centre_transform_but_yaw_only_orientation():
    # Pure pitch about +y: dyaw = atan2(T[1,0], T[0,0]) == 0; box stays upright.
    pitch = 0.4
    c, s = np.cos(pitch), np.sin(pitch)
    Rp = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
    T0, T1 = np.eye(4), _T(R=Rp, t=(2.0, 0.0, 0.0))
    b = Box((3.0, 1.0, 0.5), (2.0, 4.0, 1.6), 0.3)
    T_rel = relative_sensor_transform(T0, T1)
    out = compensate_box(b, T0, T1)
    expected_c = T_rel[:3, :3] @ b.c + T_rel[:3, 3]
    assert np.allclose(out.c, expected_c)
    assert out.yaw == pytest.approx(b.yaw)  # no yaw component in a pure pitch
    # A full rotation would tilt the box; we only keep yaw (choice o).
    dyaw = np.arctan2(T_rel[1, 0], T_rel[0, 0])
    assert dyaw == pytest.approx(0.0, abs=1e-12)
    assert out.size == b.size
    # points take the full (pitched) rigid map, same as the centre
    pts = compensate_points(np.array([b.c]), T0, T1)
    assert np.allclose(pts[0], expected_c)


def test_world_invariance_and_matches_box_transform():
    # Compensating then mapping to world equals mapping the original to world.
    T_from = _T(R=rot_z(-0.3), t=(1.0, -2.0, 0.2))
    pitch = 0.15
    c, s = np.cos(pitch), np.sin(pitch)
    Rp = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
    T_to = _T(R=rot_z(0.5) @ Rp, t=(4.0, 1.0, -0.1))
    b = Box((8.0, -3.0, 1.2), (1.9, 4.5, 1.6), -0.8)
    out = compensate_box(b, T_from, T_to)
    assert out.yaw == pytest.approx(
        b.transform(relative_sensor_transform(T_from, T_to)).yaw)
    assert np.allclose(out.c, b.transform(relative_sensor_transform(T_from, T_to)).c)
    # World centres agree even when T_to has pitch (full centre transform).
    assert np.allclose(out.transform(T_to).c, b.transform(T_from).c)
    # Empty point cloud is a (0, 3) array, not an error
    empty = compensate_points(np.zeros((0, 3)), T_from, T_to)
    assert empty.shape == (0, 3)
