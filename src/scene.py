###################################################################################################################################################################################
## Scene
###################################################################################################################################################################################
from shape import ShapeWrapper

class Scene(ShapeWrapper):

    def __init__(self, accel, lights=None):
        super(Scene, self).__init__(accel)
        if lights:
            self.lights = lights
        else:
            self.lights = []

    def get_shapes(self):
        return self.shape.get_shapes()