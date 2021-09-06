from typing import Tuple
import imageio
import os
import numpy as np
import torch
import functools
import matplotlib
matplotlib.use("Agg")
from matplotlib import cm
from matplotlib.colors import Colormap
import plyfile
import open3d as o3d
import logging

log = logging.getLogger(__name__)



class Visualizers(object):
    def __init__(self):
        pass
    
    def export_mesh(self,
        pcloud: np.array,colors:np.array,radius=0.1,
                    max_nn=8,depth=10,threshold=0.05,recalculate=True) -> o3d.geometry.TriangleMesh:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pcloud.transpose(1,0))
        pcd.colors = o3d.utility.Vector3dVector(colors.transpose(1,0)/255.)
        # calculate normals
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
        # recalculate normals to fix culling issue
        if recalculate:
            pcd.orient_normals_towards_camera_location(camera_location=np.array([0., 0., 0.]))
        # convert to mesh
        mesh , densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd,depth=depth)
        # filter out vertices
        vertices_to_remove = densities < np.quantile(densities,threshold)
        mesh.remove_vertices_by_mask(vertices_to_remove)
        # save mesh
        log.info("Exporting mesh has been finished!")
        return mesh
    
    def export_dist(self,pcloud: np.array)->Tuple:
        dist_to_ceiling = pcloud[:,:20][1].mean()
        dist_to_floor =  pcloud[:,-20:][1].mean()
        return (dist_to_ceiling,dist_to_floor)
    
    def _matplotlib_colormap(self,
        colormap: Colormap,
        tensor: torch.Tensor
    ) -> np.array:
        data = tensor.cpu().detach().numpy() if tensor.is_cuda else tensor.detach().numpy()
        return colormap(data).squeeze(1).transpose(0, 3, 1, 2)[:, :3, :, :]

    

    def _minmax_normalization(self,
        tensor: torch.Tensor, positive_only=False) -> torch.Tensor:
        b, _, __, ___ = tensor.size()
        t = tensor
        if positive_only:
            t[t < 0.0] = 0.0
        min_v = torch.min(t.view(b, -1), dim=1, keepdim=True)[0].unsqueeze(2).unsqueeze(3)
        max_v = torch.max(t.view(b, -1), dim=1, keepdim=True)[0].unsqueeze(2).unsqueeze(3)
        return (t - min_v) / (max_v - min_v) 
    
    def export_depth(self, depth:torch.tensor) -> np.array:
        depth = self._minmax_normalization(depth)
        turbo = functools.partial(self._matplotlib_colormap, cm.get_cmap('turbo'))
        #b, _, __, ___ = depth.shape
        depth = turbo(depth)
        return depth
    
    def write_ply(self,
              output_path,
              pts,
              normals=None,
              rgb=None,
              faces=None,
              face_rgb=None,
              text=False):
        '''
        Points should be 3 x N. Optionally, faces, normals, and RGB should be 3 x N as well
        '''
        names = 'x,y,z'
        formats = 'f4,f4,f4'
        if normals is not None:
            pts = np.vstack((pts, normals))
            names += ',nx,ny,nz'
            formats += ',f4,f4,f4'
        if rgb is not None:
            pts = np.vstack((pts, rgb))
            names += ',red,green,blue'
            formats += ',u1,u1,u1'
        pts = np.core.records.fromarrays(pts, names=names, formats=formats)
        el = [plyfile.PlyElement.describe(pts, 'vertex')]
        if faces is not None:
            faces = faces.astype(np.int32)
            faces = faces.copy().ravel().view([("vertex_indices", "u4", 3)])
            el.append(plyfile.PlyElement.describe(faces, 'face'))
        if face_rgb is not None:
            el.append(plyfile.PlyElement.describe(face_rgb, 'face'))

        plyfile.PlyData(el, text=text).write(output_path)

