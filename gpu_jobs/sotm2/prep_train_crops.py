"""SOT-M2 Stage 1: per-tracklet LIDAR_TOP sweep crops for nuScenes train_track Car tracklets (box CPU, no GPU).

Reads raw nuScenes JSON tables (no devkit object, to keep memory low) and LIDAR_TOP files either from a
directory (``--src-dir``, e.g. v1.0-mini) or from a ``.tgz`` blob streamed on stdin (``--tar-stdin``), so the
raw blob is never stored. Each needed sweep is transformed sensor -> ego -> global with its own calibration
and ego pose (Open3DSOT convention, xyz only) and cropped per tracklet (axis-aligned box corners +/- offset)
around the GT box (keyframes) or the interpolated GT box (sweeps). Output format matches the SOT-M2 kill test:
``trk_XXXX.npz`` (pts, off, ts, key_idx, ic, iq, iw, gc, gq, gw, npts) plus ``index.json``.

Tracklet filter (as the kill-test census): category vehicle.car, all annotations of an instance whose first
annotation is in a candidate scene, first box num_lidar_pts > 0, at least 2 keyframes.

    python -m gpu_jobs.sotm2.prep_train_crops --meta ROOT --version v1.0-trainval --scenes RANK_FILE \
        --work WORK --out OUT --tar-stdin < <(curl -s .../v1.0-trainval07_blobs.tgz)
"""
import argparse, json, os, sys, tarfile
import numpy as np
from pyquaternion import Quaternion

from gpu_jobs.sotm2.geom import interp_box, crop_axis_aligned
from gpu_jobs.sotm2.select_scenes import pick, _read, N_TARGET, N_MIN


def load_tables(root, version):
    J = lambda n: json.load(open(os.path.join(root, version, n + ".json")))
    return {n: J(n) for n in ["scene", "sample", "sample_data", "sample_annotation", "instance", "category",
                              "calibrated_sensor", "ego_pose"]}


def build_plan(T, scenes):
    """Tracklets and the sweep chain each needs. Returns (tracklets, need) with need[filename] = [(tid, i), ...]."""
    by = {n: {r["token"]: r for r in T[n]} for n in T}
    cat = {c["token"]: c["name"] for c in T["category"]}
    scene_of_sample = {s["token"]: by["scene"][s["scene_token"]]["name"] for s in T["sample"]}
    lidar_key = {}
    for sd in T["sample_data"]:
        if sd["is_key_frame"] and sd["filename"].startswith("samples/LIDAR_TOP/"):
            lidar_key[sd["sample_token"]] = sd
    scenes = set(scenes)
    tracklets, need = [], {}
    for inst in T["instance"]:
        if cat[inst["category_token"]] != "vehicle.car":
            continue
        a0 = by["sample_annotation"][inst["first_annotation_token"]]
        scene = scene_of_sample[a0["sample_token"]]
        if scene not in scenes:
            continue
        annos, tok = [], inst["first_annotation_token"]
        while tok:
            a = by["sample_annotation"][tok]; annos.append(a); tok = a["next"]
        if a0["num_lidar_pts"] <= 0 or len(annos) < 2:
            continue
        keys = [lidar_key[a["sample_token"]] for a in annos]
        sweeps, key_idx = [], []
        for k, sd in enumerate(keys):
            key_idx.append(len(sweeps)); sweeps.append((sd, k, 0.0))
            if k + 1 < len(keys):
                t0, t1 = sd["timestamp"], keys[k + 1]["timestamp"]
                nxt = sd["next"]
                while nxt and nxt != keys[k + 1]["token"]:
                    s = by["sample_data"][nxt]
                    sweeps.append((s, k, (s["timestamp"] - t0) / (t1 - t0))); nxt = s["next"]
                assert nxt == keys[k + 1]["token"], "broken sweep chain"
        boxes = []
        for sd, k, al in sweeps:
            a = annos[k]
            if al == 0.0:
                boxes.append((np.array(a["translation"], float), np.array(a["size"], float), np.array(a["rotation"], float)))
            else:
                b = annos[k + 1]
                boxes.append(interp_box(a["translation"], a["rotation"], a["size"], b["translation"], b["rotation"], al))
        tid = len(tracklets)
        tracklets.append(dict(tid=tid, scene=scene, instance=inst["token"], first_anno=a0["token"], annos=annos,
                              key_idx=key_idx, boxes=boxes, sd=[s[0] for s in sweeps]))
        for i, (sd, _, _) in enumerate(sweeps):
            need.setdefault(sd["filename"], []).append((tid, i))
    return tracklets, need, by


