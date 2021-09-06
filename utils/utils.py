import torch
import functools
import logging


log = logging.getLogger(__name__)

__all__ = ["Interpolate"]

#NOTE: align corners doc: https://discuss.pytorch.org/t/what-we-should-use-align-corners-false/22663/12

class Interpolate(torch.nn.Module):
    __MODES__ = ['nearest', 'linear', 'bilinear', 'area', 'bicubic', 'trilinear']

    def __init__(self,
        scale:                  float=0.0,
        width:                  int=-1,
        height:                 int=-1,
        #TODO: support depth as well for volumetric interpolation
        mode:                   str='bilinear', # one of ['nearest', 'linear', 'bilinear', 'area', 'bicubic', 'trilinear']            
        align_corners:          bool=False,
        recompute_scale_factor: bool=False,
    ):
        super(Interpolate, self).__init__()
        #assert_choices(log, "interpolation mode", mode, Interpolate.__MODES__)
        if not scale > 0.0 and not (width > 0 and height > 0):
            log.error(f"Either scale ({scale}) or dimensions ([{width} x {height}]) need to be set for Interpolate.")
        self.func = functools.partial(
            torch.nn.functional.interpolate,
            scale_factor=scale, mode=mode, 
            align_corners=align_corners if mode != 'nearest' and mode != 'area' else None,
            recompute_scale_factor=recompute_scale_factor,
        ) if scale > 0.0 and width < 0 and height < 0 else\
            functools.partial(
                torch.nn.functional.interpolate,
                size=(height, width), mode=mode, 
                align_corners=align_corners if mode != 'nearest' and mode != 'area' else None,
                recompute_scale_factor=recompute_scale_factor,
            )

    def forward(self,
        image: torch.Tensor
    ) -> torch.Tensor:
        return self.func(image)