"""Standard Open3DSOT one-pass-evaluation metrics.

Success = AUC of the fraction of frames with 3D IoU >= th, th in linspace(0, 1, 21).
Precision = AUC of the fraction of frames with centre distance <= th,
th in linspace(0, 2, 21) metres. Both x100, normalised by the max threshold
(Open3DSOT ``TorchSuccess`` / ``TorchPrecision``).

Because the trapezoid AUC is linear in the indicator, the Success of a set of
frames equals the mean of per-frame contributions; ``frame_success`` /
``frame_precision`` return those, which makes per-bin scores and the tracklet
bootstrap exact and fast.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from .geometry import Box, center_distance, iou_3d

SUCCESS_THRESH = np.linspace(0.0, 1.0, 21)
PRECISION_THRESH = np.linspace(0.0, 2.0, 21)


def _trapz(y, x):
    return np.trapezoid(y, x) if hasattr(np, "trapezoid") else np.trapz(y, x)


def success_auc(ious: Sequence[float]) -> float:
    o = np.asarray(ious, dtype=float)
    if o.size == 0:
        return float("nan")
    curve = [(o >= th).mean() for th in SUCCESS_THRESH]
    return float(_trapz(curve, SUCCESS_THRESH) * 100.0 / SUCCESS_THRESH[-1])


def precision_auc(dists: Sequence[float]) -> float:
    d = np.asarray(dists, dtype=float)
    if d.size == 0:
        return float("nan")
    curve = [(d <= th).mean() for th in PRECISION_THRESH]
    return float(_trapz(curve, PRECISION_THRESH) * 100.0 / PRECISION_THRESH[-1])


def frame_success(ious) -> np.ndarray:
    """Per-frame contribution: mean over frames == success_auc."""
    o = np.asarray(ious, dtype=float)[:, None]
    ind = (o >= SUCCESS_THRESH[None, :]).astype(float)
    return _trapz(ind, SUCCESS_THRESH) * 100.0 / SUCCESS_THRESH[-1]


def frame_precision(dists) -> np.ndarray:
    d = np.asarray(dists, dtype=float)[:, None]
    ind = (d <= PRECISION_THRESH[None, :]).astype(float)
    return _trapz(ind, PRECISION_THRESH) * 100.0 / PRECISION_THRESH[-1]


def score_boxes(preds: Sequence[Box], gts: Sequence[Box]):
    """Per-frame (3D IoU, centre distance)."""
    if len(preds) != len(gts):
        raise ValueError("length mismatch")
    ious = np.array([iou_3d(p, g) for p, g in zip(preds, gts)])
    dists = np.array([center_distance(p, g) for p, g in zip(preds, gts)])
    return ious, dists
