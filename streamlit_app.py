from genericpath import exists
import PIL
from streamlit.hashing import HashReason
from streamlit.state.session_state import WidgetArgs
import torch
import streamlit as st
from streamlit import components
from streamlit import file_util
import streamlit.report_thread as ReportThread
from streamlit.server.server import Server
from streamlit import caching
from streamlit import script_runner
from torch.futures import S
from unet.model import UNet as Model
from utils.utils import Interpolate
from utils.spherical import Spherical
from utils.spherical_deprojection import SphericalDeprojection
from utils.visualizers import Visualizers
import os
import platform
try:
    from torch.hub import load_state_dict_from_url
except ImportError:
    from torch.utils.model_zoo import load_url as load_state_dict_from_url
import omegaconf.omegaconf
import io
from PIL import Image
import numpy as np
import open3d as o3d # this should not be included when deployed in GitHub
import time
from streamlit.server.server import StaticFileHandler
import urllib.request


model_urls = {
    'UNet': 'https://github.com/tzole1155/StreamLitDemo/releases/download/Unet/unet.pth',
}

#@classmethod
def _get_cached_version(cls, abs_path: str):
    with cls._lock:
        return cls.get_content_version(abs_path)

#@st.cache(allow_output_mutation=True, ttl=120000, max_entries=1)
@st.cache(allow_output_mutation=True, ttl=3600, max_entries=1)
def init_model(choice:str):
    #device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    device = torch.device("cpu")
    if choice == 'UNet':
        #load model
        #read configuration file
        conf_path = './conf/unet/model_unet.yaml'
        #model_pt_path = './weights/unet/unet.pth'
        #download weights from github
        # state_dict = load_state_dict_from_url(model_urls[choice],
        #                                       progress=True)
        # if not os.path.isfile(model_pt_path):
        #         error_message = f"Missing the serialized model weights file({model_pt_path})"
        #         st.error(error_message)
        #         raise RuntimeError(error_message)
        if not os.path.isfile(conf_path):
                error_message = f"Missing the model's configuration file({conf_path})"
                st.error(error_message)
                raise RuntimeError(error_message)
        conf = omegaconf.OmegaConf.load(conf_path)
        model = Model(conf.model.configuration)
        # checkpoint = torch.load(model_pt_path,
        #     map_location=lambda storage, loc: storage
        #     )
        checkpoint = load_state_dict_from_url(model_urls[choice],
                                              map_location=lambda storage, loc: storage,
                                              progress=True)

        model.load_state_dict(checkpoint['state_dict'], False)
    
    model.to(device)
    model.eval()
    
    return model,device

def preprocess(bytes):
    raw = io.BytesIO(bytes)
    image = Image.open(raw)
    image = image.resize((512,256),Image.LANCZOS)
    image = np.array(image) # cvt color?
    image = image.transpose(2, 0, 1)
    image = torch.from_numpy(image).unsqueeze(0).float() / 255.0

    return image

def inference(input,model,device):
    with torch.no_grad():
        depth = model(input.to(device))
    
    return depth

def get_depth_map(viz,depth,static_path):
    st.markdown("## Predicted depth map", unsafe_allow_html=True)
    imgs = viz.export_depth(depth)
    #break
    return imgs

def get_point_cloud(viz,depth,color,static_path):
    device = depth.get_device()
    if device == -1:
        device = 'cpu'
    sgrid = Spherical(width=512,mode='pi',long_offset_pi=-0.5).to(device)(depth)
    isPcloud = False
    while not isPcloud:
        st.warning("Creating point cloud...")
        pcloud = SphericalDeprojection().to(device)(depth,sgrid)
        pred_xyz = pcloud[0]
        rgb = color[0] * 255.0
        if isinstance(rgb,np.ndarray):
            colors = rgb.reshape(3, - 1).astype(np.uint8)
        else:
            colors = rgb.reshape(3, - 1).cpu().numpy().astype(np.uint8)    
        pred_filename = os.path.join(static_path,'pred_pointcloud.ply')
        if os.path.isfile(pred_filename):
            os.remove(pred_filename)
        pred_xyz = pred_xyz.reshape(3, -1).cpu().numpy()
        viz.write_ply(pred_filename, pred_xyz, None, colors)
        if torch.is_tensor(pcloud):
            isPcloud=True
    
    return pred_xyz,colors


