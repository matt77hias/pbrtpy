import numpy as np

###################################################################################################################################################################################
## SamplerRendererTask
###################################################################################################################################################################################
from ray import Intersection
from sampling import Sampler3D
from spectrum_utils import y

class SamplerRendererTask():
    
    def __init__(self, scene, renderer, camera, sampler, sample, i, task_count, rng=None, max_iter=-1):
        self.scene = scene
        self.renderer = renderer
        self.camera = camera
        self.orig_sample = sample
        self.task_num = task_count-1-i
        self.task_count = task_count
        self.sampler = sampler.get_sub_sampler(self.task_num, self.task_count)
        if rng is None:
            self.rng = Sampler3D(seed=self.task_num)
        else:
            self.rng = rng
        self.max_iter = max_iter

    def __call__(self):
        print('Executing task %d/%d' % (self.task_num, self.task_count))
        
        if not self.sampler:
            return

        # Allocate space for samples and intersections
        max_samples = self.sampler.maximum_sample_count()
        samples     = self.orig_sample.duplicate(max_samples)
        rays        = [None] * max_samples
        Ls          = [None] * max_samples
        Ts          = [None] * max_samples
        isects      = np.empty(max_samples, dtype=Intersection)
        
        # Get samples from Sampler and update image
        while self.max_iter != 0:
            self.max_iter -= 1

            sample_count = self.sampler.get_more_samples(samples, self.rng)

            # If no more samples to compute, exit
            if sample_count <= 0:
                break
            
            # Generate camera rays and compute radiance along rays
            for i in range(sample_count):
                # Find camera ray for samples[i]
                ray_weight, ray_diff = self.camera.generate_ray_differential(samples[i])
                rays[i] = ray_diff
                coeff = 1.0 / np.sqrt(self.sampler.spp)
                ray_diff.scale_differentials(coeff)
                
                # Evaluate radiance along camera ray
                if ray_weight > 0.0:
                    radiance, intersection, Ts_i = self.renderer.Li(self.scene, ray_diff, samples[i], self.rng, isects[i])
                    Ls_i = ray_weight * radiance
                else:
                    Ls_i = np.zeros((3))
                    Ts_i = np.ones((3))
                
                # Check for unexpected radiance values
                if np.any(np.isnan(Ls_i)):
                    print('Not-a-number radiance value returned for image sample.  Setting to black.')
                    Ls_i = np.zeros((3))
                elif y(Ls_i)  < -1e-5:
                    print('Negative luminance value, %f, returned for image sample.  Setting to black.' % y(Ls_i))
                    Ls_i = np.zeros((3))
                elif y(Ls_i) == np.inf:
                    print('Infinite luminance value returned for image sample.  Setting to black.')
                    Ls_i = np.zeros((3))
                    
                Ls[i] = Ls_i
                Ts[i] = Ts_i

            # Report sample results to Sampler, add contributions to image
            if self.sampler.report_results(samples, rays, Ls, isects, sample_count):
                for i in range(sample_count):
                    self.camera.film.add_sample(samples[i], Ls[i], rays[i])
                    
        self.max_iter = -1

###################################################################################################################################################################################
## SamplerRenderer
###################################################################################################################################################################################
from multiprocessing.pool import ThreadPool

import global_configuration
from renderer import Renderer
from sampler import Sample

class SamplerRenderer(Renderer):

    def __init__(self, sampler, camera, surface_integrator, volume_integrator=None, first_pass_iter=0):
        super(SamplerRenderer, self).__init__()
        self.sampler = sampler
        self.camera = camera
        self.surface_integrator = surface_integrator
        self.volume_integrator = volume_integrator
        self.first_pass_iter = first_pass_iter
        
    def render(self, scene):
        # Allow integrators to do preprocessing for the scene
        self.surface_integrator.preprocess(scene, self.camera, self)
        if self.volume_integrator:
            self.volume_integrator.preprocess(scene, self.camera, self)

        # Allocate and initialize smaple
        self.sample = Sample(self.sampler, self.surface_integrator, self.volume_integrator, scene)

        # Compute number of SamplerRendererTasks to create for rendering
        n_cpus   = global_configuration.nb_cpus()
        n_pixels = self.camera.film.x_resolution * self.camera.film.y_resolution
        n_tasks  = max(32 * n_cpus, n_pixels // (16*16))
        n_tasks  = int(np.log2(n_tasks)) + 1
        tasks    = [None] * n_tasks
        
        if self.first_pass_iter == 0:
            for i in range(n_tasks):
                tasks[i] = SamplerRendererTask(scene, self, self.camera, self.sampler, self.sample, i, n_tasks).__call__

            print('First and only pass')
            if n_cpus > 1:
                pool = ThreadPool(processes=n_cpus)
                pool.map(lambda t: t(), tasks)
                pool.close()
                pool.join()
            else:
                map(lambda t: t(), tasks)
        else:
            for i in range(n_tasks):
                tasks[i] = SamplerRendererTask(scene, self, self.camera, self.sampler, self.sample, i, n_tasks, max_iter=self.first_pass_iter).__call__
        
            print('First pass')
            if n_cpus > 1:
                pool = ThreadPool(processes=n_cpus)
                pool.map(lambda t: t(), tasks)
                pool.close()
                pool.join()
            else:
                map(lambda t: t(), tasks)
                
            #TODO
                
            print('Last pass')
            if n_cpus > 1:
                pool = ThreadPool(processes=n_cpus)
                pool.map(lambda t: t(), tasks)
                pool.close()
                pool.join()
            else:
                map(lambda t: t(), tasks)
        
        # Store final image
        self.camera.film.write_image()

    def Li(self, scene, ray, sample, rng, intersection=None, T=None):
        # allocate local variables for isect and T if needed
        if not intersection:
            intersection = Intersection()
        if scene.intersect(ray, intersection):
            Li = self.surface_integrator.Li(scene, self, ray, intersection, sample, rng)
        else:
            Li = np.zeros((3))
            # Handle ray that doesn't intersect any geometry
            for light in scene.lights:
                Li += light.Le(ray)
        
        if self.volume_integrator:
            Lvi, T = self.volume_integrator.Li(scene, self, ray, sample, rng, T)
        else:
            Lvi, T = np.zeros((3)), np.ones((3))
        return (np.multiply(T, Li) + Lvi), intersection, T
                                        
    def transmittance(self, scene, ray, sample, rng):
        if self.volume_integrator:
            return self.volume_integrator.transmittance(scene, self, ray, sample, rng)
        else:
            return np.ones((3))