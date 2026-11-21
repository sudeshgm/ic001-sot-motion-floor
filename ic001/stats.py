"""Per-bin scores, tracklet bootstrap, gain concentration ratio and the DRAFT
first-test decision rule (PREREG_DRAFT §6-§8).

All thresholds are DRAFT defaults and are function parameters so the frozen
pre-registration can set them; nothing here should be tuned after scores exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

N_BOOT_DRAFT = 10_000  # OPEN item: awaiting Sudesh
SEED_DRAFT = 0


@dataclass
class FrameTable:
    """One row per scored frame. ``scores[method]`` = per-frame Success (or
    Precision) contribution from ``metrics.frame_success``."""
    tracklet: np.ndarray  # tracklet ids (any hashable -> mapped to ints)
    cell: np.ndarray  # cell label per frame (str)
    hard: np.ndarray  # bool per frame
    scores: Dict[str, np.ndarray]

    def __post_init__(self):
        self.tracklet = np.asarray(self.tracklet)
        self.cell = np.asarray(self.cell)
        self.hard = np.asarray(self.hard, dtype=bool)
        _, self.tidx = np.unique(self.tracklet, return_inverse=True)
        self.cells = sorted(set(self.cell.tolist()))
        self.cidx = np.array([self.cells.index(c) for c in self.cell])
        self.n_tracklets = int(self.tidx.max()) + 1 if len(self.tidx) else 0

    def _sums(self, method):
        T, C = self.n_tracklets, len(self.cells)
        s = np.zeros((T, C))
        n = np.zeros((T, C))
        np.add.at(s, (self.tidx, self.cidx), self.scores[method])
        np.add.at(n, (self.tidx, self.cidx), 1.0)
        return s, n


def per_cell(table: FrameTable, method: str) -> Dict[str, dict]:
    out = {}
    N = len(table.cell)
    for c in table.cells:
        m = table.cell == c
        out[c] = dict(score=float(table.scores[method][m].mean()),
                      n_frames=int(m.sum()), frame_share=float(m.sum() / N),
                      n_tracklets=int(len(np.unique(table.tidx[m]))))
    return out


def best_family_per_cell(table: FrameTable, learned: Sequence[str]) -> Dict[str, str]:
    """'Learned' in a cell = best point-estimate Success among scored families."""
    pcs = {m: per_cell(table, m) for m in learned}
    return {c: max(learned, key=lambda m: pcs[m][c]["score"]) for c in table.cells}


def _boot_weights(T, n_boot, seed, chunk=1000):
    rng = np.random.default_rng(seed)
    done = 0
    while done < n_boot:
        b = min(chunk, n_boot - done)
        yield rng.multinomial(T, np.full(T, 1.0 / T), size=b).astype(float)
        done += b


def bootstrap_gap(table: FrameTable, learned: Sequence[str], floor: str,
                  n_boot: int = N_BOOT_DRAFT, seed: int = SEED_DRAFT,
                  alpha: float = 0.05) -> Dict[str, dict]:
    """Per-cell gap = best learned - floor, with tracklet-bootstrap CI."""
    best = best_family_per_cell(table, learned)
    sf, n = table._sums(floor)
    sl = {m: table._sums(m)[0] for m in set(best.values())}
    C = len(table.cells)
    gaps = []
    for W in _boot_weights(table.n_tracklets, n_boot, seed):
        cnt = W @ n
        with np.errstate(invalid="ignore", divide="ignore"):
            g = np.empty((W.shape[0], C))
            for j, c in enumerate(table.cells):
                g[:, j] = (W @ sl[best[c]][:, j] - W @ sf[:, j]) / cnt[:, j]
        gaps.append(g)
    gaps = np.vstack(gaps)
    base_f = per_cell(table, floor)
    out = {}
    for j, c in enumerate(table.cells):
        col = gaps[:, j][np.isfinite(gaps[:, j])]
        point = per_cell(table, best[c])[c]["score"] - base_f[c]["score"]
        out[c] = dict(best_family=best[c], gap=float(point),
                      lo=float(np.quantile(col, alpha / 2)),
                      hi=float(np.quantile(col, 1 - alpha / 2)),
                      n_frames=base_f[c]["n_frames"],
                      frame_share=base_f[c]["frame_share"],
                      n_tracklets=base_f[c]["n_tracklets"])
    return out


def concentration_ratio(table: FrameTable, early: str, late: str,
                        min_total_gain: float = 2.0) -> Optional[float]:
    """R = (share of gain G in hard frames) / (share of frames that are hard).
    Returns None (undefined) if overall gain <= ``min_total_gain`` Success."""
    d = table.scores[late] - table.scores[early]
    total = d.mean()
    if total <= min_total_gain:
        return None
    share_gain = d[table.hard].sum() / d.sum()
    share_frames = table.hard.mean()
    return float(share_gain / share_frames)


def bootstrap_concentration(table: FrameTable, early: str, late: str,
                            n_boot: int = N_BOOT_DRAFT, seed: int = SEED_DRAFT,
                            threshold: float = 1.2, alpha: float = 0.05,
                            min_total_gain: float = 2.0) -> dict:
    point = concentration_ratio(table, early, late, min_total_gain)
    T = table.n_tracklets
    d = table.scores[late] - table.scores[early]
    dh = np.zeros(T); da = np.zeros(T); nh = np.zeros(T); na = np.zeros(T)
    np.add.at(dh, table.tidx[table.hard], d[table.hard])
    np.add.at(da, table.tidx, d)
    np.add.at(nh, table.tidx[table.hard], 1.0)
    np.add.at(na, table.tidx, 1.0)
    rs = []
    for W in _boot_weights(T, n_boot, seed):
        DA, NA = W @ da, W @ na
        with np.errstate(invalid="ignore", divide="ignore"):
            r = ((W @ dh) / DA) / ((W @ nh) / NA)
        r[DA / NA <= min_total_gain] = np.nan
        rs.append(r)
    rs = np.concatenate(rs)
    ok = rs[np.isfinite(rs)]
    lo = float(np.quantile(ok, alpha / 2)) if ok.size else float("nan")
    hi = float(np.quantile(ok, 1 - alpha / 2)) if ok.size else float("nan")
    supported = point is not None and point > threshold and lo > 1.0
    return dict(R=point, lo=lo, hi=hi, n_valid=int(ok.size),
                threshold=threshold, P5_supported=bool(supported))


def decide_first_test(per_dataset: Dict[str, Dict[str, dict]],
                      min_share: float = 0.20, big_share: float = 0.40,
                      kill_gap: float = 10.0, kill_lo: float = 5.0,
                      go_gap: float = 5.0, go_hi: float = 10.0,
                      min_tracklets: int = 30) -> str:
    """DRAFT §7 rule over per-dataset ``bootstrap_gap`` outputs.
    Cells with < ``min_tracklets`` are under-powered and cannot drive GO/KILL.
    Expects keys 'kitti' and 'nuscenes'; KILL needs both datasets."""
    def eligible(cells):
        return [v for v in cells.values()
                if v["frame_share"] >= min_share and v["n_tracklets"] >= min_tracklets]

    def go_cell(v):
        return v["gap"] <= go_gap and v["hi"] <= go_hi

    elig = {k: eligible(v) for k, v in per_dataset.items()}
    both = ("kitti" in elig) and ("nuscenes" in elig)
    if both and all(elig[k] and all(v["gap"] > kill_gap and v["lo"] > kill_lo for v in elig[k])
                    for k in ("kitti", "nuscenes")):
        return "KILL"
    go_each = both and all(any(go_cell(v) for v in elig[k]) for k in ("kitti", "nuscenes"))
    go_kitti_big = any(go_cell(v) and v["frame_share"] >= big_share
                       for v in elig.get("kitti", []))
    if go_each or go_kitti_big:
        return "GO"
    return "INCONCLUSIVE"
