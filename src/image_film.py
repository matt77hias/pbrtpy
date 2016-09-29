from cv2 import imwrite
import numpy as np

from spectrum_utils import rgb_to_xyz, xyz_to_rgb

FILTER_TABLE_SIZE = 16

###################################################################################################################################################################################
## ImageFilm
###################################################################################################################################################################################
from film import Film
from box_filter import BoxFilter

class ImageFilm(Film):
    
    def __init__(self, x_res=640, y_res=480, fIlter=BoxFilter(), crop_window=np.array([0.0, 1.0, 0.0, 1.0]), fname='pbrtpy.png'):
        super(ImageFilm, self).__init__(x_res, y_res)
        self.filter = fIlter
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
        self.pixels = np.empty((self.x_pixel_count, self.y_pixel_count), dtype=ImagePixel)
        for i in range(self.x_pixel_count):
            for j in range(self.y_pixel_count):
                self.pixels[i,j] = ImagePixel()
        
        # Precompute filter weight table
        self.filter_table = [0.0] * (FILTER_TABLE_SIZE * FILTER_TABLE_SIZE)
        for y in range(FILTER_TABLE_SIZE):
            fy = (float(y) + 0.5) * self.filter.y_width / float(FILTER_TABLE_SIZE)
            for x in range(FILTER_TABLE_SIZE):
                fx = (float(x) + 0.5) * self.filter.x_width / float(FILTER_TABLE_SIZE)
                self.filter_table[y * FILTER_TABLE_SIZE + x] = self.filter.evaluate(fx, fy)
        
    def add_sample(self, sample, L, ray):
        d_image_x = sample.image_x - 0.5
        d_image_y = sample.image_y - 0.5
        x0 = int(np.ceil(d_image_x - self.filter.x_width))
        x1 = int(d_image_x + self.filter.x_width)
        y0 = int(np.ceil(d_image_y - self.filter.y_width))
        y1 = int(d_image_y + self.filter.y_width)
        x0 = max(x0, self.x_pixel_start)
        x1 = min(x1, self.x_pixel_start + self.x_pixel_count - 1)
        y0 = max(y0, self.y_pixel_start)
        y1 = min(y1, self.y_pixel_start + self.y_pixel_count - 1)
        if ((x1-x0)<0) or ((y1-y0)<0):
            return

        # Loop over filter support and add sample to pixel arrays
        L_xyz = rgb_to_xyz(L)

        # Precompute x and y filter table offsets
        ifx = []
        for x in range(x0, x1+1):
            fx = abs((x - d_image_x) * self.filter.inv_x_width * FILTER_TABLE_SIZE)
            ifx.append(min(int(fx), FILTER_TABLE_SIZE-1))
        ify = []
        for y in range(y0, y1+1):
            fy = abs((y - d_image_y) * self.filter.inv_y_width * FILTER_TABLE_SIZE)
            ify.append(min(int(fy), FILTER_TABLE_SIZE-1))
        sync_needed = (self.filter.x_width > 0.5) or (self.filter.y_width > 0.5)
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                # Evaluate filter value at (x,y) pixel
                offset = ify[y-y0]*FILTER_TABLE_SIZE + ifx[x-x0]
                filter_weight = self.filter_table[offset]
                # Update pixel values with filtered sample contribution
                if not sync_needed:
                    self.pixels[x,y].update_unsafe(L_xyz, filter_weight)
                else:
                    self.pixels[x,y].update(L_xyz, filter_weight)

    def splat(self, sample, L):
        x = int(sample.image_x)
        y = int(sample.image_y)
        if (x < self.x_pixel_start) or (x - self.x_pixel_start >= self.x_pixel_count) or (y < self.y_pixel_start) or (y - self.y_pixel_start >= self.y_pixel_count):
            return
        y = y - self.y_pixel_start
        x = x - self.x_pixel_start

        L_xyz = rgb_to_xyz(L)
        self.pixels[x,y].update_splat(L_xyz)
        
    def get_sample_extent(self):
        x_start = int(self.x_pixel_start + 0.5 - self.filter.x_width)
        x_end   = int(np.ceil(self.x_pixel_start + 0.5 + self.x_pixel_count + self.filter.x_width))
        y_start = int(self.y_pixel_start + 0.5 - self.filter.y_width)
        y_end   = int(np.ceil(self.y_pixel_start + 0.5 + self.y_pixel_count + self.filter.y_width))
        return x_start, x_end, y_start, y_end

    def get_pixel_extent(self):
        x_start = self.x_pixel_start
        x_end   = self.x_pixel_start + self.x_pixel_count
        y_start = self.y_pixel_start
        y_end   = self.y_pixel_start + self.y_pixel_count
        return x_start, x_end, y_start, y_end

    def write_image(self, splat_scale=1.0):
        img = np.zeros((self.x_pixel_count, self.y_pixel_count, 3))
        for x in range(self.x_pixel_count):
            for y in range(self.y_pixel_count):
                pixel = self.pixels[x,y]

                # Convert pixel XYZ color to RGB
                rgb = xyz_to_rgb(pixel.L_xyz)

                # Normalize pixel with weight sum
                if pixel.weight_sum != 0.0:
                    rgb = np.maximum(0.0, rgb / pixel.weight_sum) 

                # Add splat value at pixel
                rgb += splat_scale * pixel.splat_xyz
                
                img[x,y,:] = 255 * rgb
        
        imwrite(self.fname, np.transpose(img, axes=(1,0,2)))
        
###################################################################################################################################################################################
## ImagePixel
###################################################################################################################################################################################      
from threading import Lock

class ImagePixel(object):
    def __init__(self):
        self.L_xyz = np.zeros((3))
        self.weight_sum = 0.0
        self.splat_xyz = np.zeros((3))
        self.pad = 0.0
        self.lock = Lock()
        
    def update(self, L, filter_weight):
        self.lock.aquire()
        self.L_xyz      += filter_weight * L
        self.weight_sum += filter_weight
        self.lock.release()
        
    def update_unsafe(self, L, filter_weight):
        self.L_xyz      += filter_weight * L
        self.weight_sum += filter_weight
        
    def update_splat(self, L):
        self.lock.aquire()
        self.splat_xyz = L
        self.lock.release()