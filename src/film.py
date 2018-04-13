###############################################################################
## Film
###############################################################################
from abc import ABCMeta, abstractmethod

class Film(object):

    __metaclass__ = ABCMeta
    
    def __init__(self, x_res=640, y_res=480):
        self.x_resolution = x_res
        self.y_resolution = y_res

    @abstractmethod
    def add_sample(self, sample, L, ray):
        return

    def splat(self, sample, L):
        return

    @abstractmethod
    def get_sample_extent(self):
        return

    @abstractmethod
    def get_pixel_extent(self):
        return
    
    def update_display(self, x0, y0, x1, y1, splat_scale=1.0):
        return

    @abstractmethod
    def write_image(self, splat_scale=1.0):
        return
