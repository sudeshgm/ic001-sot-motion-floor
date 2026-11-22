"""CPU unit tests for gpu_jobs/dump_trackany3d.py helpers (no tracker / no GPU)."""
import importlib.util
import os

import numpy as np
import pytest

_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "gpu_jobs",
    "dump_trackany3d.py",
)


def _load():
    spec = importlib.util.spec_from_file_location("dump_trackany3d", _PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_import_does_not_pull_torch():
    import sys
    before = {k for k in sys.modules if k == "torch" or k.startswith("torch.")}
    _load()
    after = {k for k in sys.modules if k == "torch" or k.startswith("torch.")}
    assert after == before


def test_csv_schema_and_method():
    m = _load()
    assert m.FIELDS == [
        "dataset", "category", "tracklet_id", "frame_idx", "protocol", "method",
        "cx", "cy", "cz", "w", "l", "h", "yaw",
    ]
    assert m.METHOD == "trackany3d"


def test_wrap_angle():
    m = _load()
    assert m._wrap(0.0) == pytest.approx(0.0)
    assert m._wrap(np.pi) == pytest.approx(-np.pi) or m._wrap(np.pi) == pytest.approx(np.pi)
    assert m._wrap(np.pi + 0.2) == pytest.approx(-np.pi + 0.2)
    assert m._wrap(-np.pi - 0.2) == pytest.approx(np.pi - 0.2)


class _Ori:
    def __init__(self, yaw):
        c, s = np.cos(yaw), np.sin(yaw)
        self.rotation_matrix = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        self.yaw_pitch_roll = (yaw, 0.0, 0.0)


class _Box:
    def __init__(self, center, wlh, yaw):
        self.center = np.asarray(center, dtype=float)
        self.wlh = np.asarray(wlh, dtype=float)
        self.orientation = _Ori(yaw)


def test_cam_box_to_velo_identity():
    m = _load()
    T = np.eye(4)
    box = _Box((1.0, 2.0, 3.0), (1.5, 4.0, 1.6), 0.3)
    c, wlh, yaw = m.cam_box_to_velo(box, T)
    assert c == pytest.approx([1.0, 2.0, 3.0])
    assert np.allclose(wlh, [1.5, 4.0, 1.6])
    assert yaw == pytest.approx(0.3)


def test_velo_gt_identity_and_yaw():
    m = _load()
    T = np.eye(4)
    # KITTI camera bottom-centre (x, y, z); velo_gt lifts y by height/2
    anno = dict(x=1.0, y=2.0, z=3.0, height=1.6, rotation_y=0.2)
    c, yaw = m.velo_gt(anno, T)
    assert c == pytest.approx([1.0, 2.0 - 0.8, 3.0])
    expected = -(0.2 + np.pi / 2)
    assert yaw == pytest.approx((expected + np.pi) % (2 * np.pi) - np.pi)


def test_global_box_yaw():
    m = _load()
    box = _Box((10.0, -2.0, 0.5), (2.0, 5.0, 1.8), -0.7)
    c, wlh, yaw = m.global_box(box)
    assert c == pytest.approx([10.0, -2.0, 0.5])
    assert np.allclose(wlh, [2.0, 5.0, 1.8])
    assert yaw == pytest.approx(-0.7)
