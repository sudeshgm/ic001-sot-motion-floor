"""SOT-M2 Stage 1 GPU harness: M2-Track (Open3DSOT f08451d) fine-tuning arms and causal evaluation.

Model code, losses and the training sample construction are Open3DSOT's own (``motion_processing``,
``compute_loss``, ``build_input_dict``, ``evaluate_one_sample``); only the point clouds fed to them change.

Modes
  rollout  pretrained checkpoint run causally at sweep rate (20 Hz) from the frame-0 GT box over every sweep
           of every tracklet in --data; writes rollout.npz (per tracklet: S x 7 = centre, quaternion).
  train    one arm, fixed optimizer-step budget, checkpoint every --block steps, resumable (--resume).
  eval     causal evaluation on --data (kill-test protocol); writes frames.csv, b_sweep_boxes.csv.

Training arms (identical batch, steps, optimizer, augmentation, seed):
  A_ft  keyframe pairs, single sweep (fine-tune control)
  I     sweep pairs (j-1, j) with devkit-interpolated GT boxes as labels (sweep-rate training)
  C     keyframe pairs, each frame = keyframe sweep + up to 9 earlier sweeps cut to the search region around
        the rollout box at that sweep, world frame (ego-motion compensated 10-sweep accumulation)
  D     as C, earlier-sweep points moved rigidly from the rollout box at sweep j to the rollout box at the
        keyframe (self-aligned target-frame buffer); loss only at keyframes
Eval arms: A (pretrained, keyframes), B (pretrained, sweep rate), A_ft, I (sweep rate), C, D (buffers built
from the pretrained B rollout boxes, as in the kill test).
"""
import argparse, csv, json, os, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from gpu_jobs.sotm2.geom import buffer_points  # noqa: E402

TRAIN_ARMS = ["A_ft", "I", "C", "D"]
EVAL_ARMS = ["A", "B", "A_ft", "I", "C", "D"]


class Sweeps:
    """Per-sweep (3, N) float64 views built on access from one float32 array (keeps RAM at the npz size)."""
    def __init__(self, P, off): self.P, self.off = P, off
    def __len__(self): return len(self.off) - 1
    def __getitem__(self, i): return self.P[self.off[i]:self.off[i + 1]].T.astype(np.float64)
    def __iter__(self): return (self[i] for i in range(len(self)))


def load_tracklets(data, keep=None):
    """Tracklets of --data. With SOTM2_CACHE set and keep=None, the decompressed points are cached once as one
    uncompressed .npy and memory-mapped by every later call (round-robin blocks; shared by loader workers)."""
    cache = os.environ.get("SOTM2_CACHE")
    if cache and keep is None:
        return _load_cached(data, cache)
    return _load(data, keep)


def _load_cached(data, cache):
    import hashlib, pickle
    cache = os.path.join(cache, hashlib.sha1(os.path.abspath(data).encode()).hexdigest()[:12])  # one per data dir
    os.makedirs(cache, exist_ok=True)
    fp, fm = os.path.join(cache, "pts_all.npy"), os.path.join(cache, "meta.pkl")
    if not (os.path.exists(fp) and os.path.exists(fm)):
        trk = _load(data, None)
        sizes = [len(t["sw"].P) for t in trk]
        mm = np.lib.format.open_memmap(fp + ".tmp", mode="w+", dtype=np.float32, shape=(sum(sizes), 3))
        o = 0
        for t, n in zip(trk, sizes):
            mm[o:o + n] = t["sw"].P; t["base"] = o; o += n
        mm.flush(); del mm
        meta = [{k: (v.off if k == "sw" else v) for k, v in t.items()} for t in trk]
        pickle.dump(meta, open(fm + ".tmp", "wb")); os.replace(fp + ".tmp", fp); os.replace(fm + ".tmp", fm)
    P = np.load(fp, mmap_mode="r"); meta = pickle.load(open(fm, "rb")); out = []
    for t in meta:
        off = t["sw"]; t = dict(t); b = t.pop("base")
        t["sw"] = Sweeps(P[b:b + off[-1]], off); out.append(t)
    return out


def _load(data, keep):
    idx = json.load(open(os.path.join(data, "index.json")))["tracklets"]
    out = []
    for t in idx:
        if keep is not None and not keep(t["tid"]):
            continue
        z = np.load(os.path.join(data, t["file"]))
        off = z["off"]; P = z["pts"].astype(np.float32)
        out.append(dict(tid=t["tid"], sw=Sweeps(P, off),
                        key_idx=[int(k) for k in z["key_idx"]],
                        gt=[(z["gc"][k], z["gw"][k], z["gq"][k]) for k in range(len(z["key_idx"]))],
                        interp=[(z["ic"][j], z["iw"][j], z["iq"][j]) for j in range(len(off) - 1)]))
    return out


