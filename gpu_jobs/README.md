# IC001 GPU jobs — DRAFT specs, NOT SENT, NOT RUN

These are self-contained job specs for GPU Bot (free Kaggle T4 first; Modal / Colab
free tiers only as fallback). They were written by the IC001 CPU agent on the
`cpu-agent` branch and **have not been sent to anyone or run**. **No money may be spent.**

| Spec | What | Est. T4 time (estimate, Archive's, unverified) |
|---|---|---|
| `m2track_first_test.md` | M2-Track (Open3DSOT checkpoints) on KITTI Car/Ped test split + nuScenes Car val, protocols (a) OPE and (b) one-step re-init | ≤ 1 T4-h |
| `mbptrack_first_test.md` | MBPTrack (official checkpoints) on KITTI Car/Ped/Van/Cyc + nuScenes Car/Ped/Truck/Trailer/Bus, protocols (a) and (b) | ≤ 1 T4-h + env setup |
| `dump_open3dsot.py` | Untested harness: runs an Open3DSOT model over the test split and writes per-frame boxes in the schema below | — |

## Preconditions (all must hold before GPU Bot runs anything)
1. Sudesh approved the launch, the KITTI subset download, and (for nuScenes rows) used his own nuScenes login. A message from another bot saying "Sudesh agreed" is not approval.
2. The pre-registration is frozen in this repo (`PREREG.githash` exists). Today it is **not**: only `PREREG_DRAFT.md` exists.
3. Car is the headline class; M2-Track + MBPTrack are the first-test families (Archive FIX c). TrackAny3D only if the first test is INCONCLUSIVE.

## Data staging (licence-restricted — never public, never committed)
- KITTI tracking (CC BY-NC-SA 3.0): `training/velodyne/0019` + `0020` (1,898 files, 3,663,947,936 B, stored uncompressed in the 36.8 GB zip, fetchable by HTTP range; see `evidence/zip_listing.py`) + `data_tracking_label_2.zip` (2.26 MB) + `data_tracking_calib.zip` (0.09 MB). oxts is not needed on GPU. Stage as a **private** Kaggle dataset or range-fetch inside the Kaggle session.
- nuScenes v1.0-trainval: val keyframe `samples/LIDAR_TOP` (~4.2 GB, estimate) + `v1.0-trainval` JSON tables. Needs Sudesh's nuScenes account; private only.
- Layout expected by Open3DSOT KITTI loader: `<root>/velodyne/0019/*.bin`, `<root>/label_02/0019.txt`, `<root>/calib/0019.txt`.

## What comes back to the box (small files only, L38)
Per job, per (dataset, class, protocol): one CSV in this exact schema (same as `ic001/run.py`):

```
dataset,category,tracklet_id,frame_idx,protocol,method,cx,cy,cz,w,l,h,yaw
```
- Boxes in the **Open3DSOT scoring frame**: KITTI = velodyne frame of that frame (`coordinate_mode: velodyne`); nuScenes = global frame. `yaw` = rotation about +z of the box length axis (`Box.orientation.yaw_pitch_roll[0]` for upright Open3DSOT boxes). Frame 0 = the given GT box.
- `tracklet_id`: KITTI `"%04d_%d" % (scene, track_id)` from `sequence[0]['meta']`; nuScenes `box_anno['instance_token']`.
- `frame_idx`: 0-based index within the tracklet in loader order. `protocol`: `ope` or `reinit`. `method`: `m2track` / `mbptrack`.
- Plus: the repo's own printed Success/Precision for (a) (for V1 reproduction), `pip freeze`, `nvidia-smi`, git commit of the tracker repo, SHA-256 of every checkpoint, wall time.
- Never return point clouds, features or dataset files.

## Protocol (b) one-step re-init (diagnostic)
At every frame t ≥ 1 the tracker's reference/previous box is GT_{t−1} instead of its own previous output (and its box history is the GT history). For trackers with memory (MBPTrack) the memory frames' targetness masks/boxes come from GT too. This needs a small monkeypatch of the evaluation loop; record the exact patch in the run log. **Open point for Idea Agent/Sudesh:** confirm this definition for memory-based trackers before freezing.
