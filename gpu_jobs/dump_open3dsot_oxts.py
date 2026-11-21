"""UNTESTED harness (no GPU on the CPU box). SECONDARY, not part of the
frozen GO / KILL decision or of V1. Run from the Open3DSOT repo root:

  python /path/to/ic001/gpu_jobs/dump_open3dsot_oxts.py --cfg cfgs/M2_track_kitti.yaml \
      --checkpoint pretrained_models/mmtrack_kitti_car.ckpt --category Car \\
      --path /kaggle/input/ic001-kitti-0019-0020/kitti \\
      --protocols ope reinit --out m2track_oxts_kitti_car.csv

M2-Track only. Before cropping, the previous box and the previous-frame
crop are mapped into the current Velodyne frame by oxts T_t^{-1} · T_{t-1}.
Box orientation is yaw-only (PREREG choice (o); same as ic001.geometry.compensate_box).
The compensated box is the ref_box for getOffsetBB, so the dumped boxes
are already in the current Velodyne frame (IC001 schema, gpu_jobs/README.md).

Requires oxts/<scene>.txt and calib Tr_imu_velo under --path. Missing oxts
is a hard error (do not silently fall back to the uncompensated crop).
"""
import argparse
import copy
import csv
import os

import numpy as np
import torch
import yaml
from easydict import EasyDict
from pyquaternion import Quaternion

from datasets import get_dataset, points_utils
from datasets.data_classes import PointCloud
from models import get_model
from nuscenes.utils import geometry_utils
from utils.metrics import TorchPrecision, TorchSuccess, estimateAccuracy, estimateOverlap

FIELDS = ["dataset", "category", "tracklet_id", "frame_idx", "protocol", "method",
          "cx", "cy", "cz", "w", "l", "h", "yaw"]

METHOD = "m2track_oxts"


def tracklet_id(cfg, seq):
    m = seq[0]["meta"]
    if cfg.dataset == "kitti":
        return "%04d_%d" % (int(m["scene"]), int(m["track_id"]))
    return m["box_anno"]["instance_token"]


def _h(m34):
    return np.vstack([m34, [0, 0, 0, 1]])


def read_calib(path):
    """KITTI tracking calib; keys stripped of a trailing colon."""
    out = {}
    with open(path) as f:
        for line in f:
            vals = line.replace(":", " ").split()
            if not vals:
                continue
            try:
                arr = np.array([float(x) for x in vals[1:]])
            except ValueError:
                continue
            if arr.size == 12:
                out[vals[0]] = arr.reshape(3, 4)
            elif arr.size == 9:
                out[vals[0]] = arr.reshape(3, 3)
    return out


def oxts_poses(path):
    """KITTI devkit convertOxtsToPose; first pose translated to the origin.

    Same convention as ic001.data.kitti.oxts_poses (relative motion only).
    """
    data = np.loadtxt(path, ndmin=2)
    lat, lon, alt = data[:, 0], data[:, 1], data[:, 2]
    roll, pitch, yaw = data[:, 3], data[:, 4], data[:, 5]
    er = 6378137.0
    scale = np.cos(lat[0] * np.pi / 180.0)
    tx = scale * lon * np.pi * er / 180.0
    ty = scale * er * np.log(np.tan((90.0 + lat) * np.pi / 360.0))
    poses = np.zeros((len(data), 4, 4))
    for i in range(len(data)):
        cr, sr = np.cos(roll[i]), np.sin(roll[i])
        cp, sp = np.cos(pitch[i]), np.sin(pitch[i])
        cy, sy = np.cos(yaw[i]), np.sin(yaw[i])
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
        poses[i, :3, :3] = Rz @ Ry @ Rx
        poses[i, :3, 3] = [tx[i], ty[i], alt[i]]
        poses[i, 3, 3] = 1.0
    poses[:, :3, 3] -= poses[0, :3, 3]
    return poses


