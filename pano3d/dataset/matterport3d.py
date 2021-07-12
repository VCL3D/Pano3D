import torch
import os
import glob
import typing
import logging

log = logging.getLogger(__name__)

__all__ = ['Matterport3D']

__FILE_MAP__ = {
    'color': 'emission',
    'depth': 'depth',
    'normal': 'normal_map',
}

class Matterport3D(torch.utils.data.Dataset):
    def __init__(self,
        root:       str,
        partition:  str,
        split:      str,
        tensors:    typing.Sequence[str],
    ):
        self.filenames = glob.glob(os.path.join(root, "**/*emission*.png"))
        

    def __len__(self) -> int:
        return len(self.filenames)

    def __getitem__(self, index: int) -> typing.Dict[str, torch.Tensor]:
        pass