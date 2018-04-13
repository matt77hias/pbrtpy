import numpy as np

###############################################################################
## WireframeFilm
###############################################################################
from film import Film
from wireframerenderer import Wireframe3DRenderer

class WireframeFilm(Film):
    
    def __init__(self, x_res=640, y_res=480, crop_window=np.array([0.0, 1.0, 0.0, 1.0]), wireframe_renderer=None, fname='pbrtpy.png'):
        super(WireframeFilm, self).__init__(x_res=x_res, y_res=y_res)
        self.fname = fname
        
        if wireframe_renderer:
            self.wireframe_renderer = wireframe_renderer
        else:
            self.wireframe_renderer = Wireframe3DRenderer()
        
        # Compute film image extent
        self.x_pixel_start = int(np.ceil(self.x_resolution * crop_window[0]))
        self.x_pixel_count = max(1, int(np.ceil(self.x_resolution * crop_window[1]) - self.x_pixel_start))
        self.y_pixel_start = int(np.ceil(self.y_resolution * crop_window[2]))
        self.y_pixel_count = max(1, int(np.ceil(self.y_resolution * crop_window[3]) - self.y_pixel_start))
        if self.x_pixel_count>self.x_resolution:
            raise ValueError
        if self.y_pixel_count>self.y_resolution:
            raise ValueError

    def add_sample(self, sample, L, ray):
        ray.accept(self.wireframe_renderer)

    def splat(self, sample, L):
        return

    def get_sample_extent(self):
        x_start = self.x_pixel_start
        x_end   = self.x_pixel_start + self.x_pixel_count + 1
        y_start = self.y_pixel_start
        y_end   = self.y_pixel_start + self.y_pixel_count + 1
        return x_start, x_end, y_start, y_end

    def get_pixel_extent(self):
        x_start = self.x_pixel_start
        x_end   = self.x_pixel_start + self.x_pixel_count
        y_start = self.y_pixel_start
        y_end   = self.y_pixel_start + self.y_pixel_count
        return x_start, x_end, y_start, y_end
    
    def write_image(self, splat_scale=1.0):
        self.wireframe_renderer.save(self.fname + '-wfr.png')
