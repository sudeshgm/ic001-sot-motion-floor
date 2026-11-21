"""Synthetic tracklets only (no real data)."""
import numpy as np

from ic001.geometry import Box, rot_z
from ic001.tracklet import Frame, Tracklet


def box_surface_points(box: Box, n=400, rng=None, z_lift=0.0):
    rng = rng or np.random.default_rng(0)
    u = rng.uniform(-0.5, 0.5, size=(n, 3)) * np.array([box.l, box.w, box.h])
    face = rng.integers(0, 2, size=n)
    u[face == 0, 0] = np.sign(u[face == 0, 0]) * box.l / 2
    u[face == 1, 1] = np.sign(u[face == 1, 1]) * box.w / 2
    u[:, 2] = np.clip(u[:, 2], -box.h / 2 + 0.3, box.h / 2) + z_lift
    return u @ box.R.T + box.c


def ground_points(center, half=6.0, z=0.0, n=600, rng=None):
    rng = rng or np.random.default_rng(1)
    xy = rng.uniform(-half, half, size=(n, 2)) + np.asarray(center)[:2]
    return np.c_[xy, np.full(n, z)]


def make_tracklet(n=20, v=(1.0, 0.0, 0.0), dt=0.1, yaw=0.0, size=(1.8, 4.2, 1.5),
                  ego_v=(0.0, 0.0, 0.0), ego_yaw_rate=0.0, n_pts=400, ground=True,
                  tid="t0", seed=0, offset_pts=(0.0, 0.0, 0.0)):
    """Object moving at constant world velocity ``v`` (m/frame); ego moving at
    ``ego_v`` (m/frame) with yaw rate (rad/frame). Points are in the sensor
    frame; GT is in the sensor frame; T_world_sensor is the ego pose."""
    rng = np.random.default_rng(seed)
    frames = []
    c0 = np.array([10.0, 2.0, 0.75])  # box bottom on ground z=0
    for t in range(n):
        cw = c0 + t * np.asarray(v, float)
        bw = Box(tuple(cw), size, yaw)
        T = np.eye(4)
        T[:3, :3] = rot_z(t * ego_yaw_rate)
        T[:3, 3] = t * np.asarray(ego_v, float)
        Tinv = np.linalg.inv(T)
        pts_w = box_surface_points(bw, n_pts, rng) + np.asarray(offset_pts)
        if ground:
            pts_w = np.vstack([pts_w, ground_points(cw, rng=rng)])
        pts_s = pts_w @ Tinv[:3, :3].T + Tinv[:3, 3]
        frames.append(Frame(gt=bw.transform(Tinv), T_world_sensor=T,
                            timestamp=t * dt, points=pts_s))
    return Tracklet("synthetic", tid, "Car", frames)