def to_global(raw, sd, by):
    p = np.frombuffer(raw, dtype=np.float32).reshape(-1, 5)[:, :3].T.astype(np.float64)
    cs = by["calibrated_sensor"][sd["calibrated_sensor_token"]]
    p = Quaternion(cs["rotation"]).rotation_matrix @ p + np.array(cs["translation"])[:, None]
    pe = by["ego_pose"][sd["ego_pose_token"]]
    return Quaternion(pe["rotation"]).rotation_matrix @ p + np.array(pe["translation"])[:, None]


def process(raw, fname, need, tracklets, by, work, offset):
    for tid, i in need[fname]:
        t = tracklets[tid]
        p = to_global(raw, t["sd"][i], by)
        c, wlh, q = t["boxes"][i]
        crop = crop_axis_aligned(p, c, wlh, q, offset).T.astype(np.float32)
        d = os.path.join(work, f"{tid:05d}"); os.makedirs(d, exist_ok=True)
        np.save(os.path.join(d, f"{i:05d}.npy"), crop)


def iter_members(args, need):
    if args.tar_stdin:
        with tarfile.open(fileobj=sys.stdin.buffer, mode="r|gz") as tf:
            for m in tf:
                if m.isfile() and m.name in need:
                    yield m.name, tf.extractfile(m).read()
    else:
        for fname in sorted(need):
            f = os.path.join(args.src_dir, fname)
            if os.path.exists(f):
                yield fname, open(f, "rb").read()


def assemble(tracklets, chosen, work, out):
    os.makedirs(out, exist_ok=True)
    index = []
    for t in tracklets:
        if t["scene"] not in chosen:
            continue
        d = os.path.join(work, f"{t['tid']:05d}")
        pts = [np.load(os.path.join(d, f"{i:05d}.npy")) for i in range(len(t["sd"]))]
        off = np.cumsum([0] + [len(p) for p in pts]).astype(np.int64)
        a = t["annos"]
        tid = len(index); fn = f"trk_{tid:04d}.npz"
        np.savez_compressed(os.path.join(out, fn), pts=np.concatenate(pts, 0).astype(np.float32), off=off,
                            ts=np.array([s["timestamp"] for s in t["sd"]], np.int64), key_idx=np.array(t["key_idx"]),
                            ic=np.array([b[0] for b in t["boxes"]]), iw=np.array([b[1] for b in t["boxes"]]),
                            iq=np.array([b[2] for b in t["boxes"]]),
                            gc=np.array([x["translation"] for x in a]), gq=np.array([x["rotation"] for x in a]),
                            gw=np.array([x["size"] for x in a]), npts=np.array([x["num_lidar_pts"] for x in a]))
        index.append(dict(tid=tid, file=fn, instance=t["instance"], scene=t["scene"], n_key=len(a),
                          n_sweep=len(t["sd"]), first_anno=t["first_anno"]))
    json.dump(dict(scenes=sorted(chosen), tracklets=index), open(os.path.join(out, "index.json"), "w"), indent=1)
    return index


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True); ap.add_argument("--version", default="v1.0-trainval")
    ap.add_argument("--scenes", required=True, help="rank file (train_track scenes in seed-0 rank order)")
    ap.add_argument("--work", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--offset", type=float, default=5.0)
    ap.add_argument("--n-target", type=int, default=N_TARGET); ap.add_argument("--n-min", type=int, default=N_MIN)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--src-dir"); g.add_argument("--tar-stdin", action="store_true")
    args = ap.parse_args(argv)
    ranked = _read(args.scenes)
    T = load_tables(args.meta, args.version)
    present = {s["name"] for s in T["scene"]}
    tracklets, need, by = build_plan(T, [s for s in ranked if s in present])
    print("candidate tracklets", len(tracklets), "needed files", len(need), flush=True)
    got = set()
    for n, (fname, raw) in enumerate(iter_members(args, need)):
        process(raw, fname, need, tracklets, by, args.work, args.offset); got.add(fname)
        if n % 2000 == 0:
            print("files", n, flush=True)
    complete = {}
    for t in tracklets:
        ok = all(s["filename"] in got for s in t["sd"])
        complete[t["scene"]] = complete.get(t["scene"], True) and ok
    done = [s for s, ok in complete.items() if ok]
    open(os.path.join(args.out + "_complete_scenes.txt"), "w").write("\n".join(sorted(done)) + "\n")
    chosen = set(pick(ranked, done, args.n_target, args.n_min))
    idx = assemble(tracklets, chosen, args.work, args.out)
    print("scenes", len(chosen), "tracklets", len(idx), "keyframes", sum(t["n_key"] for t in idx),
          "sweeps", sum(t["n_sweep"] for t in idx))


if __name__ == "__main__":
    main()
