from transform import look_at, scale, translate

###############################################################################
## Camera Utilities
###############################################################################
def cam2world(pos, look, up, T=scale(-1.0, 1.0, 1.0)):
    return (T * look_at(pos, look, up)).inverse()

###############################################################################
## Camera
###############################################################################
from abc import ABCMeta, abstractmethod
from entity import Entity
from logger import logger

class Camera(Entity):

    __metaclass__ = ABCMeta
    
    def __init__(self, camera_to_world, film, shutter_open=0.0, shutter_close=1.0, color='k'):
        super(Camera, self).__init__(color=color)
        self.camera_to_world = camera_to_world
        if shutter_open <= shutter_close:
            self.shutter_open    = float(shutter_open)
            self.shutter_close   = float(shutter_close)
        else:
            self.shutter_open    = float(shutter_close)
            self.shutter_close   = float(shutter_open)
        self.film            = film
        if camera_to_world.has_scale():
            logger.warning(
                'Scaling detected in world-to-camera transformation!\n' \
                'The system has numerous assumptions, implicit and explicit,\n' \
                'that this transform will have no scale factors in it.\n' \
                'Proceed at your own risk; your image may have errors or\n' \
                'the system may crash as a result of this.')
       
    def dim(self):
        return 3
       
    @abstractmethod
    def generate_ray(self, sample):
        return

    def generate_ray_differential(self, sample):
        w, ray = self.generate_ray(sample)
        
        shift = sample.__copy__()
        
        # Find ray after shifting one pixel in the x direction
        shift.image_x += 1
        wx, ray_x = self.generate_ray(shift)

        shift.image_x -= 1

        # Find ray after shifting one pixel in the y direction
        shift.image_y += 1
        wy, ray_y = self.generate_ray(shift)

        if (wx == 0.0) or (wy == 0.0):
            return 0.0, ray
            
        ray.set_differentials(ray_x.o, ray_x.d, ray_y.o, ray_y.d)
        return w, ray
    
###############################################################################
## ProjectiveCamera
###############################################################################
class ProjectiveCamera(Camera):

    def __init__(self, camera_to_world, projection, screen_window, film, shutter_open=0.0, shutter_close=1.0, lens_radius=0.0, focal_distance=10.0**30, color='k'):
        super(ProjectiveCamera, self).__init__(camera_to_world, film, shutter_open=shutter_open, shutter_close=shutter_close, color=color)
        
        self.lens_radius = float(lens_radius)
        self.focal_distance = float(focal_distance)
        self.camera_to_screen = projection

        # Compute projective camera screen transformations
        sc1 = scale(float(film.x_resolution), float(film.y_resolution), 1.0)
        sc2 = scale(1.0 / (screen_window[1] - screen_window[0]), 1.0 / (screen_window[2] - screen_window[3]), 1.0)
        tr  = translate(-screen_window[0], -screen_window[3], 0.0)
        self.screen_to_raster = sc1 * sc2 * tr
        self.raster_to_screen = self.screen_to_raster.inverse()
        self.raster_to_camera = self.camera_to_screen.inverse() * self.raster_to_screen
