###############################################################################
## BoxFilter
###############################################################################
from filter import Filter

class BoxFilter(Filter):

    def __init__(self, x_width=0.5, y_width=0.5):
        super(BoxFilter, self).__init__(x_width, y_width)

    def evaluate(self, x, y):
        return 1.0