def rollout_boxes(path, trk):
    """Attach rollout boxes (c, wlh, q) per sweep; wlh = interpolated GT size (M2-Track keeps the size).
    ``path`` is one rollout .npz or a directory of rollout_*of*.npz shards."""
    import glob
    files = sorted(glob.glob(os.path.join(path, "rollout_*of*.npz"))) if os.path.isdir(path) else [path]
    R = {}
    for f in files:
        z = np.load(f); R.update({k: z[k] for k in z.files})
    for t in trk:
        r = R[f"t{t['tid']}"]
        t["roll"] = [(r[j, :3], t["interp"][j][1], r[j, 3:7]) for j in range(len(t["sw"]))]


class Harness:
    def __init__(self, o3d, ckpt, device):
        sys.path.insert(0, o3d); os.chdir(o3d)
        import torch, yaml
        from easydict import EasyDict
        from nuscenes.utils.data_classes import Box
        from datasets.data_classes import PointCloud
        from datasets import points_utils
        from datasets.sampler import motion_processing
        from models import get_model
        from utils.metrics import estimateOverlap, estimateAccuracy
        self.torch, self.Box, self.PC = torch, Box, PointCloud
        self.points_utils, self.motion_processing = points_utils, motion_processing
        self.estimateOverlap, self.estimateAccuracy = estimateOverlap, estimateAccuracy
        cfg = EasyDict(yaml.load(open("cfgs/M2_Track_nuscene.yaml"), Loader=yaml.FullLoader))
        cfg.checkpoint = ckpt; self.cfg = cfg; self.device = device
        if device == "cpu":  # CPU smoke tests only (Open3DSOT hardcodes .cuda() in compute_loss)
            torch.nn.Module.cuda = lambda self, *a, **k: self
            torch.Tensor.cuda = lambda self, *a, **k: self
            from pytorch_lightning.utilities.device_dtype_mixin import DeviceDtypeModuleMixin
            DeviceDtypeModuleMixin.cuda = lambda self, *a, **k: self
        self.get_model = get_model

    def load(self, state=None):
        net = self.get_model(self.cfg.net_model).load_from_checkpoint(self.cfg.checkpoint, config=self.cfg,
                                                                      map_location="cpu")
        if state is not None:
            net.load_state_dict(self.torch.load(state, map_location="cpu")["model"])
        return net.to(self.device)

    def box(self, b):
        from pyquaternion import Quaternion
        return self.Box(np.asarray(b[0], float), np.asarray(b[1], float), Quaternion(np.asarray(b[2], float)))

    # ---------------- causal inference ----------------
    def run_chain(self, net, pcs, init_box):
        with self.torch.no_grad():
            seq = [{"pc": self.PC(p)} for p in pcs]; res = [init_box]
            for i in range(1, len(seq)):
                d, ref = net.build_input_dict(seq, i, res)
                res.append(net.evaluate_one_sample(d, ref_box=ref))
        return res

    def frame_pcs(self, t, arm, boxes=None):
        c = self.cfg; ki = t["key_idx"]
        if arm in ("A", "A_ft"):
            return [t["sw"][j] for j in ki]
        if arm in ("B", "I"):
            return list(t["sw"])
        return [buffer_points(t["sw"], j, ki[0], boxes, 10, c.bb_scale, c.bb_offset, aligned=(arm == "D")) for j in ki]

    # ---------------- training samples ----------------
    def sample(self, t, arm, k, cand):
        """One Open3DSOT motion_processing sample. k indexes keyframes (arms A_ft/C/D) or sweeps (arm I)."""
        c = self.cfg; ki = t["key_idx"]
        if arm == "I":
            pp, tp = t["sw"][k - 1], t["sw"][k]; pb, tb = t["interp"][k - 1], t["interp"][k]
        else:
            pb, tb = t["gt"][k - 1], t["gt"][k]
            if arm == "A_ft":
                pp, tp = t["sw"][ki[k - 1]], t["sw"][ki[k]]
            else:
                al = arm == "D"
                pp = buffer_points(t["sw"], ki[k - 1], ki[0], t["roll"], 10, c.bb_scale, c.bb_offset, al)
                tp = buffer_points(t["sw"], ki[k], ki[0], t["roll"], 10, c.bb_scale, c.bb_offset, al)
        data = {"prev_frame": {"pc": self.PC(pp.copy()), "3d_bbox": self.box(pb)},
                "this_frame": {"pc": self.PC(tp.copy()), "3d_bbox": self.box(tb)}, "candidate_id": cand}
        tf = self.points_utils.apply_augmentation if c.use_augmentation else None
        return self.motion_processing(data, c, template_transform=tf, search_transform=tf)


