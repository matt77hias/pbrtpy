###############################################################################
## RandomSampler
###############################################################################
from sampler import Sampler
from sampling import Sampler3D

class RandomSampler(Sampler):

    def __init__(self, x_start, x_end, y_start, y_end, spp, shutter_open, shutter_close):
        super(RandomSampler, self).__init__(x_start, x_end, y_start, y_end, spp, shutter_open, shutter_close)
        self.x_pos = self.x_pixel_start
        self.y_pos = self.y_pixel_start

        rng = Sampler3D(seed=x_start + y_start * (x_end-x_start))
        self.image_samples = rng.uniform(size=5*spp)

        # Shift image samples to pixel coordinates
        for o in range(0, 2*self.spp, 2):
            self.image_samples[o]   += self.x_pos
            self.image_samples[o+1] += self.y_pos

        self.sample_pos = 0
        
    def get_more_samples(self, samples, rng):
        if self.sample_pos == self.spp:
            if (self.x_pixel_start == self.x_pixel_end) or (self.y_pixel_start == self.y_pixel_end):
                return 0
            self.x_pos += 1
            if self.x_pos == self.x_pixel_end:
                self.x_pos = self.x_pixel_start
                self.y_pos += 1
            if self.y_pos == self.y_pixel_end:
                return 0

            self.image_samples = rng.uniform(size=5*self.spp)

            # Shift image samples to pixel coordinates
            for o in range(0, 2*self.spp, 2):
                self.image_samples[o]   += self.x_pos
                self.image_samples[o+1] += self.y_pos

            self.sample_pos = 0

        # Return next sample point
        sample = samples[0]
        sample.image_x = self.image_samples[2*self.sample_pos]
        sample.image_y = self.image_samples[2*self.sample_pos + 1]
        sample.lens_u  = self.image_samples[2*self.spp + 2*self.sample_pos]
        sample.lens_v  = self.image_samples[2*self.spp + 2*self.sample_pos + 1]
        sample.time    = self.image_samples[4*self.spp +   self.sample_pos]

        # Generate stratified samples for integrators
        for i in range(len(sample.n1D)):
            for j in range(sample.n1D[i]):
                sample.oneD[i][j] = rng.random_float()
        for i in range(len(sample.n2D)):
            for j in range(2*sample.n2D[i]):
                sample.twoD[i][j] = rng.random_float()
        
        self.sample_pos += 1
        return 1

    def maximum_sample_count(self):
        return 1

    def get_sub_sampler(self, num, count):
        x0, x1, y0, y1 = self.compute_sub_window(num, count)
        if (x0 == x1) or (y0 == y1):
            return None
        return RandomSampler(x0, x1, y0, y1, self.spp, self.shutter_open, self.shutter_close)

    def round_size(self, size):
        return size