def export_mesh(viz,pred_xyz,colors,static_path):
    isMesh = False
    while not isMesh:
        st.warning("Reconstructing mesh...")
        mesh = viz.export_mesh(pred_xyz,colors)
        #save mesh
        mesh_filename = os.path.join(static_path,"pred_mesh.obj")
        if os.path.isfile(mesh_filename):
            os.remove(mesh_filename)
        o3d.io.write_triangle_mesh(mesh_filename, mesh, write_triangle_uvs=True)
        if mesh:
            isMesh = True


def visualise_outputs(color,depth):
    device = depth.get_device()
    if device == -1:
        device = 'cpu'
    viz = Visualizers()
    imgs = viz.export_depth(depth)
    static_path = file_util.get_static_dir()
    #visualise depth map
    st.markdown("## Predicted depth map", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3,4,3])
    with col1:
        st.write("")
    with col2:
        #st.markdown("<p style='text-align: center;'>Panorama image</p>", unsafe_allow_html=True)
        st.image(imgs[0].transpose(1, 2, 0),use_column_width=True,caption='Predicted depth map')
        #st.markdown("<p style='text-align: center;'>Predicted depth map</p>", unsafe_allow_html=True)
    with col3:
        st.write("")
    pred_filename = os.path.join(static_path,'pred_depth_map.jpg')
    im_ = Image.fromarray(np.uint8(imgs[0].transpose(1,2,0) * 255))
    im_.save(pred_filename,'JPEG')
    #point cloud exporter
    # i = 0
    # latest_iteration = st.empty()
    # bar = st.progress(0)
    # for i in range(100):
    #     bar.progress(i + 1)
    sgrid = Spherical(width=512,mode='pi',long_offset_pi=-0.5).to(device)(imgs)
    pcloud = SphericalDeprojection().to(device)(depth,sgrid)
    #breakpoint()
    if not torch.is_tensor(pcloud[0]):
        st.warning("Creating point cloud...")
        st.stop()
    st.success("Point cloud has been created!")
    pred_xyz = pcloud[0]
    rgb = color[0] * 255.0
    if isinstance(rgb,np.ndarray):
        colors = rgb.reshape(3, - 1).astype(np.uint8)
    else:
        colors = rgb.reshape(3, - 1).cpu().numpy().astype(np.uint8)    
    pred_filename = os.path.join(static_path,'pred_pointcloud.ply')
    if os.path.isfile(pred_filename):
        os.remove(pred_filename)
    pred_xyz = pred_xyz.reshape(3, -1).cpu().numpy()
    #write_ply(pred_filename, pred_xyz, None, colors)
    viz.write_ply(pred_filename, pred_xyz, None, colors)
    #time.sleep(0.1)
    #export mesh
    mesh = viz.export_mesh(pred_xyz,colors)
    #save mesh
    mesh_filename = os.path.join(static_path,"pred_mesh.obj")
    if os.path.isfile(mesh_filename):
        os.remove(mesh_filename)
    o3d.io.write_triangle_mesh(mesh_filename, mesh, write_triangle_uvs=True)

