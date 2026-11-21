# IC001 secondary analyses

**Status: SECONDARY.** Nothing in this file is part of the frozen GO / KILL decision rule, the frozen floor, or frozen V1. All of it is to be labelled SECONDARY (or, for #5, a follow-up that runs only after a primary GO) in `RESULTS.md`. The frozen pre-registration is `PREREG.md` on branch `cpu-agent` at `e31629c`; the only change to that document is the dated V1 tolerance restatement in `PREREG_ADDENDUM_2026-11-21.md`.

Source: Idea Advocate notes of 21 November 2026 (`/workspace/idea_advocate/notes/20261121_IC001.md`), added to `main` at Sudesh's instruction: "Whatever helps in making paper better add it to main branch of repo and inform to cpu agent."

GPU compute, where needed, is **free Kaggle T4 only**. A private Kaggle dataset is already approved for the first-test jobs.

## Caveats that apply to the whole study

**F2 — power, KITTI motion axis.** A GT-only census (21 Nov 2026, no tracker scores) found that the KITTI Car high-motion bin (≥0.5 m world-frame displacement) has **17 tracklets**, below the frozen §9 minimum of 30. Pedestrian high motion has 6 frames in 6 tracklets. All KITTI point bins have ≥30 tracklets, so they need no merge. Primary-easy (≥50 points and low motion) covers 51.2% of Car frames (112 tracklets) and 89.2% of Pedestrian frames. On KITTI, GO / KILL will therefore rest on the point bins; any motion claim has to come from nuScenes. The Car high-motion bin cannot drive a decision.

**F3 — unread literature threat.** SPSOT (*Self-Supervised Point Cloud Single Object Tracking*, Liu, Hui et al., ICRA 2026, DOI 10.1109/ICRA57385.2026.11696284; code https://github.com/lyhnsn/SPSOT) is a self-supervised tracker with a "simple motion filter." The full text was unread as of 21 November 2026 (IEEE / closed access). It is a learned (self-supervised) detector plus filter, not a training-free floor, and the abstract reports no per-bin analysis. If the paper has a "motion filter only" ablation on KITTI or nuScenes, that line would foreshadow the floor number. Someone with IEEE access should read Tables 1–3 and the ablations before the paper is written. No scoop of the floor study was found as of that date.

## Run order, and what a formal KILL would do

1. **#1 and #2 ride with the GPU jobs.** Both need only about 0.3 T4-h each (≤0.6 T4-h together) in the same Open3DSOT / MBPTrack environment as the first test. Add the extra jobs (the oxts-compensated M2-Track crop, and BAT) to `gpu_jobs` and route them through Idea Launcher to GPU Bot, on the free Kaggle T4 only.
2. **#3 and #4 are CPU only.** #3 starts with a short timing check. #4 needs the nuScenes val stream and a GT count of fast-start tracklets first.
3. **#5 runs only if the primary result is GO.**

**Early KITTI floor context.** On the frozen heading rule, the KITTI Car floor scores **23.9 / 30.2** Success / Precision under the standard protocol (120 tracklets, 6,424 frames), against published learned scores of **65.5** (M2-Track) and **73.4** (MBPTrack). No KITTI point or motion bin was above 27 Success. A labelled post-hoc velocity-heading check made the floor worse (8.8 / 7.9), so heading is not what holds the floor down. A **formal KILL** still waits on the learned trackers' per-bin scores and on nuScenes. If that formal KILL is called, **#2–#5 become moot** for the paper as planned. **#1 and #2 still serve as a cheap diagnostic write-up** (attribution of any remaining KITTI gap, and where published progress sat), at ≤0.6 T4-h.

Advocate's verdict, recorded here as context only: as frozen, the study is likely an RA-L / ICRA / IROS paper; main track is reachable but not likely (subjectively about 1 in 4) and would need a primary GO plus one striking secondary among #4, #1, or #2.

---

## #1 — Ego-motion decomposition, plus an oxts-compensated M2-Track crop (KITTI)

**Failure it fixes.** The study as frozen is an audit of one task. On KITTI it is also unfair in one respect: Open3DSOT's learned trackers run in the sensor frame and never use `oxts`, while the floor is ego-compensated. Part of any floor ≈ learned tie, or of the learned trackers' KITTI error, could be privileged ego pose rather than "motion is enough."

**Mechanism.** On the KITTI Car test split, 2,282 of 6,304 non-first frames (36.2%, 98 tracklets) are static in the world (<0.5 m) but move ≥0.5 m in the sensor frame, because the ego vehicle moves (median ego speed 6.3 m/s; sensor-frame shift up to 1.67 m). With ego-compensation the floor's velocity is about 0 and the snap does the rest; a learned tracker has to regress that shift with no pose input. On nuScenes, Open3DSOT already works in the global frame, so the ego-only cell is empty by construction and nuScenes is a built-in negative control.

**Change (all secondary).**

- A GT-defined KITTI axis: sensor-frame displacement (≥0.5 m) crossed with world-frame displacement. Cells, from the 21 Nov GT census: static/static (2,474 frames, 36 tracklets), ego-only (2,282 frames, 98 tracklets), co-moving (1,065 frames, 11 tracklets, under-powered), both-moving (483 frames, 14 tracklets, under-powered). Claims need ≥30 tracklets; only the first two cells qualify.
- An inference-only adapter, no retraining: run M2-Track (and, if cheap, MBPTrack) with the previous box and the previous crop transformed by `oxts` \(T_t^{-1} \cdot T_{t-1}\) into the current scan before cropping. This is the standard MOT ego-compensation step; the value here is the measured attribution, not a claim of a new method.

**Cheapest falsifying test.** Reuse the planned OPE and re-init outputs, plus one extra M2-Track KITTI Car run. Measure Δgap = (learned − floor) in ego-only frames minus (learned − floor) in static/static frames, within point-bin strata. The no-ego floor (frozen control 3) is a validity check, not a discriminator: it should collapse versus the ego-compensated floor in ego-only frames under either account.

**GO / NO-GO.**

- **GO (H-ego):** Δgap ≤ −3 Success, with the tracklet-bootstrap 95% CI excluding 0, **and** the oxts-compensated M2-Track run gains ≥2 Success on ego-only frames (overall ≥1).
- **NO-GO:** |Δgap| < 2 and the compensated gain is <1. Then report "ego pose is not the source," which also defuses the fairness objection.

**Compute.** CPU minutes for the analysis, plus about **0.2–0.3 T4-h** of extra inference on the free Kaggle T4. Data: KITTI `oxts`, already in the launch data folder (~8.4 MB). No new download.

---

## #2 — BAT progress anchor (R_progress), plus a zero-compute published per-bin table

**Failure it fixes.** The field's "gains are hard-case gains" belief is untested on the standard Open3DSOT protocol, and the frozen study demoted the original P2B→later share analysis (P5) because no P2B checkpoint is available. BAT is a 2021 Open3DSOT checkpoint that can stand in as the old anchor. A published-table meta-analysis can still bring in ≥8 methods at no compute cost.

**Mechanism.** TrackAny3D (arXiv:2507.19908) Table 3, Waymo Vehicle, KITTI-trained, Easy / Medium / Hard tracklet thirds, Success:

- P2B 57.1 / 52.0 / 47.9
- BAT 61.0 / 53.3 / 48.9
- M2-Track 68.1 / 58.6 / 55.4
- MBPTrack 68.5 / 58.4 / 57.6
- TrackAny3D 72.6 / 60.5 / 57.5

P2B→TrackAny3D gains are +15.5 / +8.5 / +9.6, so a rough R ≈ 0.86 (<1). BAT→MBPTrack gains are +7.5 / +5.1 / +8.7, so a rough R ≈ 1.23 (>1). The published pairs straddle R = 1; the outcome on KITTI / nuScenes is open. Caveat: those thirds are by tracklets, not frames, and the table is cross-dataset (KITTI-trained models on Waymo).

Rival predictions: H-hard (recent gains = sparse / occlusion robustness) predicts R_progress > 1.2 with the CI excluding 1; H-refine (recent gains = better box regression on easy frames) predicts R_progress ≤ 1.0. Drop the comparison if the total BAT→best gain is ≤2 Success, as frozen P5 already does.

**Change (all secondary).**

- Add **BAT** (Open3DSOT checkpoints `bat_kitti_car`, `bat_kitti_pedestrian`, `bat_nuscenes_car`; README values 65.37 / 45.74 / 40.73 Success) in the same environment as M2-Track.
- Report R_progress = (share of the BAT→best-learned gain that sits in primary-hard frames) / (share of frames that are primary-hard), using the frozen P5 formula, next to P5's floor→best R.
- Compile a zero-compute table of published per-bin results across ≥8 methods, from TrackAny3D Table 3 (12 rows), BEVTrack sparse subsets, and TFTrack Table IX, as context.

**Cheapest falsifying test.** BAT on KITTI Car and nuScenes Car under OPE, scored by `ic001`. **Informative** if the BAT→best gain is >2 Success on each dataset and the R_progress CI excludes 1 on at least one dataset. **Uninformative (drop)** if the CI covers 1 on both datasets. Either informative sign is publishable as belief evidence.

**Compute.** About **0.3 T4-h** on the free Kaggle T4, plus a zero-compute literature table. Risk: the Open3DSOT README asks for CUDA 10.x to reproduce BAT; a Kaggle T4 (CUDA 11/12) may drift. Report the reproduced value and use BAT only as a relative anchor. No new data.

---

## #3 — A stronger training-free rung: SOTracker on KITTI Car

**Failure it fixes.** The closest prior, LiDAR-SOT, already points in this direction, and reviewers can call the frozen floor (constant velocity plus a centroid snap, with no shape term and no yaw update) a strawman. The known training-free tracker is SOTracker.

**Mechanism.** LiDAR-SOT Table I (Waymo vehicles, Acc = mean IoU) shows that the training-free shape term is large: ICP+MP scores 0.3927 / 0.5156 / 0.2828 (All / Easy / Hard), while ICP+MP+S(All)+MC scores 0.6146 / 0.7496 / 0.4959, a gain of +0.22 mean IoU overall. On the easy third it comes within 0.035 of a PointPillars + Kalman detector, but not on medium / hard. The frozen floor has no shape aggregation (ICP-yaw was dropped, frozen choice (p)), so the training-free ceiling on KITTI / nuScenes is untested and the floor ≈ learned share could be understated.

**Change (secondary).** Port `tusen-ai/LiDAR_SOT` (pure Python + scipy BFGS) to the `ic001` tracklet interface, keep frame-1 GT size and the same scoring, and run **Car only** (SOTracker is vehicle-specific). Report it as "floor+", next to the frozen floor. **Licence caveat:** the upstream repo has **no licence file**. Evaluate only; do not redistribute the ported code, and check the licence situation again before any porting starts. If the licence is incompatible with this public repo, keep the experiment private and report numbers only.

**Cheapest falsifying test.** First, a timing check on 3 KITTI Car tracklets, under 15 minutes of CPU. **NO-GO (runtime)** if the extrapolated runtime is >8 CPU-h for KITTI Car. Then, on KITTI Car OPE:

- **GO** if floor+ overall Success ≥ floor + 3 **and** the share of frames in decision bins with |learned − best training-free| ≤ 5 rises by ≥10 percentage points.
- **NO-GO** if floor+ ≤ floor + 1. Then report "the simple floor is already at the training-free ceiling on KITTI," which also answers the strawman objection.

**Compute.** CPU only; about **1 day of porting**, after the timing check. Runtime is unknown until that check. Ground removal in the upstream code uses Zermas et al. and may need a reimplementation or the same >0.25 m ground rule as the frozen floor. No extra GPU and no new data.

---

## #4 — Pre-declared gated-association fast-start floor (nuScenes)

**Failure it fixes.** This is the only proposed route to a *floor beats every learned tracker* finding, on a slice where published learned trackers already fail badly. "Motion matters" does not predict a floor win here.

**Mechanism.** TFTrack Table IX (nuScenes Car, tracklet-level) reports "Fast start" (initial GT speed >10 m/s) Success of M2-Track 14.38, MBPTrack 12.59, BEVTrack 9.75, TFTrack 15.19, against tracklet means of 60.8–67.8. A likely cause is the search window: Open3DSOT's nuScenes M2-Track config uses `bb_scale 1.25, bb_offset 2` m, while nuScenes keyframes are 2 Hz, so a 10 m/s car moves ≥5 m per keyframe. The **frozen floor fails here too**: frame 2 is a zero-velocity copy and the snap uses only a 0.5 m BEV margin, so a 5 m jump gets no snap and the velocity stays 0. Without a variant, the study would only show "both fail."

Rival predictions: H-window (the target leaves the learned search window) says learned failures concentrate at frames where GT displacement exceeds the window half-width, independent of point count, and floor-G should recover dense fast-start tracklets. H-sparse (fast cars are far and sparse) says failures track first-frame point count, and floor-G also fails on sparse tracklets. The measurement that separates them is the floor-G − learned gap on fast-start × (first-frame points ≥ vs < 10).

**Change (secondary, pre-declared before nuScenes outputs exist).** A variant "floor-G": at any step where the CV box gets fewer than 5 snap points, search non-ground clusters within a gate \(r = v_{\max} \cdot \Delta t\) (Car: \(v_{\max} = 20\) m/s, so \(r = 10\) m at 2 Hz). Pick the cluster nearest the CV prediction whose BEV extent fits inside the frame-1 GT box size + 0.5 m. Then continue with CV plus the offset-preserving snap. The frozen floor remains the headline.

**Cheapest falsifying test.** First count fast-start tracklets (TFTrack Table IX definition) from nuScenes val GT metadata. **Drop** if that count is under 30 (the count is not yet known). Otherwise run floor-G on those nuScenes val Car tracklets, reusing the planned M2-Track / MBPTrack outputs.

- **GO:** ≥30 tracklets **and** floor-G − best learned ≥ 10 Success, with the 95% lower bound > 5, **and** floor-G within 2 Success of the frozen floor on the remaining tracklets (no distractor collapse).
- **NO-GO:** floor-G ≤ best learned + 3.

**Compute.** CPU minutes; no extra GPU. Risk: in dense traffic the gate can lock onto a neighbouring car; the "within 2 of the frozen floor elsewhere" guard is meant to catch that.

---

## #5 — Floor-gated hybrid (follow-up only after a primary GO)

**Failure it fixes.** Even after a GO, the audit still has no deployable consequence on the efficiency axis the field already values (for example TFTrack's claim of about 50% fewer FLOPs).

**Mechanism.** If the floor ties on easy frames, a GT-free test-time gate can route those frames to the floor at almost no cost. Example gate: ≥k snap points in the predicted box and a snap residual |G_t − G_pred| < τ.

**Change.** Define the gate from training-split data only (KITTI scenes 0000–0016), then apply it on the test split. Do **not** start this if the primary result is KILL or INCONCLUSIVE.

**Cheapest falsifying test.** Simulate **offline under protocol (b)** (one-step re-init), where frames are independent, from already-planned outputs, at zero GPU cost.

- **GO:** the gate routes ≥40% of frames to the floor with an overall Success loss ≤0.5 against the learned tracker. Then confirm under OPE online (about 0.3 T4-h of M2-Track on the free Kaggle T4).
- **NO-GO:** the loss is >1.0 at 40% routing.

**Compute.** Zero to **0.3 T4-h**. No new data. Novelty of adaptive-compute switching for LiDAR SOT was not searched in depth; treat it as unknown until checked.

---

## Parked and dropped (not added)

- **Parked:** running the floor on Waymo against the 12 published per-bin rows. Needs a Google licence login and Waymo data of unmeasured size, which must be checked before any decision. Not authorized here.
- **Dropped as already done:** "show that motion matters" (M2-Track, TFTrack); a harder benchmark (GSOT3D, context only); CV without snap (already frozen control 2; DMT already shows the motion-only centre is weak).
