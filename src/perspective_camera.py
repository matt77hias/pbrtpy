import numpy as np
from math_utils import normalize

###############################################################################
## PerspectiveCamera
###############################################################################
from camera import ProjectiveCamera
from ray import Ray
from sampling import concentric_sample_disk
from transform import perspective

class PerspectiveCamera(ProjectiveCamera):

    def __init__(self, camera_to_world, screen_window, film, shutter_open=0.0, shutter_close=1.0, lens_radius=0.0, focal_distance=10.0**30, fov=90.0, color='k'):
        super(PerspectiveCamera, self).__init__(camera_to_world, perspective(fov, 1e-2, 1000.0), screen_window, film, shutter_open=shutter_open, shutter_close=shutter_close, lens_radius=lens_radius, focal_distance=focal_distance, color=color)
        self.dx_camera = self.raster_to_camera(np.array([1, 0, 0]), is_point=True) - self.raster_to_camera(np.array([0, 0, 0]), is_point=True)
        self.dy_camera = self.raster_to_camera(np.array([0, 1, 0]), is_point=True) - self.raster_to_camera(np.array([0, 0, 0]), is_point=True)

    def generate_ray(self, sample):
        # Generate raster and camera samples
        p_ras = np.array([sample.image_x, sample.image_y, 0.0])
        p_camera = self.raster_to_camera(p_ras, is_point=True)
        ray = Ray(np.zeros((3)), normalize(p_camera))

        #  Modify ray for depth of field
        if self.lens_radius > 0.0:
            # Sample point on lens
            lens_u, lens_v = concentric_sample_disk(sample.lens_u, sample.lens_v)
            lens_u *= self.lens_radius
            lens_v *= self.lens_radius

            # Compute point on plane of focus
            ft = self.focal_distance / ray.d[2]
            p_focus = ray(ft)

            # Update ray for effect of lens
            ray.o = np.array([lens_u, lens_v, 0.0])
            ray.d = normalize(p_focus - ray.o)

        ray.time = sample.time
        ray = self.camera_to_world(ray)

        return 1.0, ray

    def generate_ray_differential(self, sample):
        p_ras = np.array([sample.image_x, sample.image_y, 0.0])
        p_camera = self.raster_to_camera(p_ras, is_point=True)
        ray = Ray(np.zeros((3)), normalize(p_camera))

        #  Modify ray for depth of field
        if self.lens_radius > 0.0:
            # Sample point on lens
            lens_u, lens_v = concentric_sample_disk(sample.lens_u, sample.lens_v)
            lens_u *= self.lens_radius
            lens_v *= self.lens_radius

            # Compute point on plane of focus
            ft = self.focal_distance / ray.d[2]
            p_focus = ray(ft)

            # Update ray for effect of lens
            ray.o = np.array([lens_u, lens_v, 0.0])
            ray.d = normalize(p_focus - ray.o)
            
        if self.lens_radius > 0.0:
            # Sample point on lens
            lens_u, lens_v = concentric_sample_disk(sample.lens_u, sample.lens_v)
            lens_u *= self.lens_radius
            lens_v *= self.lens_radius

            dx = normalize(p_camera + self.dx_camera)
            ft = self.focal_distance / dx[2]
            p_focus = ft * dx
            rxo = np.array([lens_u, lens_v, 0.0])
            rxd = normalize(p_focus - rxo)

            dy = normalize(p_camera + self.dy_camera)
            ft = self.focal_distance / dy[2]
            p_focus = ft * dy
            ryo = np.array([lens_u, lens_v, 0.0])
            ryd = normalize(p_focus - ryo)
            
            ray.set_differentials(rxo, rxd, ryo, ryd)
        else:
            ray.set_differentials(ray.o.copy(), normalize(p_camera + self.dx_camera), ray.o.copy(), normalize(p_camera + self.dy_camera))
        
        ray.time = sample.time
        ray = self.camera_to_world(ray)
        
        return 1.0, ray
