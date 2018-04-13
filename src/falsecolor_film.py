import numpy as np

###############################################################################
## ImageFilm
###############################################################################
from film import Film

class FalseColorFilm(Film):
    
    def __init__(self, x_res=640, y_res=480, crop_window=np.array([0.0, 1.0, 0.0, 1.0]), fname='pbrtpy.png'):
        super(FalseColorFilm, self).__init__(x_res, y_res)
        self.fname = fname

        # Compute film image extent
        self.x_pixel_start = int(np.ceil(self.x_resolution * crop_window[0]))
        self.x_pixel_count = max(1, int(np.ceil(self.x_resolution * crop_window[1]) - self.x_pixel_start))
        self.y_pixel_start = int(np.ceil(self.y_resolution * crop_window[2]))
        self.y_pixel_count = max(1, int(np.ceil(self.y_resolution * crop_window[3]) - self.y_pixel_start))
        if self.x_pixel_count>self.x_resolution:
            raise ValueError
        if self.y_pixel_count>self.y_resolution:
            raise ValueError

        # Allocate film image storage
        self.pixels  = np.empty((self.x_pixel_count, self.y_pixel_count), dtype=FalseColorPixel)
        for i in range(self.x_pixel_count):
            for j in range(self.y_pixel_count):
                self.pixels[i,j] = FalseColorPixel()
        
    def add_sample(self, sample, L, ray):
        d_image_x = sample.image_x - 0.5
        d_image_y = sample.image_y - 0.5
        x0 = int(np.ceil(d_image_x - 0.5))
        x1 = int(d_image_x + 0.5)
        y0 = int(np.ceil(d_image_y - 0.5))
        y1 = int(d_image_y + 0.5)
        x0 = max(x0, self.x_pixel_start)
        x1 = min(x1, self.x_pixel_start + self.x_pixel_count - 1)
        y0 = max(y0, self.y_pixel_start)
        y1 = min(y1, self.y_pixel_start + self.y_pixel_count - 1)
        if ((x1-x0)<0) or ((y1-y0)<0):
            return
            
        for x in range(x0, x1+1):
            for y in range(y0, y1+1):
                self.pixels[x,y].update(ray)

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
        pD = np.zeros((self.x_pixel_count, self.y_pixel_count), dtype=np.int64)
        sD = np.zeros((self.x_pixel_count, self.y_pixel_count), dtype=np.int64)
        rD = np.zeros((self.x_pixel_count, self.y_pixel_count), dtype=np.int64)
        tD = np.zeros((self.x_pixel_count, self.y_pixel_count), dtype=np.int64)
        for x in range(self.x_pixel_count):
            for y in range(self.y_pixel_count):
                pixel   = self.pixels[x,y]
                pD[x,y] = pixel.pcount
                sD[x,y] = pixel.scount
                rD[x,y] = pixel.rcount
                tD[x,y] = pixel.tcount
        np.savetxt(self.fname + '-p.falsecolor', np.transpose(pD), fmt='%i') 
        np.savetxt(self.fname + '-s.falsecolor', np.transpose(sD), fmt='%i')
        np.savetxt(self.fname + '-r.falsecolor', np.transpose(rD), fmt='%i')
        np.savetxt(self.fname + '-t.falsecolor', np.transpose(tD), fmt='%i')   
        
###############################################################################
## FalseColorPixel
###############################################################################      
class FalseColorPixel(object):
    def __init__(self):
        self.pcount = 0
        self.scount = 0
        self.rcount = 0
        self.tcount = 0
        
    def update(self, ray):
        self.pcount += ray.stats.pcount
        self.scount += ray.stats.scount
        self.rcount += ray.stats.rcount
        self.tcount += ray.stats.tcount