def load_T_world_velo(kitti_root, scene):
    """(F, 4, 4) world-from-velodyne poses for one KITTI scene (e.g. '0019')."""
    scene = "%04d" % int(scene)
    oxts_path = os.path.join(kitti_root, "oxts", scene + ".txt")
    calib_path = os.path.join(kitti_root, "calib", scene + ".txt")
    if not os.path.isfile(oxts_path):
        raise FileNotFoundError(
            "oxts file missing: %s  (add oxts/ to the private Kaggle dataset "
            "ic001-kitti-0019-0020 and re-verify kitti_sha256.txt; do not fall "
            "back to an uncompensated crop)" % oxts_path)
    calib = read_calib(calib_path)
    if "Tr_imu_velo" not in calib:
        raise KeyError("Tr_imu_velo missing from %s" % calib_path)
    imu_to_velo = _h(calib["Tr_imu_velo"])
    return oxts_poses(oxts_path) @ np.linalg.inv(imu_to_velo)


def relative_sensor_transform(T_from, T_to):
    """T_to^{-1} @ T_from: previous velodyne -> current velodyne."""
    return np.linalg.inv(T_to) @ T_from


def compensate_nuscenes_box(box, T):
    """Map an Open3DSOT/nuScenes Box by T; centre full rigid, yaw-only orientation.

    Do not use Box.transform: the copy in Open3DSOT data_classes.py applies a
    transposed 3x4 to the centre. Matches ic001.geometry.compensate_box.
    """
    box = copy.deepcopy(box)
    c = np.asarray(box.center, dtype=float)
    box.center = T[:3, :3] @ c + T[:3, 3]
    dyaw = float(np.arctan2(T[1, 0], T[0, 0]))
    box.orientation = Quaternion(axis=[0, 0, 1], radians=dyaw) * box.orientation
    return box


def compensate_pc(pc, T):
    new_pc = PointCloud(pc.points.copy())
    new_pc.transform(T)
    return new_pc


class PoseCache:
    def __init__(self, kitti_root):
        self.root = kitti_root
        self._by_scene = {}

    def pose(self, meta):
        scene = "%04d" % int(meta["scene"])
        frame = int(meta["frame"])
        if scene not in self._by_scene:
            self._by_scene[scene] = load_T_world_velo(self.root, scene)
        poses = self._by_scene[scene]
        if frame < 0 or frame >= len(poses):
            raise IndexError("oxts frame %d out of range for scene %s (n=%d)"
                             % (frame, scene, len(poses)))
        return poses[frame]


def build_input_dict_oxts(net, sequence, frame_id, results_bbs, poses):
    """MotionBaseModel.build_input_dict with oxts compensation of the previous
    box and previous crop into the current Velodyne frame before cropping.
    """
    assert frame_id > 0, "no need to construct an input_dict at frame 0"
    prev_frame = sequence[frame_id - 1]
    this_frame = sequence[frame_id]
    T_rel = relative_sensor_transform(
        poses.pose(prev_frame["meta"]), poses.pose(this_frame["meta"]))
    ref_box = compensate_nuscenes_box(results_bbs[-1], T_rel)
    prev_pc = compensate_pc(prev_frame["pc"], T_rel)
    this_pc = this_frame["pc"]
    prev_frame_pc = points_utils.generate_subwindow(
        prev_pc, ref_box, scale=net.config.bb_scale, offset=net.config.bb_offset)
    this_frame_pc = points_utils.generate_subwindow(
        this_pc, ref_box, scale=net.config.bb_scale, offset=net.config.bb_offset)
    canonical_box = points_utils.transform_box(ref_box, ref_box)
    prev_points, _ = points_utils.regularize_pc(
        prev_frame_pc.points.T, net.config.point_sample_size, seed=1)
    this_points, _ = points_utils.regularize_pc(
        this_frame_pc.points.T, net.config.point_sample_size, seed=1)
    seg_mask_prev = geometry_utils.points_in_box(
        canonical_box, prev_points.T, 1.25).astype(float)
    if frame_id != 1:
        seg_mask_prev[seg_mask_prev == 0] = 0.2
        seg_mask_prev[seg_mask_prev == 1] = 0.8
    seg_mask_this = np.full(seg_mask_prev.shape, fill_value=0.5)
    timestamp_prev = np.full((net.config.point_sample_size, 1), fill_value=0)
    timestamp_this = np.full((net.config.point_sample_size, 1), fill_value=0.1)
    prev_points = np.concatenate(
        [prev_points, timestamp_prev, seg_mask_prev[:, None]], axis=-1)
    this_points = np.concatenate(
        [this_points, timestamp_this, seg_mask_this[:, None]], axis=-1)
    stack_points = np.concatenate([prev_points, this_points], axis=0)
    data_dict = {"points": torch.tensor(
        stack_points[None, :], device=net.device, dtype=torch.float32)}
    if getattr(net.config, "box_aware", False):
        candidate_bc_prev = points_utils.get_point_to_box_distance(
            stack_points[:net.config.point_sample_size, :3], canonical_box)
        candidate_bc_this = np.zeros_like(candidate_bc_prev)
        candidate_bc = np.concatenate([candidate_bc_prev, candidate_bc_this], axis=0)
        data_dict.update({"candidate_bc": points_utils.np_to_torch_tensor(
            candidate_bc.astype("float32"), device=net.device)})
    return data_dict, ref_box


