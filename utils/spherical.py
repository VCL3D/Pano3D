from utils.grid import Grid

import torch
import numpy as np

class Spherical(Grid):
    __GRID_MAP__ = {
        'pi':               'ndc',
        'tau':              'norm', 
    }

    __ORDER_MAP__ = {
        'longlat':       'xy',
        'latlong':       'yx',
    }

    __SCALE_MAP__ = {
        'longlat': {
            'pi':       [np.pi, 0.5 * np.pi],
            'tau':      [2.0 * np.pi, np.pi],
        },
        'latlong': {
            'pi':       [0.5 * np.pi, np.pi],
            'tau':      [np.pi, 2.0 * np.pi],
        },
    }

    def __init__(self,
        mode:               str='pi', # one of ['pi', 'tau']
        width:              int=512,
        inclusive:          bool=False,
        order:              str='longlat', # one of ['longlat', 'latlong']
        long_offset_pi:     float=0.0, # offset for longitude, relative to pi
    ):
        super(Spherical, self).__init__(
            mode=Spherical.__GRID_MAP__[mode],
            width=width, height=width // 2, depth=1,
            inclusive=inclusive,
            order=Spherical.__ORDER_MAP__[order],
        )
        scale = torch.Tensor([Spherical.__SCALE_MAP__[order][mode]])
        self.grid = self.grid * scale.unsqueeze(-1).unsqueeze(-1)
        if long_offset_pi != 0.0:
            dim = 0 if order.startswith('long') else 1
            self.grid[:, dim, ...] += np.pi * long_offset_pi
