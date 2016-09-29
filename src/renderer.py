###################################################################################################################################################################################
## Renderer
###################################################################################################################################################################################
from abc import ABCMeta, abstractmethod

class Renderer(object):

    __metaclass__ = ABCMeta
    
    @abstractmethod
    def render(self, scene):
        return

    @abstractmethod
    def Li(self, scene, ray, sample, rng, isect=None):
        return