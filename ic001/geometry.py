"""Upright 3D boxes, point-in-box tests, 3D IoU and centre distance.

Convention (same as Open3DSOT / nuScenes ``Box`` in the LiDAR or global frame):
centre = geometric centre (x, y, z), size = (w, l, h), yaw = rotation about +z
of the box's length axis (local +x). Boxes are upright (no roll/pitch), as in
Open3DSOT's KITTI and nuScenes evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from shapely.geometry import Polygon


def wrap_angle(a: float) -> float:
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def rot_z(yaw: float) -> np.ndarray:
    c, s = np.cos(yaw), np.sin(yaw)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


@dataclass(frozen=True)
class Box:
    center: tuple  # (x, y, z)
    size: tuple  # (w, l, h)
    yaw: float

    @property
    def c(self) -> np.ndarray:
        return np.asarray(self.center, dtype=float)

    @property
    def w(self) -> float:
        return float(self.size[0])

    @property
    def l(self) -> float:
        return float(self.size[1])

    @property
    def h(self) -> float:
        return float(self.size[2])

    @property
    def bottom_z(self) -> float:
        return float(self.center[2]) - self.h / 2.0

    @property
    def R(self) -> np.ndarray:
        return rot_z(self.yaw)

    def with_center(self, c) -> "Box":
        return replace(self, center=tuple(float(v) for v in c))

    def with_yaw(self, yaw: float) -> "Box":
        return replace(self, yaw=wrap_angle(yaw))

    def bev_corners(self) -> np.ndarray:
        """(4, 2) BEV corners, counter-clockwise."""
        hl, hw = self.l / 2.0, self.w / 2.0
        local = np.array([[hl, hw], [-hl, hw], [-hl, -hw], [hl, -hw]])
        R2 = self.R[:2, :2]
        return local @ R2.T + self.c[:2]

    def transform(self, T: np.ndarray) -> "Box":
        """Apply a 4x4 rigid transform. Only the yaw part of the rotation is
        kept for the box orientation (boxes stay upright)."""
        c = T[:3, :3] @ self.c + T[:3, 3]
        dyaw = np.arctan2(T[1, 0], T[0, 0])
        return Box(tuple(c), self.size, wrap_angle(self.yaw + dyaw))


def points_in_box(points: np.ndarray, box: Box, bev_margin: float = 0.0,
                  z_margin: float = 0.0) -> np.ndarray:
    """Boolean mask of points (N, >=3) inside ``box``.

    ``bev_margin`` expands length and width by that many metres on every side
    (the floor's "expanded by 0.5 m in BEV"); ``z_margin`` likewise in z.
    """
    if points.size == 0:
        return np.zeros(0, dtype=bool)
    local = (points[:, :3] - box.c) @ box.R  # world -> box frame (R^T applied)
    return ((np.abs(local[:, 0]) <= box.l / 2.0 + bev_margin)
            & (np.abs(local[:, 1]) <= box.w / 2.0 + bev_margin)
            & (np.abs(local[:, 2]) <= box.h / 2.0 + z_margin))


def iou_3d(a: Box, b: Box, open3dsot_compat: bool = True) -> float:
    """Upright 3D IoU: BEV polygon intersection x z-overlap / union volume.

    ``open3dsot_compat=True`` reproduces Open3DSOT ``estimateOverlap(dim=3,
    up_axis=z)`` exactly, including its quirk of taking the vertical extent as
    [centre_z - h, centre_z] (identical to the true overlap when both boxes have
    the same height, which holds for the floor: frame-1 GT size is kept and
    KITTI/nuScenes GT sizes are per-track constants). ``False`` uses the true
    vertical extent [centre_z - h/2, centre_z + h/2].
    """
    pa, pb = Polygon(a.bev_corners()), Polygon(b.bev_corners())
    inter_bev = pa.intersection(pb).area
    if open3dsot_compat:
        zmax = min(a.center[2], b.center[2])
        zmin = max(a.center[2] - a.h, b.center[2] - b.h)
    else:
        zmin = max(a.bottom_z, b.bottom_z)
        zmax = min(a.bottom_z + a.h, b.bottom_z + b.h)
    inter = inter_bev * max(0.0, zmax - zmin)
    union = a.w * a.l * a.h + b.w * b.l * b.h - inter
    return float(inter / union) if union > 0 else 0.0


def center_distance(a: Box, b: Box) -> float:
    return float(np.linalg.norm(a.c - b.c))
