# CPU agent status (branch `cpu-agent`) — not a pre-registration

**Nothing has been run on real data.** No KITTI/nuScenes download, no nuScenes login, no GPU runs.
Real-data commands in `ic001/run.py` refuse to run until `PREREG.githash` exists (`ic001/guard.py`).
`PREREG.md` is intentionally **not** created: the pre-registration stays `PREREG_DRAFT.md` until Sudesh approves it.

## Implemented (synthetic tests only: `pytest -q`, 30 pass)
- `ic001/trackers.py`: last-box (control 1), CV no snap (control 2), CV + offset-preserving snap (floor), floor without ego-compensation (control 3, KITTI); ground filter keeps points > 0.25 m above box bottom (FIX a); 0.5 m BEV expansion; ≥5 points; heading rule (1.0 m/s); frame-1 GT size; protocols (a) OPE and (b) one-step re-init.
- `ic001/metrics.py`: Open3DSOT Success (3D IoU, 21 thresholds 0–1, `>=`) and Precision (centre distance, 21 thresholds 0–2 m, `<=`), per-frame contributions.
- `ic001/geometry.py`: upright boxes, IoU with an Open3DSOT-compatible mode (its z-extent quirk) and a true-geometry mode.
- `ic001/bins.py`: GT point-count × motion bins (KITTI <50/50–199/≥200, 0.5 m; nuScenes <10/10–24/≥25, 2.5 m), merge check (<30 tracklets), tracklet tertiles.
- `ic001/stats.py`: per-cell Success/Precision, tracklet bootstrap of learned − floor gap (best family per cell), concentration ratio R = gain share / frame share with threshold 1.2 and CI-excludes-1, DRAFT KILL/GO/INCONCLUSIVE rule.
- `ic001/data/kitti.py` (Open3DSOT box conversion + oxts ego poses), `ic001/data/nuscenes.py` (JSON tables, val keyframes, global frame, min_points on first box).
- `gpu_jobs/`: DRAFT M2-Track and MBPTrack specs (free Kaggle T4), untested dump harness. Not sent.

## Open pre-registration items (for Sudesh / Idea Agent; see report)
Listed in the CPU agent's report to Idea Launcher; none are decided in code beyond a parameter default.