def pair_table(trk, arm):
    """(tracklet position, k) for every training pair of the arm, in a fixed order."""
    if arm == "I":
        return [(n, j) for n, t in enumerate(trk) for j in range(1, len(t["sw"]))]
    return [(n, k) for n, t in enumerate(trk) for k in range(1, len(t["key_idx"]))]


def draw(seed, arm_pairs_len, gidx, attempt, num_candidates=4):
    """Deterministic (pair, candidate) for global sample index; same stream for every keyframe arm."""
    r = np.random.default_rng([seed, gidx, attempt])
    return int(r.integers(arm_pairs_len)), int(r.integers(num_candidates)), int(r.integers(2 ** 31 - 1))


def make_dataset(H, trk, arm, seed, start, n):
    import torch
    pairs = pair_table(trk, arm)

    class DS(torch.utils.data.Dataset):
        def __len__(self): return n

        def __getitem__(self, i):
            g = start + i
            for attempt in range(50):
                p, cand, s = draw(seed, len(pairs), g, attempt)
                np.random.seed(s)
                tn, k = pairs[p]
                try:
                    return H.sample(trk[tn], arm, k, cand)
                except AssertionError:
                    continue
            raise RuntimeError("no valid sample after 50 attempts")
    return DS()


def train(args):
    H = Harness(args.o3d, args.ckpt, args.device); torch = H.torch
    trk = load_tracklets(args.data)
    if args.arm in ("C", "D"):
        rollout_boxes(args.rollout, trk)
    torch.manual_seed(args.seed)
    net = H.load(); net.train()
    opt = torch.optim.Adam(net.parameters(), lr=args.lr, betas=(0.5, 0.999), eps=1e-06, weight_decay=0)
    os.makedirs(args.out, exist_ok=True)
    ck = os.path.join(args.out, f"{args.arm}_last.pt"); step = 0
    if os.path.exists(ck):
        s = torch.load(ck, map_location="cpu"); net.load_state_dict(s["model"]); opt.load_state_dict(s["opt"]); step = s["step"]
    log = open(os.path.join(args.out, f"{args.arm}_train_log.csv"), "a"); t0 = time.time()
    stop_at = min(args.steps, step + args.block) if args.one_block else args.steps
    while step < stop_at:
        n = min(args.block, stop_at - step) * args.batch
        ds = make_dataset(H, trk, args.arm, args.seed, step * args.batch, n)
        dl = torch.utils.data.DataLoader(ds, batch_size=args.batch, shuffle=False, num_workers=args.workers,
                                         drop_last=True, worker_init_fn=lambda w: np.random.seed(args.seed + w))
        for batch in dl:
            batch = {k: v.to(H.device) for k, v in batch.items()}
            out = net(batch); loss = net.compute_loss(batch, out)["loss_total"]
            if not torch.isfinite(loss):
                raise SystemExit(f"FAIL non-finite loss arm={args.arm} step={step}")
            opt.zero_grad(); loss.backward(); opt.step(); step += 1
            if step % 50 == 0 or step == stop_at:
                log.write(f"{step},{loss.item():.5f},{time.time() - t0:.1f}\n"); log.flush()
        torch.save({"model": net.state_dict(), "opt": opt.state_dict(), "step": step, "arm": args.arm,
                    "seed": args.seed, "batch": args.batch, "lr": args.lr}, ck + ".tmp")
        os.replace(ck + ".tmp", ck)
        print(f"arm={args.arm} step={step}/{args.steps} t={time.time() - t0:.0f}s", flush=True)
    if step >= args.steps:
        torch.save({"model": net.state_dict(), "step": step}, os.path.join(args.out, f"{args.arm}_final.pt"))


