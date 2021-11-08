import os
import sys
import torch
import toolz
import yaml
import pathlib
import typing
import logging
import functools

from loaders import (
    load_color,
    load_depth,
    load_normal,
    load_semantic,
    load_structure,
    load_layout,
)

log = logging.getLogger(__name__)

__all__ = ['Pano3D']

class Pano3D(torch.utils.data.Dataset):

    __LOADERS__ = {
        'color': load_color,
        'raw': load_color,
        'emission': load_color,
        'depth': load_depth,
        'normal': load_normal,
        'semantic': load_semantic,
        'structure': load_structure,
        'layout': load_layout,
        'color_up': functools.partial(load_color, position='up'),
        'color_down': functools.partial(load_color, position='down'),
        'color_left': functools.partial(load_color, position='left'),
        'color_right': functools.partial(load_color, position='right'),
        'depth_up': functools.partial(load_depth, position='up'),
        'depth_down': functools.partial(load_depth, position='down'),
        'depth_left': functools.partial(load_depth, position='left'),
        'depth_right': functools.partial(load_depth, position='right'),
        'normal_up': functools.partial(load_normal, position='up'),
        'normal_down': functools.partial(load_normal, position='down'),
        'normal_left': functools.partial(load_normal, position='left'),
        'normal_right': functools.partial(load_normal, position='right'),
        'semantic_up': functools.partial(load_semantic, position='up'),
        'semantic_down': functools.partial(load_semantic, position='down'),
        'semantic_left': functools.partial(load_semantic, position='left'),
        'semantic_right': functools.partial(load_semantic, position='right'),
        'structure_up': functools.partial(load_structure, position='up'),
        'structure_down': functools.partial(load_structure, position='down'),
        'structure_left': functools.partial(load_structure, position='left'),
        'structure_right': functools.partial(load_structure, position='right'),
        'layout_up': functools.partial(load_layout, position='up'),
        'layout_down': functools.partial(load_layout, position='down'),
        'layout_left': functools.partial(load_layout, position='left'),
        'layout_right': functools.partial(load_layout, position='right'),
    }

    def __init__(self,
        root:       typing.Union[str, pathlib.Path],
        part:       str,
        split:      typing.Union[str, pathlib.Path],
        types:      typing.Sequence[str],
        max_depth:  float=8.0,
    ):
        folder = self._get_folder(root, part)
        self.filenames = self._get_filenames(folder, split)
        self.loaders = [
            functools.partial(Pano3D.__LOADERS__[type], 
                max_depth=max_depth
            ) for type in types
        ]

    def _get_folder(self, root: typing.Union[str, pathlib.Path], part: str) -> str:
        if not os.path.exists(root):
            log.error((
                f"Invalid Pano3D root folder ({root}), "
                "please use the folder where the Zenodo archives have been extracted to."
            ))
            sys.exit(2)
        part_path = os.path.join(root, part)
        if not os.path.exists(part_path):
            log.error((
                "Invalid Pano3D part folder, "
                f"please use the correct part folder's name inside the root directory ({root})."
            ))
            sys.exit(2)
        return part_path

    def _get_filenames(self,
        folder: str, split: typing.Union[str, pathlib.Path]
    ) -> typing.Sequence[typing.Union[str, pathlib.Path]]:
        if not os.path.exists(split):
            log.error((
                f"Pano3D split file ({split}) does not exist. "
            ))
            sys.exit(2)
        with open(split) as f:
            data_filenames = yaml.load(f, Loader=yaml.FullLoader)
        filenames = []
        for building, renders in data_filenames.items():
            for render in renders:
                filenames.append(os.path.join(folder, building, render))
        return filenames

    def __len__(self) -> int:
        return len(self.filenames)

    def __getitem__(self, index: int) -> typing.Mapping[str, torch.Tensor]:
        out = { }
        filename = self.filenames[index]
        for loader in self.loaders:
            out = toolz.merge(out, loader(filename))
        return out

if __name__ == "__main__":
    import argparse
    def parse_arguments(args):
        usage_text = (
            "Test Pano3D data loading."
        )
        parser = argparse.ArgumentParser(description=usage_text)
        parser.add_argument("--pano3d_root", type=str, help="Path to the root folder containing the Pano3D extracted data.")
        parser.add_argument("--pano3d_part", type=str, help="The Pano3D subset to load.")
        parser.add_argument("--pano3d_split", type=str, help="The Pano3D split corresponding to the selected subset that will be loaded.")
        parser.add_argument('--pano3d_types', default='color', nargs='+',
            choices=[
                'color', 'depth', 'normal', 'semantic', 'structure', 'layout',
                'color_up', 'depth_up', 'normal_up', 'semantic_up', 'structure_up', 'layout_up'
                'color_down', 'depth_down', 'normal_down', 'semantic_down', 'structure_down', 'layout_down'
                'color_left', 'depth_left', 'normal_left', 'semantic_left', 'structure_left', 'layout_left'
                'color_right', 'depth_right', 'normal_right', 'semantic_right', 'structure_right', 'layout_right'
            ],
            help='The Pano3D data types that will be loaded, one of [color, depth, normal, semantic, structure, layout], potentially suffixed with a stereo placement from [up, down, left, right].'
        )
        return parser.parse_known_args(args)
    args, unknown = parse_arguments(sys.argv)
    dataset = Pano3D(
        root=args.pano3d_root,
        part=args.pano3d_part,
        split=args.pano3d_split,
        types=args.pano3d_types,
    )
    print(f"Loaded {len(dataset)} items.")