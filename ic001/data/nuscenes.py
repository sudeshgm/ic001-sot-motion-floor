"""nuScenes v1.0-trainval val-split indexer (keyframes, LIDAR_TOP only),
following Open3DSOT ``NuScenesDataset`` (points and boxes in the global
frame, so ``T_world_sensor`` = identity and scoring matches Open3DSOT).

Reads the JSON tables directly (no nuscenes-devkit: its pins do not build on
Python 3.13). The val scene list is copied from nuscenes-devkit 1.2.0
``nuscenes/utils/splits.py`` (Apache-2.0) into ``nuscenes_val_scenes.txt``.

Needs: root/v1.0-trainval/*.json and root/samples/LIDAR_TOP/*.pcd.bin for val
keyframes. No sweeps, no cameras.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

import numpy as np
from pyquaternion import Quaternion

from ..geometry import Box
from ..tracklet import Frame, Tracklet

TRACKING_TO_GENERAL = {
    "bicycle": ["vehicle.bicycle"],
    "bus": ["vehicle.bus.bendy", "vehicle.bus.rigid"],
    "car": ["vehicle.car"],
    "motorcycle": ["vehicle.motorcycle"],
    "pedestrian": ["human.pedestrian.adult", "human.pedestrian.child",
                   "human.pedestrian.construction_worker",
                   "human.pedestrian.police_officer"],
    "trailer": ["vehicle.trailer"],
    "truck": ["vehicle.truck"],
}


def val_scenes() -> List[str]:
    p = os.path.join(os.path.dirname(__file__), "nuscenes_val_scenes.txt")
    with open(p) as f:
        return [l.strip() for l in f if l.strip()]


def _load(root, version, name):
    with open(os.path.join(root, version, name + ".json")) as f:
        return json.load(f)


def _T(rotation, translation) -> np.ndarray:
    T = np.eye(4)
    T[:3, :3] = Quaternion(rotation).rotation_matrix
    T[:3, 3] = translation
    return T


def _lidar_loader(path: str, T_global_lidar: np.ndarray):
    def load():
        pts = np.fromfile(path, dtype=np.float32).reshape(-1, 5)[:, :3].astype(float)
        return pts @ T_global_lidar[:3, :3].T + T_global_lidar[:3, 3]
    return load


def index_nuscenes(root: str, category: str = "car", version: str = "v1.0-trainval",
                   scenes: List[str] | None = None, min_points: int = 1,
                   key_frame_only: bool = True) -> List[Tracklet]:
    """``min_points`` filters on the FIRST annotation's ``num_lidar_pts`` as in
    Open3DSOT; set it to each tracker's official test config value."""
    if version == "v1.0-mini" and scenes is None:
        raise ValueError("mini is not allowed for the study (PREREG_DRAFT §2)")
    scenes = set(scenes if scenes is not None else val_scenes())
    tabs = {n: _load(root, version, n) for n in
            ["instance", "sample_annotation", "sample", "scene", "category",
             "sample_data", "calibrated_sensor", "ego_pose"]}
    by = {n: {r["token"]: r for r in tabs[n]} for n in tabs}
    lidar_sd: Dict[str, dict] = {}
    for sd in tabs["sample_data"]:
        if sd.get("is_key_frame") and "LIDAR_TOP" in sd["filename"]:
            lidar_sd[sd["sample_token"]] = sd
    general = set(TRACKING_TO_GENERAL[category.lower()])
    out = []
    for inst in tabs["instance"]:
        if by["category"][inst["category_token"]]["name"] not in general:
            continue
        a0 = by["sample_annotation"][inst["first_annotation_token"]]
        scene = by["scene"][by["sample"][a0["sample_token"]]["scene_token"]]
        if scene["name"] not in scenes or a0["num_lidar_pts"] < min_points:
            continue
        frames = []
        tok = inst["first_annotation_token"]
        while tok:
            a = by["sample_annotation"][tok]
            tok = a["next"]
            sd = lidar_sd.get(a["sample_token"])
            if sd is None or (key_frame_only and not sd["is_key_frame"]):
                continue
            cs = by["calibrated_sensor"][sd["calibrated_sensor_token"]]
            ep = by["ego_pose"][sd["ego_pose_token"]]
            T_gl = _T(ep["rotation"], ep["translation"]) @ _T(cs["rotation"], cs["translation"])
            yaw = Quaternion(a["rotation"]).yaw_pitch_roll[0]
            frames.append(Frame(
                gt=Box(tuple(a["translation"]), tuple(a["size"]), float(yaw)),
                T_world_sensor=np.eye(4), timestamp=sd["timestamp"] * 1e-6,
                load_points=_lidar_loader(os.path.join(root, sd["filename"]), T_gl),
                meta=dict(scene=scene["name"], ann_token=a["token"],
                          num_lidar_pts=a["num_lidar_pts"],
                          visibility=a.get("visibility_token"))))
        out.append(Tracklet("nuscenes", inst["token"], category.lower(), frames,
                            meta=dict(scene=scene["name"])))
    return out
