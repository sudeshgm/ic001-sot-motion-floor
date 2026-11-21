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
from .stats import (N_BOOT_DRAFT, SEED_DRAFT, FrameTable, bootstrap_concentration,
                    bootstrap_gap, per_cell)
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
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        trs = trs[k::n]  # tracklets k, k+n, ...; merge with scripts/merge_shards.py
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


FLOOR_METHODS = ("last_box", "cv", "cv_snap", "cv_snap_noego")


def _summ(table_scores, mask_groups):
    out = {}
    for name, mask in mask_groups.items():
        out[name] = {m: (float(v[mask].mean()) if mask.any() else None)
                     for m, v in table_scores.items()}
        out[name]["n_frames"] = int(mask.sum())
    return out


def cmd_evaluate(args):
    """PREREG.md scoring. Overall Success/Precision include frame 0 (choice g);
    per-bin scores exclude frame 0. Primary decision bins are single-axis
    (point bins, motion bins; choice f); the point x motion grid and the
    secondary hard definition are reported as SECONDARY. The CV control is
    reported under re-init only (choice d)."""
    from .bins import secondary_hard, single_axis_labels
    h = require_frozen_prereg()
    trs, spec = _index(args)
    if args.point_edges:
        spec = type(spec)(point_edges=tuple(args.point_edges), motion_thresh=spec.motion_thresh,
                          hard_point_bins=spec.hard_point_bins)
    preds = _read_preds([args.floor] + list(args.learned))
    rows = []  # (tid, idx, gt, first, pbin, mbin, grid, hard, hard2)
    for tr in trs:
        fb = assign_bins(gt_point_counts(tr), gt_motion(tr), spec)
        pl, ml = single_axis_labels(fb)
        h2 = secondary_hard(fb, spec)
        for i in range(len(tr)):
            rows.append((tr.tracklet_id, i, tr.frames[i].gt, i == 0, pl[i], ml[i],
                         fb.label[i], bool(fb.hard[i]), bool(h2[i])))
        for fr in tr.frames:
            fr.points = None
    tid = np.array([r[0] for r in rows]); first = np.array([r[3] for r in rows])
    cols = {k: np.array([r[j] for r in rows]) for k, j in
            (("pts", 4), ("mot", 5), ("grid", 6), ("hard", 7), ("hard2", 8))}
    nb = ~first
    report = {"prereg_githash": h, "dataset": args.dataset, "category": args.category,
              "n_tracklets": len(trs), "n_frames_total": len(rows),
              "n_frames_binned": int(nb.sum()), "point_edges": list(spec.point_edges),
              "motion_thresh": spec.motion_thresh, "protocols": {}}
    for proto in ("ope", "reinit"):
        succ, prec = {}, {}
        for (m, p), d in preds.items():
            if p != proto or (m == "cv" and proto == "ope"):
                continue  # choice d: CV control == last_box under OPE, not reported
            missing = [r for r in rows if (r[0], r[1]) not in d]
            if missing:
                raise ValueError(f"{m}/{p}: {len(missing)} frames missing (e.g. {missing[0][:2]})")
            ious, dists = score_boxes([d[(r[0], r[1])] for r in rows], [r[2] for r in rows])
            succ[m], prec[m] = frame_success(ious), frame_precision(dists)
        if not succ:
            continue
        groups = {"overall_incl_frame0": np.ones(len(rows), bool)}
        for axis in ("pts", "mot"):
            for v in sorted(set(cols[axis].tolist())):
                groups[f"{axis}:{v}"] = nb & (cols[axis] == v)
        groups["hard_primary"] = nb & cols["hard"]
        groups["easy_primary"] = nb & ~cols["hard"]
        sec = {"hard_secondary": nb & cols["hard2"], "easy_secondary": nb & ~cols["hard2"]}
        for v in sorted(set(cols["grid"].tolist())):
            sec[f"grid:{v}"] = nb & (cols["grid"] == v)
        trk = {g: int(len(np.unique(tid[m]))) for g, m in {**groups, **sec}.items()}
        rep = {"success": _summ(succ, groups), "precision": _summ(prec, groups),
               "secondary_success": _summ(succ, sec), "secondary_precision": _summ(prec, sec),
               "n_tracklets": trk}
        learned = [m for m in succ if m not in FLOOR_METHODS]
        if learned:
            gap = {}
            for axis in ("pts", "mot"):
                ft = FrameTable(tid[nb], cols[axis][nb], cols["hard"][nb],
                                {m: v[nb] for m, v in succ.items()})
                gap.update({f"{axis}:{k}": v for k, v in bootstrap_gap(
                    ft, learned, "cv_snap", n_boot=args.n_boot, seed=args.seed).items()})
            rep["gap_vs_floor_primary"] = gap
            # SECONDARY (choice a): gain concentration, floor -> best learned overall
            best = max(learned, key=lambda m: succ[m][nb].mean())
            ft = FrameTable(tid[nb], cols["pts"][nb], cols["hard"][nb],
                            {m: v[nb] for m, v in succ.items()})
            rep["R_secondary_floor_to_best_learned"] = dict(
                late=best, **bootstrap_concentration(ft, "cv_snap", best,
                                                     n_boot=args.n_boot, seed=args.seed))
        report["protocols"][proto] = rep
    with open(args.out, "w") as f:
        json.dump(report, f, indent=1)
    print(f"wrote {args.out}")


def cmd_sanity(args):
    """V4: on 20 random frames (seed 0), fraction of in-box points (GT box,
    0.5 m BEV expansion) removed by the ground filter. Reported, never tuned."""
    from .trackers import ground_filter_removed_fraction
    from .tracklet import to_world
    require_frozen_prereg()
    trs, _ = _index(args)
    allf = [(t, i) for t in range(len(trs)) for i in range(len(trs[t]))]
    rng = np.random.default_rng(0)
    pick = rng.choice(len(allf), size=min(20, len(allf)), replace=False)
    out = []
    for k in sorted(pick):
        t, i = allf[k]
        fr = trs[t].frames[i]
        T = fr.T_world_sensor
        frac = ground_filter_removed_fraction(to_world(fr.get_points(), T), fr.gt.transform(T))
        out.append(dict(tracklet=trs[t].tracklet_id, frame_idx=i, removed_fraction=frac))
        fr.points = None
        print(f"V4 {trs[t].tracklet_id} frame {i}: removed {frac:.3f}")
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ic001")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("floor", "evaluate", "sanity"):
        s = sub.add_parser(name)
        s.add_argument("--dataset", choices=["kitti", "nuscenes"], required=True)
        s.add_argument("--root", required=True)
        s.add_argument("--category", default="Car")
        s.add_argument("--min-points", type=int, default=1)
        s.add_argument("--out", required=True)
    sub.choices["floor"].add_argument("--shard", default=None, help="k/n: run every n-th tracklet from k")
    e = sub.choices["evaluate"]
    e.add_argument("--floor", required=True)
    e.add_argument("--learned", nargs="*", default=[])
    e.add_argument("--n-boot", type=int, default=N_BOOT_DRAFT)
    e.add_argument("--seed", type=int, default=SEED_DRAFT)
    e.add_argument("--point-edges", type=float, nargs="*", default=None,
                   help="override point-bin edges (merged bins per PREREG merge rule)")
    a = ap.parse_args(argv)
    {"floor": cmd_floor, "evaluate": cmd_evaluate, "sanity": cmd_sanity}[a.cmd](a)


if __name__ == "__main__":
    main()
