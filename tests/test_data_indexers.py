"""Indexers on tiny SYNTHETIC files written to tmp_path (no real data)."""
import json
import os

import numpy as np
import pytest

from ic001.data.kitti import index_kitti, oxts_poses, label_to_velo_box
from ic001.data.nuscenes import index_nuscenes, val_scenes
from ic001.guard import require_frozen_prereg, PreregNotFrozen

CALIB = """P0: 1 0 0 0 0 1 0 0 0 0 1 0
R_rect 1 0 0 0 1 0 0 0 1
Tr_velo_cam 0 -1 0 0 0 0 -1 0 1 0 0 0
Tr_imu_velo 1 0 0 0 0 1 0 0 0 0 1 0
"""


def _write_kitti(root, n=4):
    for d in ["calib", "label_02", "oxts", "velodyne/0019"]:
        os.makedirs(os.path.join(root, d), exist_ok=True)
    open(os.path.join(root, "calib/0019.txt"), "w").write(CALIB)
    lines = []
    for f in range(n):
        # Car id 3 moving +1 m/frame in camera z (= velo x)
        lines.append(f"{f} 3 Car 0 0 0 0 0 10 10 1.5 1.8 4.2 0 1.6 {10 + f} 0")
        lines.append(f"{f} 7 Pedestrian 0 1 0 0 0 10 10 1.7 0.6 0.8 2 1.6 8 0")
        lines.append(f"{f} -1 DontCare -1 -1 -10 0 0 10 10 -1 -1 -1 -1000 -1000 -1000 -10")
    open(os.path.join(root, "label_02/0019.txt"), "w").write("\n".join(lines) + "\n")
    ox = [[49.0, 8.4 + 1e-5 * f, 100.0, 0, 0, 0] + [0] * 24 for f in range(n)]
    np.savetxt(os.path.join(root, "oxts/0019.txt"), np.array(ox))
    for f in range(n):
        np.zeros((10, 4), np.float32).tofile(os.path.join(root, f"velodyne/0019/{f:06d}.bin"))


def test_kitti_index_synthetic(tmp_path):
    root = str(tmp_path)
    _write_kitti(root)
    trs = index_kitti(root, scenes=[19], category="Car")
    assert len(trs) == 1 and len(trs[0]) == 4
    b = trs[0].frames[0].gt
    # camera (x=0, y=1.6-0.75, z=10) -> velo (10, 0, -0.85)
    assert np.allclose(b.c, [10, 0, -0.85])
    assert b.yaw == pytest.approx(-np.pi / 2)
    assert trs[0].frames[0].get_points().shape == (10, 3)
    assert len(index_kitti(root, scenes=[19], category="All")) == 2
    # oxts: pure eastward motion -> poses translate along +x
    P = oxts_poses(os.path.join(root, "oxts/0019.txt"))
    assert P[1, 0, 3] > 0 and abs(P[1, 1, 3]) < 1e-6


def test_nuscenes_index_synthetic(tmp_path):
    root = str(tmp_path); ver = "v1.0-trainval"
    os.makedirs(os.path.join(root, ver)); os.makedirs(os.path.join(root, "samples/LIDAR_TOP"))
    scene_name = val_scenes()[0]
    q = [1, 0, 0, 0]
    tabs = dict(
        category=[dict(token="c1", name="vehicle.car"), dict(token="c2", name="human.pedestrian.adult")],
        scene=[dict(token="sc", name=scene_name)],
        calibrated_sensor=[dict(token="cs", rotation=q, translation=[0, 0, 1.8])],
        ego_pose=[dict(token=f"e{i}", rotation=q, translation=[i, 0, 0]) for i in range(3)],
        sample=[dict(token=f"s{i}", scene_token="sc") for i in range(3)],
        sample_data=[dict(token=f"sd{i}", sample_token=f"s{i}", is_key_frame=True,
                          filename=f"samples/LIDAR_TOP/f{i}.pcd.bin", timestamp=i * 500000,
                          calibrated_sensor_token="cs", ego_pose_token=f"e{i}") for i in range(3)],
        sample_annotation=[dict(token=f"a{i}", sample_token=f"s{i}", translation=[10 + i, 0, 1],
                                size=[1.9, 4.5, 1.6], rotation=q, num_lidar_pts=30,
                                next=f"a{i+1}" if i < 2 else "") for i in range(3)],
        instance=[dict(token="i1", category_token="c1", first_annotation_token="a0")],
    )
    for k, v in tabs.items():
        json.dump(v, open(os.path.join(root, ver, k + ".json"), "w"))
    for i in range(3):
        np.array([[1, 0, 0, 0, 0]], np.float32).tofile(os.path.join(root, f"samples/LIDAR_TOP/f{i}.pcd.bin"))
    trs = index_nuscenes(root, "car")
    assert len(trs) == 1 and len(trs[0]) == 3
    f2 = trs[0].frames[2]
    assert np.allclose(f2.get_points(), [[3, 0, 1.8]])  # lidar -> ego -> global
    assert f2.timestamp == pytest.approx(1.0)
    assert index_nuscenes(root, "car", min_points=31) == []
    assert index_nuscenes(root, "pedestrian") == []


def test_mini_rejected(tmp_path):
    with pytest.raises(ValueError):
        index_nuscenes(str(tmp_path), "car", version="v1.0-mini")


def test_val_scene_list():
    v = val_scenes()
    assert len(v) == 150 and len(set(v)) == 150


def test_guard_blocks_without_prereg(tmp_path):
    with pytest.raises(PreregNotFrozen):
        require_frozen_prereg(str(tmp_path))


def test_cli_refuses_without_frozen_prereg(tmp_path):
    from ic001 import run
    with pytest.raises(PreregNotFrozen):
        run.main(["floor", "--dataset", "kitti", "--root", str(tmp_path),
                  "--out", str(tmp_path / "x.csv")])
