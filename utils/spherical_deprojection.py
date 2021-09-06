import torch

class SphericalDeprojection(torch.nn.Module):
    '''
        Cartesian coordinates extraction from Spherical coordinates
            z is forward axis
            y is the up axis
            x is the right axis
            r is the radius (i.e. spherical depth)
            phi is the longitude/azimuthial rotation angle (defined on the x-z plane)
            theta is the latitude/elevation rotation angle (defined on the y-z plane)
    '''
    def __init__(self,

    ):
        super(SphericalDeprojection, self).__init__()

    def _phi(self, sgrid): # longitude or azimuth
        return sgrid[:, 0, :, :].unsqueeze(1)

    def _theta(self, sgrid): # latitude or elevation
        return sgrid[:, 1, :, :].unsqueeze(1)

    def _coord_x(self, sgrid, depth):
        return ( # r * sin(phi) * sin(theta) -> r * cos(phi) * -cos(theta) in our offsets
            depth # this is due to the offsets as explained below
            * torch.cos(self._phi(sgrid)) # long = x - 3 * pi / 2
            * -1.0 * torch.cos(self._theta(sgrid)) # lat = y - pi / 2
        )

    def _coord_y(self, sgrid, depth):
        return ( # r * cos(theta) -> r * sin(theta) in our offsets
            depth # this is due to the offsets as explained below
            * torch.sin(self._theta(sgrid)) # lat = y - pi / 2
        )

    def _coord_z(self, sgrid, depth):
        return ( # r * cos(phi) * sin(theta) -> r * -sin(phi) * -cos(theta) in our offsets
            depth # this is due to the offsets as explained above
            * torch.sin(self._phi(sgrid)) # * -1
            * torch.cos(self._theta(sgrid)) # * -1
        ) # the -1s cancel out

    def _coords_3d(self, sgrid, depth):
        return torch.cat(
            (
                self._coord_x(sgrid, depth),
                self._coord_y(sgrid, depth),
                self._coord_z(sgrid, depth)
            ), dim=1
        )

    def forward(self, 
        depth: torch.Tensor, 
        sgrid: torch.Tensor
    ) -> torch.Tensor:
        return self._coords_3d(sgrid, depth)
