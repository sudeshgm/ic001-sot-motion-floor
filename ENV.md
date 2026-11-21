# CPU environment

- venv: `/workspace/ic001_venv` (outside the repo, not /tmp), Python 3.13.5 (box system python).
- Create: `python3 -m venv /workspace/ic001_venv && /workspace/ic001_venv/bin/pip install -r requirements-lock.txt`
- Tests (synthetic data only): `/workspace/ic001_venv/bin/python -m pytest -q`
- `nuscenes-devkit` is intentionally NOT installed: its pins (old shapely) do not build on
  Python 3.13. `ic001/data/nuscenes.py` reads the JSON tables directly; the val scene list
  is copied from nuscenes-devkit 1.2.0 `splits.py` (Apache-2.0).
- No torch on the CPU side. Learned trackers run on GPU only (see `gpu_jobs/`).
