import numpy as np

from math_utils import face_forward
from ray import Ray

###############################################################################
## AmbientOcclusionIntegrator
###############################################################################
from integrator import SurfaceIntegrator

class AmbientOcclusionIntegrator(SurfaceIntegrator):

    def __init__(self, nb_samples=1, max_distance=np.inf):
        super(SurfaceIntegrator, self).__init__()
        self.nb_samples = nb_samples
        self.max_distance = max_distance

    def Li(self, scene, renderer, ray, isect, sample, rng):
        n = face_forward(isect.n, -ray.d)
        nb_clear = 0
        for i in range(self.nb_samples):
            axis_w = n
            axis_u = np.cross(np.array([0.0, 1.0, 0.0]) if np.fabs(axis_w[0]) > 0.1 else np.array([1.0, 0.0, 0.0]), axis_w)
            axis_v = np.cross(axis_w, axis_u)
            sample_d = rng.cosine_weighted_uniform_sample_hemisphere()
            d = (sample_d[0] * axis_u + sample_d[1] * axis_v + sample_d[2] * axis_w)
            
            r = Ray(origin=isect.p, direction=d, start=0.01, end=self.max_distance)
            if not scene.intersect(r):
                nb_clear += 1
            ray.stats.scount += r.stats.pcount
            ray.stats.tcount += r.stats.rcount
        
        return np.ones(3) * (float(nb_clear) / self.nb_samples)
