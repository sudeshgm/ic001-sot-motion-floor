"""Allow nuscenes-devkit 1.1.9 to load a slim dataroot whose map.json is [].

The official NuScenes() constructor tries to open map-mask PNGs and
__make_reverse_index__ indexes self.map[0] and log.map_token. The IC001 slim
val-keyframes dataset has no maps/ directory. This patch is a no-op when the
map table is non-empty. It does not change tracker logic.
"""
_APPLIED = False


def apply():
    global _APPLIED
    if _APPLIED:
        return
    from nuscenes.nuscenes import NuScenes
    orig = NuScenes.__make_reverse_index__

    def _patched(self, verbose=True):
        saved = list(self.map)
        if not saved:
            # Dummy so the official self.map[0] / log_to_map lookups do not crash.
            # MapMask was already skipped in __init__ (empty table at that point).
            dummy = {
                "token": "__slim_nomap__",
                "log_tokens": [log["token"] for log in self.log],
                "filename": "maps/__slim_nomap__.png",
                "category": "semantic_prior",
            }
            self.map = [dummy]
        orig(self, verbose)
        if not saved:
            self.map = []
            if hasattr(self, "_token2ind") and isinstance(self._token2ind, dict):
                self._token2ind["map"] = {}
            for log_record in self.log:
                log_record["map_token"] = None
            if verbose:
                print("slim dataroot: map table empty, skipped log->map reverse index")

    NuScenes.__make_reverse_index__ = _patched
    _APPLIED = True
    print("patch_nuscenes_maps.apply(): patched NuScenes.__make_reverse_index__ for empty map.json")


if __name__ == "__main__":
    apply()
