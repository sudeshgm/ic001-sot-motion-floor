"""Dataset-agnostic tracklet container used by trackers, bins and metrics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

import numpy as np

from .geometry import Box


@dataclass
class Frame:
    gt: Box  # GT box in the sensor (LiDAR) frame of this frame
    T_world_sensor: np.ndarray  # 4x4, sensor -> world (identity if unknown)
    timestamp: float  # seconds
    points: Optional[np.ndarray] = None  # (N, >=3) in sensor frame, lazily loaded
    load_points: Optional[Callable[[], np.ndarray]] = None
    meta: dict = field(default_factory=dict)

    def get_points(self) -> np.ndarray:
        if self.points is None:
            if self.load_points is None:
                return np.zeros((0, 3))
            self.points = self.load_points()
        return self.points


@dataclass
class Tracklet:
    dataset: str  # "kitti" | "nuscenes" | "synthetic"
    tracklet_id: str
    category: str
    frames: List[Frame]
    meta: dict = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.frames)


def to_world(points: np.ndarray, T: np.ndarray) -> np.ndarray:
    if points.size == 0:
        return points[:, :3] if points.ndim == 2 else np.zeros((0, 3))
    return points[:, :3] @ T[:3, :3].T + T[:3, 3]
