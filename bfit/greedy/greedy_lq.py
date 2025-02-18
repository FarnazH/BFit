# -*- coding: utf-8 -*-
# FittingBasisSets is a basis-set curve-fitting optimization package.
#
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
r"""

"""

import numpy as np

from bfit.greedy.greedy_strat import GreedyStrategy
from bfit.greedy.greedy_utils import get_next_choices
from bfit.greedy.optimize import optimize_using_nnls, optimize_using_slsqp
from bfit.model import AtomicGaussianDensity

__all__ = ["GreedyLeastSquares"]


class GreedyLeastSquares(GreedyStrategy):
    def __init__(self, grid, density, splitting_func=get_next_choices,
                 factor=2):
        self.gauss_obj = AtomicGaussianDensity(grid.points, num_s=density)
        self.grid = grid
        self.factor = factor
        self.splitting_func = splitting_func
        super(GreedyStrategy, self).__init__()

    @property
    def density(self):
        return self.gauss_obj._density

    def get_cost_function(self, params):
        self.gauss_obj.cost_function(params)

    def _solve_one_function_weight(self, weight):
        a = 2.0 * np.sum(weight)
        sum_of_grid_squared = np.sum(weight * np.power(self.grid.points, 2))
        b = 2.0 * sum_of_grid_squared
        sum_ln_electron_density = np.sum(weight * np.log(self.density))
        c = 2.0 * sum_ln_electron_density
        d = b
        e = 2.0 * np.sum(weight * np.power(self.grid.points, 4))
        f = 2.0 * np.sum(weight * np.power(self.grid.points, 2) *
                         np.log(self.density))
        big_a = (b * f - c * e) / (b * d - a * e)
        big_b = (a * f - c * d) / (a * e - b * d)
        coefficient = np.exp(big_a)
        exponent = - big_b
        return np.array([coefficient, exponent])

    def get_best_one_function_solution(self):
        # Minimizing weighted least squares with three different weights
        weight1 = np.ones(len(self.grid.points))
        weight3 = np.power(self.density, 2.)
        p1 = self._solve_one_function_weight(weight1)
        cost_func1 = self.gauss_obj.cost_function(p1)

        p2 = self._solve_one_function_weight(self.density)
        cost_func2 = self.gauss_obj.cost_function(p2)

        p3 = self._solve_one_function_weight(weight3)
        cost_func3 = self.gauss_obj.cost_function(p3)

        p_min = min([(cost_func1, p1), (cost_func2, p2), (cost_func3, p3)],
                    key=lambda t: t[0])

        # Minimize by analytically finding coefficient.
        val = 1e10
        if self.gauss_obj.element is not None:
            exp_choice1 = self.gauss_obj.generation_of_UGBS_exponents(1.25,
                                                                      self.ugbs)
            exp_choice2 = self.gauss_obj.generation_of_UGBS_exponents(1.5,
                                                                      self.ugbs)
            exp_choice3 = self.gauss_obj.generation_of_UGBS_exponents(1.75,
                                                                      self.ugbs)
            grid_squared = self.grid.points**2.
            best_found = None
            for exp in np.append((exp_choice1, exp_choice2, exp_choice3)):
                num = np.sum(self.density * np.exp(-exp * grid_squared))
                den = np.sum(np.exp(-2. * exp * grid_squared))
                c = num / den
                p = np.array([c, exp])
                p = self.get_optimization_routine(p)
                cost_func = self.gauss_obj.cost_function(p)
                if cost_func < val:
                    val = cost_func
                    best_found = p

        if p_min[0] < val:
            return p_min[1]
        return best_found

    def get_next_iter_params(self, params):
        return self.splitting_func(self.factor, params[:len(params)//2],
                                   params[len(params)//2:])

    def get_optimization_routine(self, params):
        exps = params[len(params)//2:]
        cofac_matrix = self.gauss_obj.create_cofactor_matrix(exps)
        coeffs = optimize_using_nnls(self.density, cofac_matrix)

        p = np.append(coeffs, exps)
        params = optimize_using_slsqp(self.gauss_obj, p)
        return params

    def get_errors_from_model(self, params):
        model = self.gauss_obj.create_model(params)
        err1 = self.gauss_obj.integrate_model_trapz(model)
        err2 = self.gauss_obj.get_integration_error(self.density, model)
        err3 = self.gauss_obj.get_error_diffuse(self.density, model)
        return [err1, err2, err3]