def rollout(args):
    H = Harness(args.o3d, args.ckpt, args.device)
    si, sn = map(int, args.shard.split("/"))
    tids = [t["tid"] for t in json.load(open(os.path.join(args.data, "index.json")))["tracklets"] if t["tid"] % sn == si]
    net = H.load().eval(); res = {}; t0 = time.time()
    for n, tid in enumerate(tids):  # one tracklet in memory at a time
        t = load_tracklets(args.data, keep=lambda x: x == tid)[0]
        bs = H.run_chain(net, list(t["sw"]), H.box(t["gt"][0]))
        res[f"t{t['tid']}"] = np.array([np.r_[b.center, b.orientation.elements] for b in bs], np.float64)
        if n % 20 == 0:
            print(f"rollout {n + 1}/{len(tids)} t={time.time() - t0:.0f}s", flush=True)
    os.makedirs(args.out, exist_ok=True)
    np.savez_compressed(os.path.join(args.out, f"rollout_{si}of{sn}.npz"), **res)


def evaluate(args):
    from pyquaternion import Quaternion
    H = Harness(args.o3d, args.ckpt, args.device)
    keep = set(map(int, args.tids.split(","))) if args.tids else None
    trk = load_tracklets(args.data, keep=(lambda tid: tid in keep) if keep else None)
    arms = args.arms.split(",")
    nets = {"A": H.load().eval()}
    for a in arms:
        if a in TRAIN_ARMS:
            nets[a] = H.load(os.path.join(args.models, f"{a}_final.pt")).eval()
    os.makedirs(args.out, exist_ok=True)
    fw = open(os.path.join(args.out, "frames.csv"), "w", newline=""); W = csv.writer(fw)
    W.writerow(["tid", "k", "arm", "iou", "dist", "cx", "cy", "cz", "yaw"])
    fb = open(os.path.join(args.out, "b_sweep_boxes.csv"), "w", newline=""); WB = csv.writer(fb)
    WB.writerow(["tid", "j", "cx", "cy", "cz", "qw", "qx", "qy", "qz"])
    t0 = time.time(); IOU, UP = H.cfg.IoU_space, H.cfg.up_axis
    for n, t in enumerate(trk):
        gt = [H.box(b) for b in t["gt"]]; preds = {}
        bsw = H.run_chain(nets["A"], H.frame_pcs(t, "B"), gt[0])
        for j, b in enumerate(bsw):
            WB.writerow([t["tid"], j, *np.round(b.center, 4), *np.round(b.orientation.elements, 6)])
        bboxes = [(b.center, b.wlh, b.orientation.elements) for b in bsw]
        for a in arms:
            if a == "B":
                preds[a] = [bsw[j] for j in t["key_idx"]]; continue
            net = nets["A" if a == "A" else a]
            r = H.run_chain(net, H.frame_pcs(t, a, bboxes), gt[0])
            preds[a] = [r[j] for j in t["key_idx"]] if a == "I" else r
        for a in arms:
            for k, b in enumerate(preds[a]):
                W.writerow([t["tid"], k, a, round(float(H.estimateOverlap(gt[k], b, dim=IOU, up_axis=UP)), 6),
                            round(float(H.estimateAccuracy(gt[k], b, dim=IOU, up_axis=UP)), 5),
                            *np.round(b.center, 4), round(float(Quaternion(matrix=b.rotation_matrix).yaw_pitch_roll[0]), 6)])
        fw.flush(); fb.flush()
        print(f"[{n + 1}/{len(trk)}] tid={t['tid']} t={time.time() - t0:.0f}s", flush=True)
    fw.close(); fb.close()
    json.dump(dict(arms=arms, n_tracklets=len(trk), wall_s=time.time() - t0, device=args.device),
              open(os.path.join(args.out, "eval_meta.json"), "w"), indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["rollout", "train", "eval"])
    ap.add_argument("--o3d", required=True); ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda"); ap.add_argument("--arm", choices=TRAIN_ARMS)
    ap.add_argument("--rollout", default="", help="rollout .npz or directory of shards")
    ap.add_argument("--shard", default="0/1", help="rollout shard i/n (tracklets with tid %% n == i)"); ap.add_argument("--models", default="")
    ap.add_argument("--arms", default=",".join(EVAL_ARMS)); ap.add_argument("--tids", default="")
    ap.add_argument("--steps", type=int, default=3000); ap.add_argument("--block", type=int, default=500)
    ap.add_argument("--one-block", action="store_true", help="train one block then exit (round-robin driver)")
    ap.add_argument("--batch", type=int, default=100); ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args(argv)
    for k in ("o3d", "ckpt", "data", "out", "rollout", "models"):
        v = getattr(args, k)
        if v: setattr(args, k, os.path.abspath(v))
    {"rollout": rollout, "train": train, "eval": evaluate}[args.mode](args)


if __name__ == "__main__":
    main()
