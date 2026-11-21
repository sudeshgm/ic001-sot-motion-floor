# KITTI floor run (CPU) — RUNLOG

- PREREG frozen at e31629c99566bd989094d3a3922374863f0ac163 (`PREREG.githash`); code at branch `cpu-agent`, commit with this file.
- Data: `/workspace/ic001/data/kitti` (DATA.md, `data_manifest/kitti_sha256.txt`). Open3DSOT test split scenes 0019–0020.
- Tracklets/frames (match Open3DSOT counts cited in PREREG_DRAFT): Car 120 / 6,424; Pedestrian 62 / 6,088; Van 16 / 1,248; Cyclist 8 / 308.
- Commands (per class C): `python -m ic001.run floor --dataset kitti --root /workspace/ic001/data/kitti --category C --out runs/kitti_C_floor_{A,B}.csv`; `python -m ic001.run evaluate ... --floor runs/kitti_C_floor_A.csv`; `python -m ic001.run sanity` (Car, Pedestrian).
- Merge rule (decided from GT only, `scripts/gt_bin_census.py`, before any score was looked at): every point bin of Car and Pedestrian has ≥ 30 distinct tracklets → **no merge**; KITTI bins stay <50 / 50–199 / ≥200.
- Under-powered (< 30 tracklets): Car high-motion bin (17 tracklets, 24.6% of binned frames); Pedestrian high-motion (6 frames); all Van and Cyclist bins (Other).
- V3 determinism: two independent runs per class are byte-identical (`V3_determinism_sha256.txt`). PASS.
- V4 ground filter (20 random frames, seed 0, GT box + 0.5 m BEV): Car median 0.126 removed (0.00–0.52), Pedestrian median 0.107 (0.00–0.34). Reported, not tuned.
- Deviations: none. The CV control is reported under re-init only (identical to last box under OPE, PREREG (d)).
- Learned trackers not run yet (GPU jobs pending) → decision rule NOT applied.
