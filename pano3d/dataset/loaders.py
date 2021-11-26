import typing
import torch
from torch.functional import norm
import torchvision
import cv2
import numpy
import os

def load_color(filename: str, **kwargs) -> torch.Tensor:    
    if 'position' in kwargs:
        filename = filename.replace('center', kwargs['position'])
    return {'color': torchvision.io.read_image(filename) / 255.0 }    

def load_depth(filename: str, max_depth: float=8.0, **kwargs) -> torch.Tensor:
    if 'position' in kwargs:
        filename = filename.replace('center', kwargs['position'])
    depth_filename = filename.replace('emission', 'depth').replace('.png', '.exr')
    if 'filmic' in os.path.split(depth_filename)[-3]:
        depth_filename = depth_filename.replace('_filmic', '')
    depth = torch.from_numpy(
        cv2.imread(depth_filename, cv2.IMREAD_ANYDEPTH)
    ).unsqueeze(0)
    #NOTE: add a micro meter to allow for thresholding to extact the valid mask
    depth[depth > max_depth] = max_depth + 1e-6
    return {
        'depth': depth
    }

def load_normal(filename: str, **kwargs) -> torch.Tensor:
    if 'position' in kwargs:
        filename = filename.replace('center', kwargs['position'])
    normal_filename = filename.replace('emission', 'normal_map').replace('.png', '.exr')
    if 'filmic' in os.path.split(normal_filename)[-3]:
        normal_filename = normal_filename.replace('_filmic', '')
    return {
        'normal': torch.from_numpy(cv2.imread(normal_filename, 
            cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR
        ).transpose(2, 0, 1))
    }

def load_semantic(filename: str, **kwargs) -> torch.Tensor:
    if 'position' in kwargs:
        filename = filename.replace('center', kwargs['position'])
    return {
        'semantic': torch.from_numpy(cv2.imread(
            filename.replace('emission', 'semantic_map').replace('.png', '.exr')
        )).long()[:,:,0]
    }

def load_structure(filename: str, **kwargs) -> torch.Tensor:
    if 'position' in kwargs:
        filename = filename.replace('center', kwargs['position'])
    return { 
        'structure': torch.from_numpy(cv2.imread(
            filename.replace('emission', 'layout').replace('.png', '.exr')
        )).long()
    }

def load_layout(filename: str, **kwargs) -> typing.Mapping[str, torch.Tensor]:
    if 'position' in kwargs:
        filename = filename.replace('center', kwargs['position'])
    ret = { }
    with numpy.load(filename) as f:
        layout = f['arr_0.npy']
    ret["top_layout"] = torch.from_numpy(layout[0, ...])
    ret["top_weights"] = (ret["top_layout"] > 0).float()
    ret["top_layout"] = (128. - ret["top_layout"]) / 128.
    ret["bottom_layout"] = torch.from_numpy(layout[1, ...])
    ret["bottom_weights"] = (ret["bottom_layout"] > 0).float()
    ret["bottom_layout"] = (ret["bottom_layout"] - 128.) / 128.
    ret["top_layout"] *= ret["top_weights"]
    ret["bottom_layout"] *= ret["bottom_weights"]
    return ret
