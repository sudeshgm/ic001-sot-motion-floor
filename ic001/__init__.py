"""IC001 motion floor for LiDAR 3D single-object tracking (CPU side).

Status: scaffold. Tested on synthetic data only. Nothing in this package has
been run on real KITTI / nuScenes data. Scoring real data is blocked by
``ic001.guard.require_frozen_prereg`` until a frozen pre-registration exists.
"""
__version__ = "0.1.0"
