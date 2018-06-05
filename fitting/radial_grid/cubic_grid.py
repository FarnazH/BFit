# -*- coding: utf-8 -*-
# A basis-set curve-fitting optimization package.
# Copyright (C) 2018 The FittingBasisSets Development Team.
#
# This file is part of FittingBasisSets.
#
# FittingBasisSets is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# FittingBasisSets is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# ---
import numpy as np
from fitting.radial_grid.general_grid import RadialGrid

__all__ = ["CubicGrid"]


class CubicGrid(RadialGrid):
    def __init__(self, grid, step_size):
        self.step = step_size
        super(CubicGrid, self).__init__(grid)

    def integrate(self, *args):
        total_arr = np.ma.asarray(np.ones(len(args[0])))
        for arr in args:
            total_arr *= arr
        return self.step**3. * np.sum(total_arr)

    def integrate_3d_space(self, *args):
        # Same as Integrating Normally.
        return self.integrate(*args)
