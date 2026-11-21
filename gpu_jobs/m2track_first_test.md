# GPU job: M2-Track inference for the IC001 first test (DRAFT — not sent, not run)

**Why GPU:** Open3DSOT needs the `pointnet2_ops` CUDA kernels (erikwijmans Pointnet2_PyTorch). A CPU port would change the checkpoint's numbers (GATES.md §4). Inference only, no training.
**Cost:** free Kaggle T4 only. **No money spent.** Estimated ≤ 1 T4-hour incl. setup (estimate).
**Gate:** do not run until the launch, the KITTI download and (for nuScenes) Sudesh's nuScenes login are approved AND `PREREG.githash` exists in `sudeshgm/ic001-sot-motion-floor`.

## Code and checkpoints
- Repo: `https://github.com/Ghostish/Open3DSOT` (MIT). Record the commit hash used.
- Checkpoints (in repo, 27 MB each): `pretrained_models/mmtrack_kitti_car.ckpt`, `mmtrack_kitti_pedestrian.ckpt`, `mmtrack_nuscenes_car.ckpt`. No Van/Cyclist/nuScenes-Ped M2-Track checkpoints exist → those cells are not scored for M2-Track.
- Configs: `cfgs/M2_track_kitti.yaml` (set `category_name`, `path`; `coordinate_mode: velodyne`, `up_axis [0,0,1]`, `IoU_space: 3`, `test_split: test` = scenes 0019–0020), `cfgs/M2_Track_nuscene.yaml` (`version: v1.0-trainval`, `test_split: val`, `key_frame_only: True`; loader uses `min_points=1` on the test split).

## Environment (Kaggle T4, sm_75)
1. `git clone https://github.com/Ghostish/Open3DSOT && cd Open3DSOT && git rev-parse HEAD`
2. Use Kaggle's preinstalled torch (record version). `pip install -r requirement.txt` but keep Kaggle torch; pin `pytorch-lightning` to the version in `requirement.txt` if it imports, otherwise the nearest 1.x that does (record the deviation).
3. `TORCH_CUDA_ARCH_LIST="7.5" pip install "git+https://github.com/erikwijmans/Pointnet2_PyTorch.git#egg=pointnet2_ops&subdirectory=pointnet2_ops_lib"`
4. nuScenes rows: `pip install nuscenes-devkit` (Kaggle Python ≥3.10 is fine for the devkit).
Note from the README: checkpoints were produced on 3090/3080ti; small GPU-precision differences are expected.

## Steps
1. **V1 reproduction (protocol a, standard script):**
   `python main.py --cfg cfgs/M2_track_kitti.yaml --checkpoint pretrained_models/mmtrack_kitti_car.ckpt --test` (category Car). Record printed Success/Precision. Reference values: README checkpoint table KITTI Car 67.43 / 81.04, Pedestrian 60.61 / 89.39, nuScenes Car 57.22 / 65.72; M2-Track paper KITTI Car 65.5 / 80.8. **Which reference the 1.0-Success tolerance applies to is an open pre-registration item.** If outside tolerance: stop and report, no tuning.
2. **Per-frame dump, protocol (a) and (b):** `python ../gpu_jobs/dump_open3dsot.py --cfg <cfg> --checkpoint <ckpt> --category <Car|Pedestrian> --method m2track --protocols ope reinit --out m2track_<dataset>_<class>.csv`
   (from the IC001 repo; run with Open3DSOT root as CWD so `datasets`/`models` import). Sanity: Success recomputed from the dumped `ope` boxes by the harness must equal step 1's value (it prints both).
3. Repeat 1–2 for KITTI Pedestrian and nuScenes Car.

## Return to the box
`m2track_kitti_car.csv`, `m2track_kitti_pedestrian.csv`, `m2track_nuscenes_car.csv` (schema in `gpu_jobs/README.md`), the step-1 logs, `pip freeze`, `nvidia-smi`, Open3DSOT commit, checkpoint SHA-256s, wall times. Nothing else.

## Expected runtime (estimate)
KITTI Car 6,424 frames + Ped 6,088 frames + nuScenes Car val keyframes; M2-Track is fast (>50 FPS on a 3090). × 2 protocols ≈ 10–20 min of inference on a T4, plus setup/data staging.

## Status
DRAFT. Not sent, not run. No money spent.
