"""Training-free motion floor and its controls (PREREG_DRAFT §3).

All propagation happens in the world frame (KITTI: ego-compensated with oxts
poses; nuScenes: global frame). Predictions are mapped back to each frame's
sensor frame for scoring, so scoring matches Open3DSOT.

Methods
-------
``last_box``  zero-velocity copy of the previous box, no snap (control 1).
``cv``        constant velocity, no snap (control 2).
``cv_snap``   the floor: constant velocity + offset-preserving snap.
Control 3 (KITTI only) = ``cv_snap`` with ``ego_comp=False``.

Defaults follow PREREG.md (frozen): heading is always the previous box's yaw
(choice k); OPE keeps the frame-1 GT size, re-init uses the previous GT box
size (choice j); the CV control is only meaningful under re-init (choice d).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from .geometry import Box, points_in_box, wrap_angle
from .tracklet import Tracklet, to_world

METHODS = ("last_box", "cv", "cv_snap")
PROTOCOLS = ("ope", "reinit")


@dataclass(frozen=True)
class FloorConfig:
    ground_clearance: float = 0.25  # [FIX a] keep points > 0.25 m above box bottom
    snap_bev_margin: float = 0.5  # predicted box expanded by 0.5 m in BEV
    snap_min_points: int = 5  # snap only if >= 5 non-ground points
    ego_comp: bool = True  # False = control 3 (KITTI)
    # POST-HOC, SECONDARY, NOT PRE-REGISTERED (Sudesh, 21 Nov, after KITTI floor
    # results): "velocity" = PREREG_DRAFT v0 heading rule (yaw = atan2(v_y, v_x)
    # when world speed > heading_speed_thresh, else previous yaw). The frozen
    # primary is "previous_box" (PREREG choice k).
    heading_mode: str = "previous_box"
    heading_speed_thresh: float = 1.0  # m/s, used only by heading_mode="velocity"


def nonground_in_box(points_w: np.ndarray, box: Box, cfg: FloorConfig) -> np.ndarray:
    """Points inside ``box`` expanded by ``snap_bev_margin`` in BEV and more than
    ``ground_clearance`` above that box's bottom."""
    if points_w.shape[0] == 0:
        return points_w[:, :3]
    m = points_in_box(points_w, box, bev_margin=cfg.snap_bev_margin)
    m &= points_w[:, 2] > box.bottom_z + cfg.ground_clearance
    return points_w[m, :3]


def ground_filter_removed_fraction(points_w: np.ndarray, box: Box,
                                   cfg: FloorConfig = FloorConfig()) -> float:
    """V4 sanity: fraction of in-box points (expanded box) removed by FIX (a)."""
    m = points_in_box(points_w, box, bev_margin=cfg.snap_bev_margin)
    n = int(m.sum())
    if n == 0:
        return float("nan")
    kept = int((points_w[m, 2] > box.bottom_z + cfg.ground_clearance).sum())
    return 1.0 - kept / n


@dataclass
class StepInfo:
    snapped: bool
    n_snap_points: int
    offset_defined: bool


def track(tracklet: Tracklet, method: str = "cv_snap", protocol: str = "ope",
          cfg: FloorConfig = FloorConfig()):
    """Run one training-free tracker on one tracklet.

    Returns (predictions in each frame's sensor frame, per-step info).
    Frame 0 prediction = frame-0 GT box (Open3DSOT convention).
    Under OPE, ``cv`` == ``last_box`` by construction (frame 2 is a zero-velocity
    copy and velocity comes from the tracker's own centres).
    """
    if method not in METHODS:
        raise ValueError(f"unknown method {method}")
    if protocol not in PROTOCOLS:
        raise ValueError(f"unknown protocol {protocol}")
    frames = tracklet.frames
    n = len(frames)
    I = np.eye(4)
    Ts = [f.T_world_sensor if cfg.ego_comp else I for f in frames]
    gt_w = [f.gt.transform(T) for f, T in zip(frames, Ts)]
    size = frames[0].gt.size  # frame-1 GT size, fixed
    ts = [f.timestamp for f in frames]

    preds_w: List[Box] = [gt_w[0]]
    infos: List[StepInfo] = [StepInfo(False, 0, False)]
    offset: Optional[np.ndarray] = None
    pts_cache = {}

    def pts_w(i):
        if i not in pts_cache:
            pts_cache[i] = to_world(frames[i].get_points(), Ts[i])
        return pts_cache[i]

    for t in range(1, n):
        src = preds_w if protocol == "ope" else gt_w
        prev = src[t - 1]
        # OPE: frame-1 GT size fixed. Re-init: previous GT box incl. its size.
        box_size = size if protocol == "ope" else prev.size
        prev = Box(prev.center, box_size, prev.yaw)
        dt = max(ts[t] - ts[t - 1], 1e-6)
        yaw = prev.yaw  # heading from the previous box, never from velocity
        c = prev.c.copy()
        if method != "last_box" and t >= 2:
            prev2 = src[t - 2]
            dt_prev = max(ts[t - 1] - ts[t - 2], 1e-6)
            disp = prev.c - prev2.c  # floor's own last two centres (OPE)
            c = prev.c + disp * (dt / dt_prev)
            if cfg.heading_mode == "velocity":  # POST-HOC variant only
                speed = float(np.linalg.norm(disp[:2]) / dt_prev)
                if speed > cfg.heading_speed_thresh:
                    yaw = float(np.arctan2(disp[1], disp[0]))
            elif cfg.heading_mode != "previous_box":
                raise ValueError(cfg.heading_mode)
        pred = Box(tuple(c), box_size, wrap_angle(yaw))
        info = StepInfo(False, 0, offset is not None)

        if method == "cv_snap":
            # update object-frame offset o = R_{t-1}^-1 (C_{t-1} - G_{t-1})
            g_prev = nonground_in_box(pts_w(t - 1), prev, cfg)
            if g_prev.shape[0] >= cfg.snap_min_points:
                offset = prev.R.T @ (prev.c - g_prev.mean(axis=0))
            elif protocol == "reinit":
                offset = None
            g_now = nonground_in_box(pts_w(t), pred, cfg)
            info = StepInfo(False, int(g_now.shape[0]), offset is not None)
            if g_now.shape[0] >= cfg.snap_min_points and offset is not None:
                pred = pred.with_center(g_now.mean(axis=0) + pred.R @ offset)
                info.snapped = True
        preds_w.append(pred)
        infos.append(info)
        pts_cache.pop(t - 2, None)

    preds = [b.transform(np.linalg.inv(T)) for b, T in zip(preds_w, Ts)]
    return preds, infos
