###################################################################################################################################################################################
## MultiFilm
###################################################################################################################################################################################
from film import Film

class MultiFilm(Film):

    def __init__(self, x_res, y_res):
        super(MultiFilm, self).__init__(x_res, y_res)
        self.films = []
        
    def add_film(self, film):
        self.films.append(film)
        
    def add_sample(self, sample, L, ray):
        for film in self.films:
            film.add_sample(sample, L, ray)

    def splat(self, sample, L):
        for film in self.films:
            film.splat(sample, L)

    def get_sample_extent(self):
        return self.films[0].get_sample_extent()

    def get_pixel_extent(self):
        return self.films[0].get_sample_extent()
    
    def update_display(self, x0, y0, x1, y1, splat_scale=1.0):
        for film in self.films:
            film.update_display(x0, y0, x1, y1, splat_scale=splat_scale)

    def write_image(self, splat_scale=1.0):
        for film in self.films:
            film.write_image(splat_scale=splat_scale)