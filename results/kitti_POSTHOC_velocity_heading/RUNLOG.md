# POST-HOC, SECONDARY, NOT PRE-REGISTERED — velocity-heading check (KITTI Car, Pedestrian)

**Status: POST-HOC / SECONDARY / NOT PRE-REGISTERED.** Requested by Sudesh on 2026-11-21, after he had seen the
frozen KITTI floor results. It does NOT replace or change the frozen primary. The frozen PREREG.md (e31629c)
is untouched. The primary floor heading stays choice (k): the heading comes from the previous box. Results in this folder
must not be used in the KILL/GO/INCONCLUSIVE decision.

- Variant: `FloorConfig(heading_mode="velocity")`. yaw = atan2(v_y, v_x) of the tracker's own last world-frame
  displacement when speed > 1.0 m/s (the PREREG_DRAFT v0 rule); otherwise the previous yaw. Everything else is
  identical to the frozen floor (ego-comp, snap, sizes).
- Method names: `cv_snap_POSTHOC_velhead` (OPE + re-init) and `cv_POSTHOC_velhead` (re-init only; under OPE it is a
  zero-velocity copy, as with frozen `cv`).
- Command: `python -m ic001.run floor --posthoc-velocity-heading --dataset kitti --category {Car,Pedestrian}`.
  The evaluation runs on frozen CSV + POST-HOC rows concatenated, so the frozen columns sit beside it (frozen numbers reproduce exactly).
- Regression check: after the code change, the frozen Cyclist floor CSV is byte-identical to the frozen run
  (sha256 25cd73d5f0a9d200…). Default behaviour is unchanged.
- GT sanity: for moving GT cars (>1 m/s, 4,447 steps), 98.5% have a GT yaw within 20° of the GT velocity direction.
  The convention is correct.

## Results (Success/Precision, Open3DSOT, overall incl. frame 0)

| Class | Protocol | frozen cv_snap (k) | POST-HOC cv_snap_velhead | frozen cv | POST-HOC cv_velhead |
|---|---|---|---|---|---|
| Car | OPE | 23.9/30.2 | **8.8/7.9** | – | – |
| Car | re-init | 89.1/94.9 | 85.6/93.6 | 93.8/96.3 | 90.9/96.3 |
| Pedestrian | OPE | 26.2/48.7 | 22.4/38.8 | – | – |
| Pedestrian | re-init | 86.8/96.8 | 79.7/96.1 | 90.6/97.3 | 84.8/97.3 |

Car OPE by bin, frozen → POST-HOC: pts0 26.6→11.1, pts1 17.6→4.9, pts2 21.8→4.4, motLo 24.6→7.4, motHi 15.8→6.0,
hard_primary 23.4→9.8, easy_primary 21.5→4.5 (Success).

Pedestrian OPE by bin, frozen → POST-HOC: pts0 34.3→31.7, pts1 28.3→22.6, pts2 20.5→18.2, hard 34.3→31.6, easy 24.4→20.4.

**Reading (secondary):** velocity heading makes the floor worse for both classes and both protocols. Under OPE the tracker's
own centre jitter (after the snap) turns into heading errors, and those compound. Choice (k) is therefore not what keeps the
floor low. This removes one validity concern raised about the frozen floor.

Files: `*_POSTHOC_SECONDARY_velhead_eval.json` (evaluate output, frozen + POST-HOC methods),
`*_POSTHOC_SECONDARY_velhead_floor.csv.gz` (POST-HOC rows only), `sha256.txt` (uncompressed CSVs).
