###################################################################################################################################################################################
## Camera setup
###################################################################################################################################################################################

from falsecolor_film import FalseColorFilm
from image_film import ImageFilm
from multi_film import MultiFilm
from perspective_camera import PerspectiveCamera
from wireframe_film import WireframeFilm
from wireframerenderer import Wireframe3DRenderer

def create_camera(scene, camera_to_world, fov=60.0, x_res=512, y_res=512, fname='pbrtpy.png', image_film=True, false_color_film=False, wireframe_film=False):
    # Film
    film = MultiFilm(x_res=x_res, y_res=y_res)
    if image_film: 
        film.add_film(ImageFilm(x_res=x_res, y_res=y_res, fname=fname))
    if false_color_film:
        film.add_film(FalseColorFilm(x_res=x_res, y_res=y_res, fname=fname))
    
    # Camera
    frame = float(x_res) / y_res
    if frame > 1.0:
        screen_window = [-frame, frame, -1.0, 1.0]
    else:
        screen_window = [-1.0, 1.0, -1.0 / frame, 1.0 / frame]
    camera = PerspectiveCamera(camera_to_world=camera_to_world, screen_window=screen_window, fov=fov, film=film)
     
    # Film  
    if wireframe_film:
        wfr = Wireframe3DRenderer()
        scene.accept(wfr)
        camera.accept(wfr)
        film.add_film(WireframeFilm(wireframe_renderer=wfr, fname=fname))

    return camera

###################################################################################################################################################################################
## Renderer setup
###################################################################################################################################################################################

from ambientocclusion_integrator import AmbientOcclusionIntegrator
from occlusion_integrator import OcclusionIntegrator
from random_sampler import RandomSampler
from sampler_renderer import SamplerRenderer

def create_renderer(camera, spp=1, first_pass_iter=0):
    # Surface_integrator
    surface_integrator = AmbientOcclusionIntegrator(nb_samples=1)
    # Sampler
    sampler = RandomSampler(*camera.film.get_sample_extent(), spp=spp, shutter_open=camera.shutter_open, shutter_close=camera.shutter_close)
    # Renderer
    return SamplerRenderer(sampler=sampler, camera=camera, surface_integrator=surface_integrator, first_pass_iter=first_pass_iter)

###################################################################################################################################################################################
## Tests
###################################################################################################################################################################################

import numpy as np
from camera import cam2world
from modelgenerator import _cube
from regulargrid import RegularGrid
from scene import Scene
from scenegenerator import stratified

def test():
    #scene = Scene(stratified(model=cube(), density=0.75, nb_voxels=3, scaling=0.2))
    scene = Scene(RegularGrid(_cube().shapes))
    
    pos   = np.array([1.341364,    0.2693291, -1.40054])
    look  = np.array([-0.6851092, -0.1375613, 0.7153337])
    up    = np.array([-0.09513324, 0.9904932, 0.09936189])
    camera_to_world = cam2world(pos, look, up)
    
    camera = create_camera(scene, camera_to_world, false_color_film=True, wireframe_film=False)
    renderer = create_renderer(camera, spp=2, first_pass_iter=0)
    renderer.render(scene=scene)
  
if __name__ == '__main__':
    test()