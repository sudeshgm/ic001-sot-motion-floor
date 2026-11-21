"""GT-defined difficulty bins (PREREG_DRAFT §4). Uses GT attributes only.

Defaults are the DRAFT values; they are parameters so the frozen
pre-registration can set them without code changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

import numpy as np

from .geometry import points_in_box
from .tracklet import Tracklet


@dataclass(frozen=True)
class BinSpec:
    point_edges: Tuple[float, ...]  # inner edges, e.g. (50, 200) -> <50, 50-199, >=200
    motion_thresh: float  # metres between consecutive frames
    hard_point_bins: Tuple[int, ...] = (0,)  # which point bins count as "low-point" (OPEN)
    merged_point_edges: Tuple[float, ...] = ()  # fallback if a cell has < min_tracklets

    def point_bin(self, n_pts: float) -> int:
        return int(np.searchsorted(np.asarray(self.point_edges), n_pts, side="right"))

    def n_point_bins(self) -> int:
        return len(self.point_edges) + 1


KITTI_BINS = BinSpec(point_edges=(50, 200), motion_thresh=0.5, merged_point_edges=(200,))
NUSCENES_BINS = BinSpec(point_edges=(10, 25), motion_thresh=2.5, merged_point_edges=(25,))
MIN_TRACKLETS_PER_CELL = 30


def gt_point_counts(tracklet: Tracklet) -> np.ndarray:
    """Points inside each frame's GT box (sensor frame, no margin)."""
    out = []
    for f in tracklet.frames:
        if "num_pts_override" in f.meta:  # e.g. nuScenes num_lidar_pts (option)
            out.append(f.meta["num_pts_override"])
            continue
        p = f.get_points()
        out.append(int(points_in_box(p, f.gt).sum()) if p.size else 0)
    return np.asarray(out, dtype=float)


def gt_motion(tracklet: Tracklet) -> np.ndarray:
    """World-frame GT centre displacement from the previous frame; NaN at t=0."""
    cs = np.array([f.gt.transform(f.T_world_sensor).c for f in tracklet.frames])
    d = np.full(len(cs), np.nan)
    if len(cs) > 1:
        d[1:] = np.linalg.norm(np.diff(cs, axis=0), axis=1)
    return d


@dataclass
class FrameBins:
    point_bin: np.ndarray
    high_motion: np.ndarray  # bool (False at t=0)
    hard: np.ndarray  # bool
    label: List[str] = field(default_factory=list)


def assign_bins(n_pts: np.ndarray, motion: np.ndarray, spec: BinSpec,
                point_edges: Sequence[float] | None = None) -> FrameBins:
    edges = np.asarray(point_edges if point_edges is not None else spec.point_edges)
    pb = np.searchsorted(edges, n_pts, side="right")
    hm = np.nan_to_num(motion, nan=0.0) >= spec.motion_thresh
    hard_pts = np.isin(pb, spec.hard_point_bins)
    hard = hard_pts | hm
    labels = [f"p{int(p)}|{'mHi' if m else 'mLo'}" for p, m in zip(pb, hm)]
    return FrameBins(pb, hm, hard, labels)


def cell_tracklet_counts(labels: Sequence[str], tracklet_ids: Sequence[str]) -> Dict[str, int]:
    seen: Dict[str, set] = {}
    for lab, tid in zip(labels, tracklet_ids):
        seen.setdefault(lab, set()).add(tid)
    return {k: len(v) for k, v in seen.items()}


def needs_merge(labels, tracklet_ids, min_tracklets: int = MIN_TRACKLETS_PER_CELL) -> bool:
    return any(v < min_tracklets for v in cell_tracklet_counts(labels, tracklet_ids).values())


def tracklet_tertile_edges(per_tracklet_points: Sequence[float]) -> Tuple[float, float]:
    """KITTI last-resort point bins: tertiles of a tracklet-level statistic
    (computed from GT only, before any score is seen)."""
    q = np.quantile(np.asarray(per_tracklet_points, dtype=float), [1 / 3, 2 / 3])
    return float(q[0]), float(q[1])
