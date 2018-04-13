from math_utils import lerp

###############################################################################
## Sampler
###############################################################################
from abc import ABCMeta, abstractmethod

class Sampler(object):

    __metaclass__ = ABCMeta
    
    def __init__(self, x_start, x_end, y_start, y_end, spp, shutter_open, shutter_close):
        self.x_pixel_start = x_start
        self.x_pixel_end   = x_end
        self.y_pixel_start = y_start
        self.y_pixel_end   = y_end
        self.spp           = spp
        self.shutter_open  = shutter_open
        self.shutter_close = shutter_close

    @abstractmethod
    def get_more_samples(self, sample, rng):
        return

    @abstractmethod
    def maximum_sample_count(self):
        return

    def report_results(self, samples, rays, ls, intersections, count):
        return True

    @abstractmethod
    def get_sub_sampler(self, num, count):
        return

    @abstractmethod
    def round_size(self, size):
        return

    def compute_sub_window(self, num, count):
        dx = self.x_pixel_end - self.x_pixel_start
        dy = self.y_pixel_end - self.y_pixel_start
        nx = count
        ny = 1
        while(((nx & 0x1) == 0) and ((2*dx*ny) < (dy*nx))):
            nx >>= 1
            ny <<= 1

        xo = num % nx
        yo = num // nx
        tx0 = float(xo)   / float(nx)
        tx1 = float(xo+1) / float(nx)
        ty0 = float(yo)   / float(ny)
        ty1 = float(yo+1) / float(ny)

        x_start = int(lerp(tx0, self.x_pixel_end, self.x_pixel_start))
        x_end   = int(lerp(tx1, self.x_pixel_end, self.x_pixel_start))
        y_start = int(lerp(ty0, self.y_pixel_end, self.y_pixel_start))
        y_end   = int(lerp(ty1, self.y_pixel_end, self.y_pixel_start))
        
        return x_start, x_end, y_start, y_end

###############################################################################
## CameraSample
###############################################################################
class CameraSample(object):

    def __init__(self, image_x=0.0, image_y=0.0, lens_u=0.0, lens_v=0.0, time=0.0):
        self.image_x = image_x
        self.image_y = image_y
        self.lens_u = lens_u
        self.lens_v = lens_v
        self.time = time
        
    def __copy__(self):
        return self.__deepcopy__()
    
    def __deepcopy__(self):
        return type(self)(image_x=self.image_x, image_y=self.image_y, lens_u=self.lens_u, lens_v=self.lens_v, time=self.time)

###############################################################################
## Sample
###############################################################################
from copy import copy

class Sample(CameraSample):

    def __init__(self, sampler=None, surface_integrator=None, volume_integrator=None, scene=None):
        super(Sample, self).__init__()
        self.n1D = []
        self.n2D = []
        self.oneD = None
        self.twoD = None 
        if surface_integrator:
           surface_integrator.request_samples(sampler, self, scene)
        if volume_integrator:
            volume_integrator.request_samples(sampler, self, scene)

    def add_1D(self, num):
        self.n1D.append(num)
        return len(self.n1D)-1

    def add_2D(self, num):
        self.n2D.append(num)
        return len(self.n2D)-1

    def duplicate(self, count):
        ret = [None] * count
        for i in range(count):
            sample = Sample()
            sample.n1D = copy(self.n1D)
            sample.n2D = copy(self.n2D)
            ret[i] = sample
        return ret
