import numpy as np

###############################################################################
## OcclusionIntegrator
###############################################################################
from integrator import SurfaceIntegrator

class OcclusionIntegrator(SurfaceIntegrator):

    def __init__(self):
        super(SurfaceIntegrator, self).__init__()

    def Li(self, scene, renderer, ray, isect, sample, rng):
        return np.ones(3)
