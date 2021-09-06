# import moai.networks.lightning as minet
# import moai.nn.convolution as mic
# import moai.nn.sampling.spatial.downsample as mids
# import moai.nn.sampling.spatial.upsample as mius

import torch
import numpy as np
import functools
import omegaconf.omegaconf as omegaconf
import typing
import logging

log = logging.getLogger(__name__)

__all__ = ["UNet"]


class Upsample2d(torch.nn.Module):
    def __init__(self,
        resolution: typing.Sequence[int]=None,
        scale: float=2.0,        
        mode: str="bilinear",
    ):
        super(Upsample2d, self).__init__()
        if resolution:
            self.upsample = functools.partial(torch.nn.functional.interpolate,
                size=tuple(resolution),
                mode=mode
            )
        else:
            self.upsample = functools.partial(torch.nn.functional.interpolate,
                scale_factor=scale,
                mode=mode
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.upsample(x)

class AntialiasedMaxPool2d(torch.nn.MaxPool2d):
    def __init__(self,
        features: int,
        kernel_size: int=2,
        stride: int=2,
        padding: int=0,
        pad_type: str='reflect',
    ):
        super(AntialiasedMaxPool2d, self).__init__(
            kernel_size, stride=1, padding=int(np.ceil(1.0 * (kernel_size - 1.0) / 2.0))
        )
        self.filt_size = kernel_size
        self.pad_off = 0
        self.pad_sizes = [
            int(1.0 * (kernel_size - 1) / 2.0), int(np.ceil(1.0 * (kernel_size - 1.0) / 2.0)),
            int(1.0 * (kernel_size - 1) / 2.0), int(np.ceil(1.0 * (kernel_size - 1) / 2.0))
        ]
        self.pad_sizes = [pad_size + self.pad_off for pad_size in self.pad_sizes]
        self.aa_stride = stride if stride else kernel_size #NOTE: different name due to subclassing
        self.off = int((self.aa_stride - 1) / 2.0)
        self.channels = features

        if(self.filt_size==1):
            a = np.array([1.,])
        elif(self.filt_size==2):
            a = np.array([1., 1.])
        elif(self.filt_size==3):
            a = np.array([1., 2., 1.])
        elif(self.filt_size==4):    
            a = np.array([1., 3., 3., 1.])
        elif(self.filt_size==5):    
            a = np.array([1., 4., 6., 4., 1.])
        elif(self.filt_size==6):    
            a = np.array([1., 5., 10., 10., 5., 1.])
        elif(self.filt_size==7):    
            a = np.array([1., 6., 15., 20., 15., 6., 1.])

        filt = torch.Tensor(a[:,None] * a[None,:])
        filt = filt / torch.sum(filt)
        self.register_buffer('filter', filt[None,None,:,:].repeat((self.channels, 1, 1, 1)))
        self.pad = self._get_pad_layer(pad_type)(self.pad_sizes)

    def _get_pad_layer(self, pad_type: str):
        if(pad_type in ['refl', 'reflect']):
            PadLayer = torch.nn.ReflectionPad2d
        elif(pad_type in ['repl', 'replicate']):
            PadLayer = torch.nn.ReplicationPad2d
        elif(pad_type=='zero'):
            PadLayer = torch.nn.ZeroPad2d
        else:
            log.error('Pad type [%s] not recognized' % pad_type)
        return PadLayer

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        pooled = super(AntialiasedMaxPool2d, self).forward(input)
        if(self.kernel_size==1):
            if(self.pad_off==0):
                return pooled[:,:,::self.aa_stride,::self.aa_stride]    
            else:
                return self.pad(pooled)[:,:,::self.aa_stride,::self.aa_stride]
        else:
            return torch.nn.functional.conv2d(self.pad(pooled), 
                self.filter, stride=self.aa_stride, groups=pooled.shape[1]
            )


class Conv2dBlock(torch.nn.Module):
    def __init__(self,
        in_features: int,
        out_features: int,
        convolution_params: dict,
        activation_type='relu_bn2d',
    ):
        super(Conv2dBlock, self).__init__()
        self.conv = _make_conv_op(
            in_channels=in_features,
            out_channels=out_features,
            kernel_size=convolution_params.kernel_size,
            stride=convolution_params.stride,
            padding=convolution_params.padding,
        )
        if activation_type == 'relu_bn2d':
            self.activation = ReLu_BN(
                features=out_features,
            )
        elif activation_type == 'relu':
            self.activation =  torch.nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(self.conv(x))

class ReLu_BN(torch.nn.Module):
    def __init__(self,
        features: int,
        inplace: bool=True,
        epsilon: float=1e-5,
    ):
        super(ReLu_BN, self).__init__()
        self.bn = torch.nn.BatchNorm2d(features, eps=epsilon)
        self.activation = torch.nn.ReLU(inplace=inplace)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.bn(self.activation(x))

def _make_conv_op(
        #convolution_type: str,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int=1,
        padding: int=1,
        dilation: int=1,        
        groups: int=1, 
        bias: bool=True,
    ) -> torch.nn.Module:

    return torch.nn.Conv2d( **locals())



class UNet(torch.nn.Module):
    def __init__(self,
        configuration:  omegaconf.DictConfig,
    ) -> None:
        super().__init__()
        convolution = configuration.convolution
        activation = configuration.activation
        downscale = configuration.downscale
        bottleneck = configuration.bottleneck
        upscale = configuration.upscale
        prediction = configuration.prediction
        #skip = modules['skip'] if modules is not None else None
        block_features = configuration.block_features
        down_block_convs = configuration.down_block_convs
        in_features = configuration.in_features
        self.enc = torch.nn.ModuleDict()
        self.down = torch.nn.ModuleDict()
        for f, b in zip(block_features, down_block_convs):
            enc_block = torch.nn.Sequential()
            for i in range(b):
                enc_block.add_module(f'enc{f}_{i}',Conv2dBlock(
                    in_features=in_features if i == 0 else f, 
                    out_features=f,
                    convolution_params=convolution.params,
                    activation_type=configuration.activation.type,
                ))
            in_features = f
            self.enc.add_module(f'enc_block{f}', enc_block)
            self.down.add_module(f'down{f}', AntialiasedMaxPool2d(
                features=f,
                kernel_size=3 if downscale.type == 'maxpool2d_aa' else 2,
                #stride=1,
                #padding=1,
            ))
        
        self.bottleneck = torch.nn.Sequential()
        for i in range(bottleneck.blocks):
            self.bottleneck.add_module(f'bottleneck{i}', Conv2dBlock(
                in_features=block_features[-1] if i == 0 else bottleneck.features, 
                out_features=bottleneck.features,
                convolution_params=bottleneck.convolution.params,
            ))
        up_block_convs = configuration.up_block_convs
        up_block_convs = reversed(down_block_convs) if up_block_convs is None else up_block_convs
        self.dec = torch.nn.ModuleDict()
        self.up = torch.nn.ModuleDict()
        self.skip = torch.nn.ModuleDict()
        for f, b in zip(reversed(block_features), up_block_convs):
            self.up.add_module(f'up{f}', torch.nn.Sequential(
                Upsample2d(),
                _make_conv_op(
                    in_channels=f * 2, out_channels=f,
                    kernel_size=1,
                    stride=1,
                    dilation=1,
                    padding=0,
                    groups=1,
                    bias=False  
                )
            ))#TODO: need to downscale features too
            #NOTE: one case is deconv2d and the other is upscale and project
            #NOTE: we now only use upscale and project
            self.skip.add_module(f'skip{f}', torch.nn.Identity())
            dec_block = torch.nn.Sequential()
            for i in range(b):
                dec_block.add_module(f'dec{f}_{i}', Conv2dBlock(
                    in_features=f * 2 if i == 0 else f, 
                    out_features=f,
                    convolution_params=convolution.params,
                ))
            self.dec.add_module(f'dec_block{f}', dec_block)
        out_features = configuration.out_features
        self.pred = Conv2dBlock(
            in_features=block_features[0], out_features=out_features,
            convolution_params=prediction.convolution.params,
            activation_type=prediction.activation.type,
        )
    def forward(self,
        x: torch.Tensor) -> torch.Tensor:
        features = [x]
        skipped = []
        for e, d in zip(self.enc.values(), self.down.values()):
            skipped.append(e(features[-1]))
            features.append(d(skipped[-1]))
        bottleneck = self.bottleneck(features[-1])
        skipped.reverse()
        features = [bottleneck]
        for i, (u, s, d) in enumerate(zip(
                self.up.values(),
                self.skip.values(),
                self.dec.values()
            )):
                up = u(features[-1])
                skip = s(skipped[i])
                concat = torch.cat([up, skip], dim=1)
                features.append(d(concat))
        out = self.pred(features[-1])
        return out


if __name__ == '__main__':
    init_params = omegaconf.DictConfig({ # configuration            
            'block_features': [32, 64, 128, 256, 512],
            'down_block_convs': [2, 2, 2, 2, 2],
            'in_features': 3,
            'out_features': 1,
            'input': ['image'],
            'output': ['depth'],
            'convolution': omegaconf.DictConfig({ 
                'type': 'conv2d',
                'params': {
                    'kernel_size': 3,
                    'stride': 1,
                    'padding': 1,
                },
            }),
            'activation': omegaconf.DictConfig({ 
                'type': 'relu_bn2d',
                'params': {
                    'inplace': True,
                },
            }),   
            'downscale': omegaconf.DictConfig({
                'type': 'maxpool2d_aa',
                'params': { },
            }),
            'bottleneck': omegaconf.DictConfig({
                'blocks': 2,
                'features': 1024,
                'convolution': omegaconf.DictConfig({ 
                    'type': 'conv2d',
                    'params': {
                        'kernel_size': 3,
                        'stride': 1,
                        'padding': 1,
                    },
                }),
                'activation': omegaconf.DictConfig({ 
                    'type': 'relu_bn2d',
                    'params': {
                        'inplace': True,
                    },
                }), 
            }),
            'upscale': omegaconf.DictConfig({
                'type': 'upsample2d',
                'params': { },
            }),
            'prediction': omegaconf.DictConfig({
                'convolution': {
                    'type': 'conv2d',
                    'params': { 
                        'kernel_size': 1,
                        'padding': 0,
                        'stride': 1,
                    },
                },
                'activation': {
                    'type': 'relu',
                    'params': { 
                        'inplace': True,
                    },
                },
            }),
        })
    unet = UNet(
        omegaconf.DictConfig({ # configuration            
            'block_features': [32, 64, 128, 256, 512],
            'down_block_convs': [2, 2, 2, 2, 2],
            'in_features': 3,
            'out_features': 1,
            'input': ['image'],
            'output': ['depth'],
            'convolution': omegaconf.DictConfig({ 
                'type': 'conv2d',
                'params': {
                    'kernel_size': 3,
                    'stride': 1,
                    'padding': 1,
                },
            }),
            'activation': omegaconf.DictConfig({ 
                'type': 'relu_bn2d',
                'params': {
                    'inplace': True,
                },
            }),   
            'downscale': omegaconf.DictConfig({
                'type': 'maxpool2d_aa',
                'params': { },
            }),
            'bottleneck': omegaconf.DictConfig({
                'blocks': 2,
                'features': 1024,
                'convolution': omegaconf.DictConfig({ 
                    'type': 'conv2d',
                    'params': {
                        'kernel_size': 3,
                        'stride': 1,
                        'padding': 1,
                    },
                }),
                'activation': omegaconf.DictConfig({ 
                    'type': 'relu_bn2d',
                    'params': {
                        'inplace': True,
                    },
                }), 
            }),
            'upscale': omegaconf.DictConfig({
                'type': 'upsample2d',
                'params': { },
            }),
            'prediction': omegaconf.DictConfig({
                'convolution': {
                    'type': 'conv2d',
                    'params': { 
                        'kernel_size': 1,
                        'padding': 0,
                        'stride': 1,
                    },
                },
                'activation': {
                    'type': 'relu',
                    'params': { 
                        'inplace': True,
                    },
                },
            }),
        }),
    )
    inp = torch.rand(5, 3, 256, 512)
    #depth = unet({'image': inp})['depth']
    depth = unet(inp)
    print(depth.shape)