"""CLI. Real-data commands are blocked until the pre-registration is frozen.

  python -m ic001.run floor    --dataset kitti --root DATA --category Car --out runs/kitti_car_floor.csv
  python -m ic001.run evaluate --dataset kitti --floor runs/kitti_car_floor.csv \
                               --learned runs/m2track_kitti_car.csv runs/mbptrack_kitti_car.csv \
                               --out runs/kitti_car_eval.json

Per-frame CSV schema (floor output AND the format GPU jobs must return):
  dataset,category,tracklet_id,frame_idx,protocol,method,cx,cy,cz,w,l,h,yaw
Boxes are in the Open3DSOT scoring frame (KITTI: velodyne of that frame;
nuScenes: global). tracklet_id: KITTI "<scene:04d>_<track_id>", nuScenes
instance token. frame_idx: 0-based index within the tracklet.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict

import numpy as np

from .bins import KITTI_BINS, NUSCENES_BINS, assign_bins, gt_motion, gt_point_counts
from .geometry import Box
from .guard import require_frozen_prereg
from .metrics import frame_precision, frame_success, score_boxes
from .stats import (N_BOOT_DRAFT, SEED_DRAFT, FrameTable, bootstrap_gap, per_cell)
from .trackers import FloorConfig, track

FIELDS = ["dataset", "category", "tracklet_id", "frame_idx", "protocol", "method",
          "cx", "cy", "cz", "w", "l", "h", "yaw"]


def _index(args):
    if args.dataset == "kitti":
        from .data.kitti import index_kitti
        return index_kitti(args.root, split="test", category=args.category), KITTI_BINS
    from .data.nuscenes import index_nuscenes
    return index_nuscenes(args.root, category=args.category,
                          min_points=args.min_points), NUSCENES_BINS


def cmd_floor(args):
    h = require_frozen_prereg()
    trs, _ = _index(args)
    variants = [("last_box", FloorConfig()), ("cv", FloorConfig()), ("cv_snap", FloorConfig())]
    if args.dataset == "kitti":
        variants.append(("cv_snap_noego", FloorConfig(ego_comp=False)))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(FIELDS)
        for tr in trs:
            for name, cfg in variants:
                m = "cv_snap" if name.startswith("cv_snap") else name
                for proto in ("ope", "reinit"):
                    preds, _ = track(tr, m, proto, cfg)
                    for i, b in enumerate(preds):
                        w.writerow([args.dataset, tr.category, tr.tracklet_id, i, proto, name,
                                    *b.center, *b.size, b.yaw])
            for fr in tr.frames:
                fr.points = None  # free memory
    print(f"wrote {args.out} (prereg {h})")


def _read_preds(paths):
    out = defaultdict(dict)  # (method, protocol) -> {(tid, idx): Box}
    for p in paths:
        with open(p) as f:
            for r in csv.DictReader(f):
                b = Box((float(r["cx"]), float(r["cy"]), float(r["cz"])),
                        (float(r["w"]), float(r["l"]), float(r["h"])), float(r["yaw"]))
                out[(r["method"], r["protocol"])][(r["tracklet_id"], int(r["frame_idx"]))] = b
    return out


def cmd_evaluate(args):
    h = require_frozen_prereg()
    trs, spec = _index(args)
    preds = _read_preds([args.floor] + list(args.learned))
    tids, cells, hard, keys = [], [], [], []
    for tr in trs:
        fb = assign_bins(gt_point_counts(tr), gt_motion(tr), spec)
        start = 0 if args.include_first_frame else 1
        for i in range(start, len(tr)):
            tids.append(tr.tracklet_id); cells.append(fb.label[i]); hard.append(fb.hard[i])
            keys.append((tr.tracklet_id, i, tr.frames[i].gt))
        for fr in tr.frames:
            fr.points = None
    report = {"prereg_githash": h, "dataset": args.dataset, "category": args.category,
              "n_frames": len(keys), "protocols": {}}
    for proto in ("ope", "reinit"):
        succ, prec = {}, {}
        for (m, p), d in preds.items():
            if p != proto:
                continue
            missing = [k for k in keys if (k[0], k[1]) not in d]
            if missing:
                raise ValueError(f"{m}/{p}: {len(missing)} frames missing (e.g. {missing[0][:2]})")
            ious, dists = score_boxes([d[(k[0], k[1])] for k in keys], [k[2] for k in keys])
            succ[m], prec[m] = frame_success(ious), frame_precision(dists)
        if not succ:
            continue
        ts, tp = (FrameTable(np.array(tids), np.array(cells), np.array(hard), s)
                  for s in (succ, prec))
        ts_h = FrameTable(np.array(tids), np.where(hard, "hard", "easy"), np.array(hard), succ)
        learned = [m for m in succ if m not in ("last_box", "cv", "cv_snap", "cv_snap_noego")]
        rep = {"overall_success": {m: float(v.mean()) for m, v in succ.items()},
               "overall_precision": {m: float(v.mean()) for m, v in prec.items()},
               "per_cell_success": {m: per_cell(ts, m) for m in succ},
               "per_cell_precision": {m: per_cell(tp, m) for m in prec},
               "per_hard_easy_success": {m: per_cell(ts_h, m) for m in succ}}
        if learned:
            rep["gap_vs_floor"] = bootstrap_gap(ts, learned, "cv_snap",
                                                n_boot=args.n_boot, seed=args.seed)
        report["protocols"][proto] = rep
    with open(args.out, "w") as f:
        json.dump(report, f, indent=1)
    print(f"wrote {args.out}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ic001")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("floor", "evaluate"):
        s = sub.add_parser(name)
        s.add_argument("--dataset", choices=["kitti", "nuscenes"], required=True)
        s.add_argument("--root", required=True)
        s.add_argument("--category", default="Car")
        s.add_argument("--min-points", type=int, default=1)
        s.add_argument("--out", required=True)
    e = sub.choices["evaluate"]
    e.add_argument("--floor", required=True)
    e.add_argument("--learned", nargs="*", default=[])
    e.add_argument("--n-boot", type=int, default=N_BOOT_DRAFT)
    e.add_argument("--seed", type=int, default=SEED_DRAFT)
    e.add_argument("--include-first-frame", action="store_true",
                   help="per-bin analysis includes frame 0 (motion undefined); OPEN item")
    a = ap.parse_args(argv)
    {"floor": cmd_floor, "evaluate": cmd_evaluate}[a.cmd](a)


if __name__ == "__main__":
    main()
