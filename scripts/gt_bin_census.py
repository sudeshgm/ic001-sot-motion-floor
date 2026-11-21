"""GT-only census per class: frames and distinct tracklets per single-axis bin
(no tracker output involved). Decides the PREREG merge rule before scoring."""
import json, sys
import numpy as np
from ic001.bins import KITTI_BINS, assign_bins, gt_motion, gt_point_counts, single_axis_labels
from ic001.data.kitti import index_kitti

root, out = sys.argv[1], sys.argv[2]
res = {}
for c in ["Car", "Pedestrian", "Van", "Cyclist"]:
    trs = index_kitti(root, "test", c)
    rows = []
    for tr in trs:
        fb = assign_bins(gt_point_counts(tr), gt_motion(tr), KITTI_BINS)
        pl, ml = single_axis_labels(fb)
        for i in range(1, len(tr)):  # frame 0 excluded from bins (choice g)
            rows.append((tr.tracklet_id, pl[i], ml[i], bool(fb.hard[i])))
        for f in tr.frames: f.points = None
    d = {}
    for key, j in (("pts", 1), ("mot", 2)):
        for v in sorted({r[j] for r in rows}):
            sel = [r for r in rows if r[j] == v]
            d[f"{key}:{v}"] = dict(frames=len(sel), share=len(sel) / len(rows),
                                   tracklets=len({r[0] for r in sel}))
    h = [r for r in rows if r[3]]
    d["hard_primary"] = dict(frames=len(h), share=len(h) / len(rows), tracklets=len({r[0] for r in h}))
    res[c] = dict(n_tracklets=len(trs), n_binned_frames=len(rows), bins=d)
    print(c, json.dumps(res[c]), flush=True)
heads = ["Car", "Pedestrian"]
merge = any(v["tracklets"] < 30 for c in heads for k, v in res[c]["bins"].items() if k.startswith("pts:"))
res["merge_point_bins_kitti"] = merge
print("MERGE (per dataset, headline classes Car+Pedestrian):", merge)
json.dump(res, open(out, "w"), indent=1)