def run_sequence(net, seq, protocol, poses):
    ious, dists, out = [], [], []
    for t in range(len(seq)):
        gt = seq[t]["3d_bbox"]
        if t == 0:
            out.append(gt)
        else:
            hist = [s["3d_bbox"] for s in seq[:t]] if protocol == "reinit" else out
            data_dict, ref_bb = build_input_dict_oxts(net, seq, t, hist, poses)
            out.append(net.evaluate_one_sample(data_dict, ref_box=ref_bb))
        ious.append(estimateOverlap(gt, out[-1], dim=net.config.IoU_space, up_axis=net.config.up_axis))
        dists.append(estimateAccuracy(gt, out[-1], dim=net.config.IoU_space, up_axis=net.config.up_axis))
    return out, ious, dists


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--path", required=True, help="KITTI root (must contain oxts/ and calib/)")
    ap.add_argument("--protocols", nargs="+", default=["ope", "reinit"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--method", default=METHOD,
                    help="CSV method label (default m2track_oxts)")
    a = ap.parse_args()
    cfg = EasyDict(yaml.load(open(a.cfg), Loader=yaml.FullLoader))
    cfg.update(dict(category_name=a.category, preloading=False, test=True, checkpoint=a.checkpoint))
    cfg.path = a.path
    if getattr(cfg, "dataset", "kitti") != "kitti":
        raise ValueError("dump_open3dsot_oxts.py is KITTI / M2-Track only")
    net = get_model(cfg.net_model).load_from_checkpoint(a.checkpoint, config=cfg).cuda().eval()
    # M2TRACK subclasses MotionBaseModel; refuse a silent BAT/P2B run.
    bases = [c.__name__ for c in type(net).__mro__]
    if "MotionBaseModel" not in bases:
        raise TypeError(
            "oxts-compensated crop is defined for M2-Track (MotionBaseModel); "
            "got %s (%s)" % (type(net).__name__, bases))
    data = get_dataset(cfg, type="test", split=cfg.test_split)
    poses = PoseCache(a.path)
    with open(a.out, "w", newline="") as f, torch.no_grad():
        w = csv.writer(f); w.writerow(FIELDS)
        for proto in a.protocols:
            succ, prec = TorchSuccess(), TorchPrecision()
            for i in range(len(data)):
                seq = data[i]
                boxes, ious, dists = run_sequence(net, seq, proto, poses)
                succ(torch.tensor(ious)); prec(torch.tensor(dists))
                tid = tracklet_id(cfg, seq)
                for k, b in enumerate(boxes):
                    w.writerow([cfg.dataset, a.category, tid, k, proto, a.method,
                                *map(float, b.center), *map(float, b.wlh),
                                float(b.orientation.yaw_pitch_roll[0])])
            print(f"{proto}: Success {succ.compute():.2f} Precision {prec.compute():.2f}  "
                  f"[SECONDARY m2track_oxts; not V1, not GO/KILL]")


if __name__ == "__main__":
    main()
