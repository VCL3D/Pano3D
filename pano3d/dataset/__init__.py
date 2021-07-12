from pano3d.dataset.gibson_v2 import GibsonV2
from pano3d.dataset.matterport3d import Matterport3D

import torch
import toolz
import typing
import logging

log = logging.getLogger(__name__)

__all__ = ['Pano3D']

__DATASETS__ = {
    'm3d': Matterport3D,
    'gv2': GibsonV2,
}

def _split(dataset: str) -> typing.Tuple[str, str]:
    s = dataset.split('_')
    return toolz.first(s), toolz.second(s)

class Pano3D(torch.utils.data.ConcatDataset):
    def __init__(self,
        root:       str,
        datasets:   typing.Sequence[str],
        splits:     typing.Sequence[str],
        tensors:    typing.Sequence[str],
    ):
        super(Pano3D, self).__init__(
            __DATASETS__[d](root, p, s, tensors) for (d, p), s in zip(
                map(_split, datasets), 
                splits
            )
        )