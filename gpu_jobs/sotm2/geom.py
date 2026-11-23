"""SOT-M2 Stage 1 geometry helpers (numpy + pyquaternion only; no torch).

Boxes are (center[3], wlh[3], quat_wxyz[4]) in the nuScenes global frame. Point arrays are (3, N).
Conventions follow the SOT-M2 inference-only kill test:
- sweep boxes are devkit-style interpolations between consecutive keyframe annotations
  (centre lerp, rotation slerp, size of the earlier keyframe);
- the tracker search region is the box enlarged by ``wlh * scale / 2 + offset`` per axis
  (M2-Track: scale 1.25, offset 2 m);
- buffer arm C keeps past-sweep points in the world frame (ego-motion compensated only);
- buffer arm D moves past-sweep points rigidly from the box at sweep j to the box at the current frame.
"""
import numpy as np
from pyquaternion import Quaternion


def interp_box(a_c, a_q, a_wlh, b_c, b_q, alpha):
    """Box at fraction ``alpha`` in [0, 1] between keyframe boxes a and b (size of a)."""
    a_c = np.asarray(a_c, float); b_c = np.asarray(b_c, float)
    c = (1.0 - alpha) * a_c + alpha * b_c
    q = Quaternion.slerp(Quaternion(np.asarray(a_q, float)), Quaternion(np.asarray(b_q, float)), amount=alpha)
    return c, np.asarray(a_wlh, float).copy(), q.elements


def corners(c, wlh, q):
    """8 corners (3, 8) of a nuScenes-convention box (x = length, y = width, z = height)."""
    w, l, h = wlh
    x = l / 2 * np.array([1, 1, 1, 1, -1, -1, -1, -1])
    y = w / 2 * np.array([1, -1, -1, 1, 1, -1, -1, 1])
    z = h / 2 * np.array([1, 1, -1, -1, 1, 1, -1, -1])
    R = Quaternion(np.asarray(q, float)).rotation_matrix
    return R @ np.vstack([x, y, z]) + np.asarray(c, float)[:, None]


def crop_axis_aligned(p, c, wlh, q, offset):
    """Open3DSOT preload crop: axis-aligned bounds of the box corners +/- offset (strict)."""
    cr = corners(c, wlh, q)
    mx = cr.max(1) + offset; mn = cr.min(1) - offset
    m = np.all((p > mn[:, None]) & (p < mx[:, None]), axis=0)
    return p[:, m]


def in_region(p, c, wlh, q, scale, offset):
    """Mask of points inside the tracker search region around the box."""
    R = Quaternion(np.asarray(q, float)).rotation_matrix
    loc = R.T @ (p - np.asarray(c, float)[:, None])
    wlh = np.asarray(wlh, float)
    half = wlh[[1, 0, 2]] * scale / 2 + offset  # box frame x = l, y = w, z = h
    return np.all(np.abs(loc) < half[:, None], axis=0)


def align(p, src_c, src_q, dst_c, dst_q):
    """Rigid move of points from the src box frame to the dst box frame."""
    Rs = Quaternion(np.asarray(src_q, float)).rotation_matrix
    Rd = Quaternion(np.asarray(dst_q, float)).rotation_matrix
    loc = Rs.T @ (p - np.asarray(src_c, float)[:, None])
    return Rd @ loc + np.asarray(dst_c, float)[:, None]


def buffer_points(sweeps, j, first_j, boxes, nbuf, scale, offset, aligned):
    """Points for frame j with up to ``nbuf - 1`` earlier sweeps (never before ``first_j``).

    sweeps: list of (3, N_i) arrays (world frame); boxes: list of (c, wlh, q) per sweep used both to crop
    the past sweeps to the search region and (if ``aligned``) to move them into the frame-j box.
    The current sweep is always kept whole (it is cropped later by the tracker itself).
    """
    parts = [sweeps[j]]
    lo = max(first_j, j - (nbuf - 1))
    for i in range(lo, j):
        p = sweeps[i]
        c, wlh, q = boxes[i]
        p = p[:, in_region(p, c, wlh, q, scale, offset)]
        if aligned:
            p = align(p, c, q, boxes[j][0], boxes[j][2])
        parts.append(p)
    return np.concatenate(parts, 1)
