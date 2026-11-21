# GPU job: MBPTrack inference for the IC001 first test (DRAFT — not sent, not run)

**Why GPU:** MBPTrack uses CUDA point ops (`pointnet2_ops`) and pytorch3d; it pins torch 1.8.0 + CUDA 11.1 + pytorch3d 0.6.2 + pytorch-lightning 1.5.10. Inference only.
**Cost:** free Kaggle T4 only. **No money spent.** Estimated ≤ 1 T4-hour of inference (estimate); environment setup is the main risk (Archive: up to 1–2 days for old pins).
**Gate:** same as `m2track_first_test.md` (launch + KITTI + nuScenes login approved, `PREREG.githash` exists).

## Code and checkpoints
- Repo: `https://github.com/slothfulxtx/MBPTrack3D` (**no licence file** — use for evaluation only, do not redistribute code or weights). Record commit.
- Checkpoints: Google Drive folder from the README (`https://drive.google.com/drive/folders/1bYa_oLTbQcnm-wQO89Dv5km8HH_GIqSv`): `mbptrack_kitti_{car,ped,van,cyc}` and nuScenes car/ped/truck/trailer/bus. **Sizes and download liveness not yet checked.** Fetch with `gdown --folder` inside Kaggle; record SHA-256. If the Drive link is dead or quota-blocked: stop and report (do not substitute other weights).
- Configs: `configs/mbptrack_kitti_{car,ped,van,cyc}_cfg.yaml` (KITTI loader uses `coordinate_mode: camera`, `up_axis [0,-1,0]`), `configs/mbptrack_nuscenes_kitti_{car,ped,truck,trailer,bus}_cfg.yaml` (`NuscenesKITTIMem`, `test_version v1.0-trainval`, keyframes only, `min_points=1` on val/test).
- Test command (README): `python main.py configs/mbptrack_kitti_car_cfg.yaml --phase test --resume_from pretrained/mbptrack_kitti_car.ckpt`

## Environment (Kaggle T4)
Plan A (faithful): micromamba env with Python 3.8, `pytorch==1.8.0 cudatoolkit=11.1`, `pytorch3d==0.6.2` (conda `pytorch3d` channel or source build), `pytorch-lightning==1.5.10`, then build the repo's `pointnet2_ops` with `TORCH_CUDA_ARCH_LIST="7.5"`. Use `freeze.yml` from the repo as the reference list.
Plan B (only if A fails after a bounded effort, e.g. 2 h): Kaggle's modern torch + pytorch3d built from source + rebuilt `pointnet2_ops`; record every deviation. V1 reproduction decides whether Plan B numbers are usable.

## Steps
1. **V1 reproduction (protocol a):** run the README test command for KITTI Car; record Success/Precision; compare with the MBPTrack paper's KITTI Car value (look it up in the paper and record the table/number; tolerance 1.0 Success is an OPEN pre-registration item). Outside tolerance → stop, report, no tuning.
2. **Coordinate frame:** MBPTrack's KITTI loader works in the **camera** frame. Convert every output box to the Open3DSOT velodyne frame before writing the CSV: centre_velo = inv([Tr_velo_cam; 0 0 0 1]) · centre_cam (their camera-mode centre already includes the −h/2 shift, same as Open3DSOT), size (w, l, h) unchanged, yaw_velo derived from the camera-frame rotation about −y (yaw_velo = −(rot_y + π/2), same mapping as `ic001/data/kitti.py`). Self-check: converting the frame-0 GT box must give exactly the box `ic001.data.kitti.index_kitti` produces (print max centre error; must be < 1e-4 m).
3. **Per-frame dump, protocols (a) and (b):** patch MBPTrack's evaluation loop (in `models/MBPTrack/model.py` / base model test step) to record the box predicted at every frame, plus a `reinit` variant where the previous box and the memory frames' boxes/targetness masks come from GT. Write `mbptrack_<dataset>_<class>.csv` in the schema of `gpu_jobs/README.md`. Sanity: Success recomputed from the dumped `ope` boxes equals the step-1 value.
4. **nuScenes tracklet ids:** `NuscenesKITTIMem` rebuilds tracklets from nuScenes instances; record `instance_token` for each tracklet as `tracklet_id`, and check its frame count equals `ic001.data.nuscenes.index_nuscenes` on the same data. If tracklet sets differ (e.g. different filtering), stop and report the difference.
5. Order: KITTI Car first (headline), then nuScenes Car, then the other classes.

## Return to the box
One CSV per (dataset, class) with both protocols, step-1 logs, `pip freeze` / `conda list`, `nvidia-smi`, MBPTrack commit, checkpoint SHA-256s, wall times, list of environment deviations. Nothing else.

## Status
DRAFT. Not sent, not run. No money spent.
