from pathlib import Path

import torch
from box import Box

from .core import get_frame_index, load_data, load_frame
from .ops import stack
from .scene_frame import get_scene_frame_names


class BasicSceneframeDataset(torch.utils.data.Dataset):
    """Basic wai dataset to iterative over frames of scenes"""

    @staticmethod
    def collate_fn(batch):
        return stack(batch)

    def __init__(
        self,
        cfg: Box,
    ):
        super().__init__()
        self.cfg = cfg
        self.root = cfg.root
        self.scene_frame_names = get_scene_frame_names(cfg)
        self.scene_frame_list = [
            (scene_name, frame_name)
            for scene_name, frame_names in self.scene_frame_names.items()
            for frame_name in frame_names
        ]
        self._scene_cache = {}

    def __len__(self):
        return len(self.scene_frame_list)

    def _load_scene(self, scene_name):
        # load scene data
        scene_data = {}
        scene_data["meta"] = load_data(
            Path(
                self.root,
                scene_name,
                self.cfg.get("scene_meta_path", "scene_meta.json"),
            ),
            "scene_meta",
        )

        return scene_data

    def _load_scene_frame(self, scene_name, frame_name):
        scene_frame_data = {}
        if not (scene_data := self._scene_cache.get(scene_name)):
            scene_data = self._load_scene(scene_name)
            # for now only cache the last scene
            self._scene_cache = {}
            self._scene_cache[scene_name] = scene_data

        frame_idx = get_frame_index(scene_data["meta"], frame_name)

        scene_frame_data["scene_name"] = scene_name
        scene_frame_data["frame_name"] = frame_name
        scene_frame_data["scene_path"] = str(Path(self.root, scene_name))
        scene_frame_data["frame_idx"] = frame_idx
        scene_frame_data.update(
            load_frame(
                Path(self.root, scene_name),
                frame_name,
                modalities=self.cfg.frame_modalities,
                scene_meta=scene_data["meta"],
            )
        )
        # Remap key names
        for key, new_key in self.cfg.get("key_remap", {}).items():
            if key in scene_frame_data:
                scene_frame_data[new_key] = scene_frame_data.pop(key)

        return scene_frame_data

    def __getitem__(self, index):
        scene_frame = self._load_scene_frame(*self.scene_frame_list[index])
        return scene_frame
