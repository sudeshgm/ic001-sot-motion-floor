"""KITTI tracking indexer for the Open3DSOT protocol (test split = scenes 0019-0020).

Expected layout (same as Open3DSOT, plus oxts for ego-compensation)::

    root/velodyne/0019/000000.bin   root/label_02/0019.txt
    root/calib/0019.txt             root/oxts/0019.txt

Box conversion copies Open3DSOT ``kittiDataset._get_frame_from_anno`` in
'velodyne' mode (centre = camera-frame label centre raised by h/2, mapped with
inv(Tr_velo_cam); R_rect is ignored exactly as Open3DSOT does), so GT boxes
match what the learned trackers are scored against.
"""
from __future__ import annotations

import os
from collections import OrderedDict
from typing import Dict, List, Sequence

import numpy as np

from ..geometry import Box, wrap_angle
from ..tracklet import Frame, Tracklet

OPEN3DSOT_SPLITS = {
    "train": list(range(0, 17)),
    "valid": list(range(17, 19)),
    "test": list(range(19, 21)),
}
LABEL_COLS = ["frame", "track_id", "type", "truncated", "occluded", "alpha",
              "bbox_left", "bbox_top", "bbox_right", "bbox_bottom",
              "height", "width", "length", "x", "y", "z", "rotation_y"]
KITTI_DT = 0.1  # 10 Hz; tracking release has no per-frame timestamps


def read_calib(path: str) -> Dict[str, np.ndarray]:
    out = {}
    with open(path) as f:
        for line in f:
            vals = line.replace(":", " ").split()
            if not vals:
                continue
            try:
                arr = np.array([float(x) for x in vals[1:]])
            except ValueError:
                continue
            if arr.size == 12:
                out[vals[0]] = arr.reshape(3, 4)
            elif arr.size == 9:
                out[vals[0]] = arr.reshape(3, 3)
    return out


def _h(m34: np.ndarray) -> np.ndarray:
    return np.vstack([m34, [0, 0, 0, 1]])


def read_labels(path: str) -> List[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            v = line.split()
            if len(v) < 17:
                continue
            r = dict(zip(LABEL_COLS, v[:17]))
            for k in LABEL_COLS:
                if k != "type":
                    r[k] = float(r[k])
            r["frame"] = int(r["frame"]); r["track_id"] = int(r["track_id"])
            r["occluded"] = int(r["occluded"])
            rows.append(r)
    return rows


def oxts_poses(path: str) -> np.ndarray:
    """KITTI devkit ``convertOxtsToPose``: (F, 4, 4) IMU->world, Mercator
    projection with the scale of the first frame, first pose NOT normalised
    (only relative motion matters for the floor)."""
    data = np.loadtxt(path, ndmin=2)
    lat, lon, alt = data[:, 0], data[:, 1], data[:, 2]
    roll, pitch, yaw = data[:, 3], data[:, 4], data[:, 5]
    er = 6378137.0
    scale = np.cos(lat[0] * np.pi / 180.0)
    tx = scale * lon * np.pi * er / 180.0
    ty = scale * er * np.log(np.tan((90.0 + lat) * np.pi / 360.0))
    poses = np.zeros((len(data), 4, 4))
    for i in range(len(data)):
        cr, sr = np.cos(roll[i]), np.sin(roll[i])
        cp, sp = np.cos(pitch[i]), np.sin(pitch[i])
        cy, sy = np.cos(yaw[i]), np.sin(yaw[i])
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
        poses[i, :3, :3] = Rz @ Ry @ Rx
        poses[i, :3, 3] = [tx[i], ty[i], alt[i]]
        poses[i, 3, 3] = 1.0
    poses[:, :3, 3] -= poses[0, :3, 3]  # keep numbers small; rigid shift only
    return poses


def label_to_velo_box(r: dict, velo_to_cam: np.ndarray) -> Box:
    c_cam = np.array([r["x"], r["y"] - r["height"] / 2.0, r["z"], 1.0])
    c_velo = (np.linalg.inv(velo_to_cam) @ c_cam)[:3]
    # Open3DSOT: Quaternion(axis=[0,0,-1], rad=ry) * Quaternion(axis=[0,0,-1], 90deg)
    yaw = wrap_angle(-(r["rotation_y"] + np.pi / 2.0))
    return Box(tuple(c_velo), (r["width"], r["length"], r["height"]), yaw)


def _velo_loader(path: str):
    def load():
        if not os.path.isfile(path):  # Open3DSOT tolerates missing scans
            return np.zeros((0, 3))
        return np.fromfile(path, dtype=np.float32).reshape(-1, 4)[:, :3].astype(float)
    return load


def index_kitti(root: str, split: str = "test", category: str = "Car",
                scenes: Sequence[int] | None = None,
                require_oxts: bool = True) -> List[Tracklet]:
    """Build Open3DSOT-ordered tracklets (scene, then track id in order of first
    appearance, as pandas ``unique()``). Points load lazily."""
    scenes = scenes if scenes is not None else OPEN3DSOT_SPLITS[split]
    cats = {"All": {"Car", "Van", "Pedestrian", "Cyclist"}}.get(category, {category})
    out: List[Tracklet] = []
    for s in scenes:
        sn = f"{s:04d}"
        calib = read_calib(os.path.join(root, "calib", sn + ".txt"))
        velo_to_cam = _h(calib["Tr_velo_cam"])
        oxts_path = os.path.join(root, "oxts", sn + ".txt")
        if os.path.isfile(oxts_path):
            imu_to_velo = _h(calib["Tr_imu_velo"])
            T_world_imu = oxts_poses(oxts_path)
            T_world_velo = T_world_imu @ np.linalg.inv(imu_to_velo)
        elif require_oxts:
            raise FileNotFoundError(oxts_path)
        else:
            T_world_velo = None
        rows = [r for r in read_labels(os.path.join(root, "label_02", sn + ".txt"))
                if r["type"] in cats]
        by_track: "OrderedDict[int, list]" = OrderedDict()
        for r in rows:
            by_track.setdefault(r["track_id"], []).append(r)
        for tid, rs in by_track.items():
            rs = sorted(rs, key=lambda r: r["frame"])
            frames = []
            for r in rs:
                fid = r["frame"]
                T = T_world_velo[fid] if T_world_velo is not None else np.eye(4)
                frames.append(Frame(
                    gt=label_to_velo_box(r, velo_to_cam), T_world_sensor=T,
                    timestamp=fid * KITTI_DT,
                    load_points=_velo_loader(os.path.join(root, "velodyne", sn, f"{fid:06d}.bin")),
                    meta=dict(scene=sn, frame=fid, occluded=r["occluded"],
                              truncated=r["truncated"], type=r["type"])))
            out.append(Tracklet("kitti", f"{sn}_{tid}", rs[0]["type"], frames,
                                meta=dict(scene=sn, track_id=tid)))
    return out