def trigger_rerun():

    ctx = ReportThread.get_report_ctx()

    this_session = None
    
    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56        
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        this_session = s
        if (
            # Streamlit < 0.54.0
            (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')
    #this_session.request_rerun()
    this_session.request_rerun(None)


def main():
    StaticFileHandler._get_cached_version = _get_cached_version
    #Use this for clearing cache!
    st.set_page_config(layout="wide")
    static_path = file_util.get_static_dir()
    urllib.request.urlretrieve(
        'https://raw.githubusercontent.com/tzole1155/StreamLitDemo/main/Images/Banner.png',
        os.path.join(static_path,"banner.png"))
    #st.title('Pano3D 360 depth estimator')
    banner = PIL.Image.open(os.path.join(static_path,"banner.png"))
    # st.image(os.path.join('Images','banner.png'), use_column_width  = True)
    st.image(banner, use_column_width  = True)
    st.markdown("<h1 style='text-align: center; color: white;'>Reconstruct your room from a single panorama</h1>", unsafe_allow_html=True)

    #st.write("This web-page provides a live demo of the recentl")

    text_file = open("intro.md", "r")
    #read whole file to a string
    md_string = text_file.read()
    #close file
    text_file.close()

    readme_text = st.markdown(md_string)

    menu = ['UNet']
    st.sidebar.header('Model Selection')
    choice = st.sidebar.selectbox('How would you like to be turn ?', menu)
    
    #init model
    model, device = init_model(choice)

    viz = Visualizers()

    Image = st.file_uploader('Upload your panorama here',type=['jpg','jpeg','png'])
    #caching.clear_cache()
    if Image is not None:
        #col1, col2 = st.beta_columns(2)
        st.markdown("## Input Panorama", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3,4,3])
        with col1:
            st.write("")
        Image = Image.read()
        #st.text(type(Image))
        with col2:
            st.image(Image,use_column_width=True,caption='Input panorama')
        with col3:
            st.write("")
        #process image
        input = preprocess(Image)
        #run model
        isDepth = False
        while not isDepth:
            st.warning("Model is running...")
            depth = inference(input,model,device)
            if torch.is_tensor(depth):
                isDepth = True
        #visualise outputs
        imgs = get_depth_map(viz,depth,static_path)
        col1, col2, col3 = st.columns([3,4,3])
        with col1:
            st.write("")
        with col2:
            #st.markdown("<p style='text-align: center;'>Panorama image</p>", unsafe_allow_html=True)
            st.image(imgs[0].transpose(1, 2, 0),use_column_width=True,caption='Predicted depth map')
            #st.markdown("<p style='text-align: center;'>Predicted depth map</p>", unsafe_allow_html=True)
        with col3:
            st.write("")
        #point cloud
        pred_xyz,colors = get_point_cloud(viz,depth,input,static_path)
        text_file = open("./html/ply.html", "r")
        #read whole file to a string
        html_string = text_file.read()
        text_file.close()
        st.markdown("## Predicted Point Cloud", unsafe_allow_html=True)
        st.markdown("Inspect the predicted point cloud through the interactive 3D Model Viewer", unsafe_allow_html=True)
        h1 = components.v1.html(html_string, height=600)
        st.success("Point cloud has been created!")
        linko= f'<a href="pred_pointcloud.ply" download="pred_pointcloud.ply"><button class="css-1ubkpyc edgvbvh1">Download Point Cloud!</button></a>'
        st.markdown(linko, unsafe_allow_html=True)
        #mesh
        export_mesh(viz,pred_xyz,colors,static_path)
        text_file = open("./html/mesh.html", "r")
        #read whole file to a string
        html_string = text_file.read()
        text_file.close()
        st.markdown("## Reconstructed Mesh", unsafe_allow_html=True)
        st.markdown("Inspect the reconstructed mesh through the interactive 3D Model Viewer", unsafe_allow_html=True)
        h2 = components.v1.html(html_string, height=600)
        st.success("Mesh has been created!")
        linko= f'<a href="pred_mesh.obj" download="pred_mesh.obj"><button class="css-1ubkpyc edgvbvh1">Download Reconstructed Mesh!</button></a>'
        st.markdown(linko, unsafe_allow_html=True)
        #Acknow
        text_file = open("Ackn.md", "r")
        #read whole file to a string
        md_string = text_file.read()
        #close file
        text_file.close()
        ack_text = st.markdown(md_string)
        st.stop()
        #trigger_rerun()
    

# def main():
#     #Use this for clearing cache!
#     st.set_page_config(layout="wide")
#     static_path = file_util.get_static_dir()
#     urllib.request.urlretrieve(
#         'https://raw.githubusercontent.com/tzole1155/StreamLitDemo/main/Images/Banner.png',
#         os.path.join(static_path,"banner.png"))
#     #st.title('Pano3D 360 depth estimator')
#     banner = PIL.Image.open(os.path.join(static_path,"banner.png"))
#     # st.image(os.path.join('Images','banner.png'), use_column_width  = True)
#     st.image(banner, use_column_width  = True)
#     st.markdown("<h1 style='text-align: center; color: white;'>Reconstruct your room form a single panorama</h1>", unsafe_allow_html=True)

#     #st.write("This web-page provides a live demo of the recentl")

#     text_file = open("intro.md", "r")
#     #read whole file to a string
#     md_string = text_file.read()
#     #close file
#     text_file.close()

#     readme_text = st.markdown(md_string)

#     menu = ['UNet']
#     st.sidebar.header('Model Selection')
#     choice = st.sidebar.selectbox('How would you like to be turn ?', menu)
    
#     #init model
#     model, device = init_model(choice)

#     Image = st.file_uploader('Upload your panorama here',type=['jpg','jpeg','png'])
#     if Image is not None:
#         #col1, col2 = st.beta_columns(2)
#         st.markdown("## Input Panorama", unsafe_allow_html=True)
#         col1, col2, col3 = st.columns([3,4,3])
#         with col1:
#             st.write("")
#         Image = Image.read()
#         #st.text(type(Image))
#         with col2:
#             st.image(Image,use_column_width=True,caption='Input panorama')
#         with col3:
#             st.write("")
#         #process image
#         input = preprocess(Image)
#         #run model
#         depth = inference(input,model,device)
#         #visualise outputs
#         visualise_outputs(input,depth)
#         #clear cache?
#         StaticFileHandler._get_cached_version = _get_cached_version
#         text_file = open("./html/ply.html", "r")
#         #read whole file to a string
#         html_string = text_file.read()
#         #time.sleep(1.5)
#         #close file
#         text_file.close()
#         #breakpoint()
#         st.markdown("## Predicted Point Cloud", unsafe_allow_html=True)
#         st.markdown("Inspect the predicted point cloud through the interactive 3D Model Viewer", unsafe_allow_html=True)
#         h1 = components.v1.html(html_string, height=600)
#         linko= f'<a href="pred_pointcloud.ply" download="pred_pointcloud.ply"><button class="css-1ubkpyc edgvbvh1">Download Point Cloud!</button></a>'
#         st.markdown(linko, unsafe_allow_html=True)
#         #st.markdown("<p style='text-align: center;'>Predicted Point Cloud</p>", unsafe_allow_html=True)
#         #visualize mesh
#         text_file = open("./html/mesh.html", "r")
#         #read whole file to a string
#         html_string = text_file.read()
#         #time.sleep(1.5)
#         #close file
#         text_file.close()
#         st.markdown("## Reconstructed Mesh", unsafe_allow_html=True)
#         st.markdown("Inspect the reconstructed mesh through the interactive 3D Model Viewer", unsafe_allow_html=True)
#         h2 = components.v1.html(html_string, height=600)
#         # st.markdown("<p style='text-align: center;'>Reconstructed Mesh</p>", unsafe_allow_html=True)
#         #download=st.button('Download Point Cloud')
#         static_path = file_util.get_static_dir()
#         linko= f'<a href="pred_mesh.obj" download="pred_mesh.obj"><button class="css-1ubkpyc edgvbvh1">Download Reconstructed Mesh!</button></a>'
#         st.markdown(linko, unsafe_allow_html=True)

#         text_file = open("Ackn.md", "r")
#         #read whole file to a string
#         md_string = text_file.read()
#         #close file
#         text_file.close()
#         ack_text = st.markdown(md_string)

   


if __name__ == '__main__':
    main()
