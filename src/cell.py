from abc import ABCMeta
import numpy as np

###############################################################################
## AbstractCell
###############################################################################
class AbstractCell(object):
    
    __metaclass__ = ABCMeta
    
    def append(self, shapes):
        return self
    
    def intersect_exclusive(self, excl, ray, isect=None):
        return self.intersect(ray=ray, isect=isect)
        
###############################################################################
## AlwaysHitCell
###############################################################################
class AlwaysHitCell(AbstractCell):
    
    def __init__(self):
        super(AlwaysHitCell, self).__init__()
    
    def intersect(self, ray, isect=None):
        return True
        
###############################################################################
## NeverHitCell
############################################################################### 
class NeverHitCell(AbstractCell):
    
    def __init__(self):
        super(NeverHitCell, self).__init__()
    
    def intersect(self, ray, isect=None):
        return False
  
###############################################################################
## FloatHitCell
###############################################################################  
class FloatHitCell(AbstractCell):
    
    def __init__(self, threshold=1.0, rng=None):
        super(FloatHitCell, self).__init__()
        self.threshold = threshold
        if rng is None:
            self.rng = np.random
        else:
            self.rng = rng

    def intersect(self, ray, isect=None):
        return self.rng.uniform() < self.threshold

###############################################################################
## BinaryHitCell
###############################################################################
class BinaryHitCell(AbstractCell):
    
    def __init__(self, hit=False):
        super(BinaryHitCell, self).__init__()
        self.hit = hit
    
    def append(self, shapes):
        if type(shapes) is list:
            self.hit |= (len(shapes) != 0)
        else:
            self.hit = True
        return self
    
    def intersect(self, ray, isect=None):
        return self.hit
