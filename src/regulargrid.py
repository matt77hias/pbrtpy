import numpy as np
from math_utils import clamp, round2int

MAX_NB_CELLS = 64

###############################################################################
## RegularGrid
###############################################################################
from aggregate import Aggregate
from group import Group
from line import Line
from threading import Lock

class RegularGrid(Aggregate):

    def __init__(self, shapes=[], resolution=None, i=None, color='k', cell_type=Group):
        super(RegularGrid, self).__init__(shapes=shapes, i=i, color=color)
        self.access_count = 0
        self.lock = Lock()
        self._build(cell_type=cell_type)

    def _build(self, cell_type=Group, resolution=None, **kwargs):
        # Grid resolution
        self.bounds = super(RegularGrid, self).bounds()
        d = self.bounds.diagonal()
        if resolution is None:
            max_axis = self.bounds.maximum_extent()
            inv_max_width = 1.0 / d[max_axis]
            cube_root = 3.0 * pow(float(len(self.shapes)), 1.0/3.0)
            cells_per_unit_dist = cube_root * inv_max_width
            self.shape = np.zeros((3), dtype=int)
            for axis in range(3):
                self.shape[axis] = round2int(d[axis] * cells_per_unit_dist)
                self.shape[axis] = clamp(self.shape[axis], 1, MAX_NB_CELLS)
        else:
            self.shape = resolution.copy()
        self.width = np.zeros((3))
        self.inv_width = np.zeros((3))
        for axis in range(3):
            self.width[axis] = d[axis] / self.shape[axis]
            if self.width[axis] == 0.0:
                self.inv_width[axis] = 0.0
            else:
                self.inv_width[axis] = 1.0 / self.width[axis]

        self.cells = np.empty((self.shape[0], self.shape[1], self.shape[2]), dtype=cell_type)
        if cell_type is not Group:
            for x in range(self.shape[0]):
                for y in range(self.shape[1]):
                    for z in range(self.shape[2]):
                        self.cells[x,y,z] = cell_type()

        # Partition shapes
        for shape in self.shapes:
            box = shape.bounds()
            cell_min = np.zeros((3), dtype=int)
            cell_max = np.zeros((3), dtype=int)
            for axis in range(3):
                cell_min[axis] = self._cell(box.pMin, axis)
                cell_max[axis] = self._cell(box.pMax, axis)
       
            for x in range(cell_min[0], cell_max[0]+1):
                for y in range(cell_min[1], cell_max[1]+1):
                    for z in range(cell_min[2], cell_max[2]+1):
                        if self.cells[x,y,z] is None:
                            self.cells[x,y,z] = cell_type(shape)
                        else:
                            self.cells[x,y,z].append(shape)

    def _cell(self, point, axis):
        return clamp(int((point[axis] - self.bounds.pMin[axis]) * self.inv_width[axis]), 0, self.shape[axis]-1)

    def _pos(self, point,  axis):
        return self.bounds.pMin[axis] + point * self.width[axis]

    def bounds(self):
        return self.bounds

    def intersect(self, ray, isect=None):
        self.lock.acquire()
        self.access_count += 1
        self.lock.release()

        if isect is None:
            if self.bounds.inside(ray(ray.tMin)):
                ray_t = ray.tMin
            else:
                hit, ray_t, _, _, _ =  self.bounds.intersect_info(ray)
                if not hit:
                    return False
            grid_isect = ray(ray_t)

            # Set up 3D DDA for ray
            next_crossing_t = np.zeros((3))
            delta_t = np.zeros((3))
            step = np.zeros((3), dtype=int)
            out = np.zeros((3), dtype=int)
            pos = np.zeros((3), dtype=int)
            for axis in range(3):
                # Compute current cell for axis
                pos[axis] = self._cell(grid_isect, axis)
                if ray.d[axis] >= 0.0:
                    # Handle ray with positive direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis]+1, axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = self.width[axis] / ray.d[axis]
                    step[axis] = 1
                    out[axis] = self.shape[axis]
                else:
                    # Handle ray with negative direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis], axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = -self.width[axis] / ray.d[axis]
                    step[axis] = -1
                    out[axis] = -1

            # Walk ray through cell grid
            hit = False
            while True:
                # Check for intersection in current cell and advance to next
                cell = self.cells[pos[0], pos[1], pos[2]]
                if (cell is not None) and cell.intersect(ray):
                    return True
                ray.stats.scount += 1

                # Advance to next cell
                bits = ((next_crossing_t[0] < next_crossing_t[1]) << 2) + \
                       ((next_crossing_t[0] < next_crossing_t[2]) << 1) + \
                       ((next_crossing_t[1] < next_crossing_t[2]))
                compare_to_axis = [2, 1, 2, 1, 2, 2, 0, 0]
                step_axis = compare_to_axis[bits]
                if (ray.tMax < next_crossing_t[step_axis]):
                    break
                pos[step_axis] += step[step_axis]
                if pos[step_axis] == out[step_axis]:
                    break
                next_crossing_t[step_axis] += delta_t[step_axis]

            return False
        else:
            if self.bounds.inside(ray(ray.tMin)):
                ray_t = ray.tMin
            else:
                hit, ray_t, _, _, _ =  self.bounds.intersect_info(ray)
                if not hit:
                    return False
            grid_isect = ray(ray_t)

            # Set up 3D DDA for ray
            next_crossing_t = np.zeros((3))
            delta_t = np.zeros((3))
            step = np.zeros((3), dtype=int)
            out = np.zeros((3), dtype=int)
            pos = np.zeros((3), dtype=int)
            for axis in range(3):
                # Compute current cell for axis
                pos[axis] = self._cell(grid_isect, axis)
                if ray.d[axis] >= 0.0:
                    # Handle ray with positive direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis]+1, axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = self.width[axis] / ray.d[axis]
                    step[axis] = 1
                    out[axis] = self.shape[axis]
                else:
                    # Handle ray with negative direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis], axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = -self.width[axis] / ray.d[axis]
                    step[axis] = -1
                    out[axis] = -1

            # Walk ray through cell grid
            hit = False
            while True:
                # Check for intersection in current cell and advance to next
                cell = self.cells[pos[0], pos[1], pos[2]]
                if cell is not None:
                    hit |= cell.intersect(ray, isect)
                ray.stats.pcount += 1

                # Advance to next cell
                bits = ((next_crossing_t[0] < next_crossing_t[1]) << 2) + \
                       ((next_crossing_t[0] < next_crossing_t[2]) << 1) + \
                       ((next_crossing_t[1] < next_crossing_t[2]))
                compare_to_axis = [2, 1, 2, 1, 2, 2, 0, 0]
                step_axis = compare_to_axis[bits]
                if (ray.tMax < next_crossing_t[step_axis]):
                    break
                pos[step_axis] += step[step_axis]
                if pos[step_axis] == out[step_axis]:
                    break
                next_crossing_t[step_axis] += delta_t[step_axis]

            return hit

    def intersect_exclusive(self, excl, ray, isect=None):
        self.lock.aquire()
        self.access_count += 1
        self.lock.release()

        if isect is None:
            if self.bounds.inside(ray(ray.tMin)):
                ray_t = ray.tMin
            else:
                hit, ray_t, _, _, _ =  self.bounds.intersect_info(ray)
                if not hit:
                    return False
            grid_isect = ray(ray_t)

            # Set up 3D DDA for ray
            next_crossing_t = np.zeros((3))
            delta_t = np.zeros((3))
            step = np.zeros((3), dtype=int)
            out = np.zeros((3), dtype=int)
            pos = np.zeros((3), dtype=int)
            for axis in range(3):
                # Compute current cell for axis
                pos[axis] = self._cell(grid_isect, axis)
                if ray.d[axis] >= 0.0:
                    # Handle ray with positive direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis]+1, axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = self.width[axis] / ray.d[axis]
                    step[axis] = 1
                    out[axis] = self.shape[axis]
                else:
                    # Handle ray with negative direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis], axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = -self.width[axis] / ray.d[axis]
                    step[axis] = -1
                    out[axis] = -1

            # Walk ray through cell grid
            hit = False
            while True:
                # Check for intersection in current cell and advance to next
                cell = self.cells[pos[0], pos[1], pos[2]]
                if (cell is not None) and cell.intersect_exclusive(self, excl, ray):
                    return True
                ray.stats.scount += 1

                # Advance to next cell
                bits = ((next_crossing_t[0] < next_crossing_t[1]) << 2) + \
                       ((next_crossing_t[0] < next_crossing_t[2]) << 1) + \
                       ((next_crossing_t[1] < next_crossing_t[2]))
                compare_to_axis = [2, 1, 2, 1, 2, 2, 0, 0]
                step_axis = compare_to_axis[bits]
                if (ray.tMax < next_crossing_t[step_axis]):
                    break
                pos[step_axis] += step[step_axis]
                if pos[step_axis] == out[step_axis]:
                    break
                next_crossing_t[step_axis] += delta_t[step_axis]

            return False
        else:
            if self.bounds.inside(ray(ray.tMin)):
                ray_t = ray.tMin
            else:
                hit, ray_t, _, _, _ =  self.bounds.intersect_info(ray)
                if not hit:
                    return False
            grid_isect = ray(ray_t)

            # Set up 3D DDA for ray
            next_crossing_t = np.zeros((3))
            delta_t = np.zeros((3))
            step = np.zeros((3), dtype=int)
            out = np.zeros((3), dtype=int)
            pos = np.zeros((3), dtype=int)
            for axis in range(3):
                # Compute current cell for axis
                pos[axis] = self._cell(grid_isect, axis)
                if ray.d[axis] >= 0.0:
                    # Handle ray with positive direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis]+1, axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = self.width[axis] / ray.d[axis]
                    step[axis] = 1
                    out[axis] = self.shape[axis]
                else:
                    # Handle ray with negative direction for cell stepping
                    next_crossing_t[axis] = ray_t + (self._pos(pos[axis], axis) - grid_isect[axis]) / ray.d[axis]
                    delta_t[axis] = -self.width[axis] / ray.d[axis]
                    step[axis] = -1
                    out[axis] = -1

            # Walk ray through cell grid
            hit = False
            while True:
                # Check for intersection in current cell and advance to next
                cell = self.cells[pos[0], pos[1], pos[2]]
                if cell is not None:
                    hit |= cell.intersect_exclusive(self, excl, ray, isect)
                ray.stats.pcount += 1

                # Advance to next cell
                bits = ((next_crossing_t[0] < next_crossing_t[1]) << 2) + \
                       ((next_crossing_t[0] < next_crossing_t[2]) << 1) + \
                       ((next_crossing_t[1] < next_crossing_t[2]))
                compare_to_axis = [2, 1, 2, 1, 2, 2, 0, 0]
                step_axis = compare_to_axis[bits]
                if (ray.tMax < next_crossing_t[step_axis]):
                    break
                pos[step_axis] += step[step_axis]
                if pos[step_axis] == out[step_axis]:
                    break
                next_crossing_t[step_axis] += delta_t[step_axis]

            return hit

    def accept(self, visitor, grid=False, **kwargs):
        super(RegularGrid, self).accept(visitor)
        # TODO: use NAABBs instead of lines for general visitor support?
        if grid:
            # fixed z lines
            for x in range(self.shape[0]+1):
                for y in range(self.shape[1]+1):
                    v1 = self.bounds.pMin.__copy__()
                    v1[0] += x * self.width[0]
                    v1[1] += y * self.width[1]
                    v2 = v1.copy()
                    v2[2] = self.bounds.pMax[2]
                    Line(v1, v2, color=self.color).accept(visitor)
            # fixed x lines
            for y in range(self.shape[1]+1):
                for z in range(self.shape[2]+1):
                    v1 = self.bounds.pMin.__copy__()
                    v1[1] += y * self.width[1]
                    v1[2] += z * self.width[2]
                    v2 = v1.copy()
                    v2[0] = self.bounds.pMax[0]
                    Line(v1, v2, color=self.color).accept(visitor)
            # fixed y lines
            for z in range(self.shape[2]+1):
                for x in range(self.shape[0]+1):
                    v1 = self.bounds.pMin.__copy__()
                    v1[2] += z * self.width[2]
                    v1[0] += x * self.width[0]
                    v2 = v1.copy()
                    v2[1] = self.bounds.pMax[1]
                    Line(v1, v2, color=self.color).accept(visitor)
