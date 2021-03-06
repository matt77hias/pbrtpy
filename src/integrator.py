###############################################################################
## Integrator
###############################################################################
class Integrator(object):
    
    def preprocess(self, scene, camera, renderer):
        pass

    def request_samples(self, sampler, sample, scene):
        pass

###############################################################################
## SurfaceIntegrator
###############################################################################
from abc import ABCMeta, abstractmethod

class SurfaceIntegrator(Integrator):

    __metaclass__ = ABCMeta

    def __init__(self):
        super(SurfaceIntegrator, self).__init__()

    @abstractmethod
    def Li(self, scene, renderer, ray, intersection, sample, rng):
        return