# def write_ply(output_path,
#               pts,
#               normals=None,
#               rgb=None,
#               faces=None,
#               face_rgb=None,
#               text=False):
#         '''
#         Points should be 3 x N. Optionally, faces, normals, and RGB should be 3 x N as well
#         '''
#         names = 'x,y,z'
#         formats = 'f4,f4,f4'
#         if normals is not None:
#             pts = np.vstack((pts, normals))
#             names += ',nx,ny,nz'
#             formats += ',f4,f4,f4'
#         if rgb is not None:
#             pts = np.vstack((pts, rgb))
#             names += ',red,green,blue'
#             formats += ',u1,u1,u1'
#         pts = np.core.records.fromarrays(pts, names=names, formats=formats)
#         el = [plyfile.PlyElement.describe(pts, 'vertex')]
#         if faces is not None:
#             faces = faces.astype(np.int32)
#             faces = faces.copy().ravel().view([("vertex_indices", "u4", 3)])
#             el.append(plyfile.PlyElement.describe(faces, 'face'))
#         if face_rgb is not None:
#             el.append(plyfile.PlyElement.describe(face_rgb, 'face'))

#         plyfile.PlyData(el, text=text).write(output_path)



# def _matplotlib_colormap(
#     colormap: Colormap,
#     tensor: torch.Tensor
# ) -> np.array:
#     data = tensor.cpu().detach().numpy() if tensor.is_cuda else tensor.detach().numpy()
#     return colormap(data).squeeze(1).transpose(0, 3, 1, 2)[:, :3, :, :]


# turbo = functools.partial(_matplotlib_colormap, cm.get_cmap('turbo'))



# def _minmax_normalization(tensor: torch.Tensor, positive_only=False) -> torch.Tensor:
#         b, _, __, ___ = tensor.size()
#         t = tensor
#         if positive_only:
#             t[t < 0.0] = 0.0
#         min_v = torch.min(t.view(b, -1), dim=1, keepdim=True)[0].unsqueeze(2).unsqueeze(3)
#         max_v = torch.max(t.view(b, -1), dim=1, keepdim=True)[0].unsqueeze(2).unsqueeze(3)
#         return (t - min_v) / (max_v - min_v)     

def _save_depth(
        #path:               str,
        depth:              torch.tensor,
        #key:                str,
        #index:              int,
        #ext:                str,
    ) -> np.array:
        #normalize depth
        depth = _minmax_normalization(depth)
        #b, _, __, ___ = depth.shape
        depth = turbo(depth)
        return depth
        #for i in range(b):
           #colorize map
           #turbo(depth)
           #torchvision.utils.save_image(
               #depth[i, :, :, :], 
               #f'{key}_{index + i}.{ext}'
            #)
            #p = os.path.join(path,f'{key}_{index + i}.{ext}')
            #imageio.imwrite(p, (depth.cpu().numpy())[i, :, :, :].transpose(1,2,0))
            #imageio.imwrite(f'{key}_{index + i}.{ext}', (array)[i, :, :, :].transpose(1,2,0))
        #return b

# def _convert_to_mesh(pcloud: np.array,colors:np.array,radius=0.1,
#                     max_nn=8,depth=10,threshold=0.05,recalculate=True) -> o3d.geometry.TriangleMesh:
#     pcd = o3d.geometry.PointCloud()
#     pcd.points = o3d.utility.Vector3dVector(pcloud.transpose(1,0))
#     pcd.colors = o3d.utility.Vector3dVector(colors.transpose(1,0)/255.)
#     # calculate normals
#     pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
#     # recalculate normals to fix culling issue
#     if recalculate:
#         pcd.orient_normals_towards_camera_location(camera_location=np.array([0., 0., 0.]))
#     # convert to mesh
#     mesh , densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd,depth=depth)
#     # filter out vertices
#     vertices_to_remove = densities < np.quantile(densities,threshold)
#     mesh.remove_vertices_by_mask(vertices_to_remove)
#     # save mesh
#     print("finished processing mesh")
#     return mesh

def _calc_distances(pcloud: np.array)->Tuple:
    dist_to_ceiling = pcloud[:,:20][1].mean()
    dist_to_floor =  pcloud[:,-20:][1].mean()
    return (dist_to_ceiling,dist_to_floor)