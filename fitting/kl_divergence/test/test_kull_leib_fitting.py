r"""Test file for 'fitting.mbis.mbis_abc'"""


import numpy as np
import numpy.testing as npt
from fitting.kl_divergence.kull_leib_fitting import KullbackLeiblerFitting
from fitting.radial_grid.radial_grid import ClenshawGrid, RadialGrid

__all__ = ["test_get_descriptors_of_model",
           "test_get_kullback_leibler",
           "test_get_lagrange_multiplier",
           "test_goodness_of_fit",
           "test_goodness_of_fit_squared",
           "test_input_checks",
           "test_integration_spherical"]


def test_input_checks():
    r"""Test input checks for 'fitting.kl_divergence.mbis_abc'."""
    g = ClenshawGrid(10, 2, 1)
    e = np.array(g.radii * 5.)
    npt.assert_raises(TypeError, KullbackLeiblerFitting, 10., e)
    npt.assert_raises(TypeError, KullbackLeiblerFitting, g, 10.)
    npt.assert_raises(TypeError, KullbackLeiblerFitting, g, e, 5j)
    npt.assert_raises(ValueError, KullbackLeiblerFitting, g, e, -5)
    npt.assert_raises(ValueError, KullbackLeiblerFitting, g, e, 0.)

    # Test that lagrange multiplier gives zero or nan.
    g = RadialGrid(np.arange(0., 10.))
    e = np.exp(-g.radii)
    npt.assert_raises(RuntimeError, KullbackLeiblerFitting, g, e, np.nan)
    e = np.zeros(10)
    npt.assert_raises(RuntimeError, KullbackLeiblerFitting, g, e, 1)

    # Test when Integration Value (inte_val) is None
    g = RadialGrid(np.arange(0., 26, 0.05))
    e = np.exp(-g._radii)
    kl = KullbackLeiblerFitting(g, e, None)
    npt.assert_allclose(kl.inte_val, 2. * 4. * np.pi)


def test_get_lagrange_multiplier():
    r"""Test the lagrange multiplier in KullbackLeiblerFitting."""
    g = RadialGrid(np.arange(0., 26, 0.05))
    e = np.exp(-g._radii)
    kl = KullbackLeiblerFitting(g, e, inte_val=1.)
    npt.assert_allclose(kl.lagrange_multiplier, 2. * 4 * np.pi)


def test_integration_spherical():
    r"""Test integration of model in KullbackLeiblerFitting."""
    g = RadialGrid(np.arange(0., 26, 0.01))
    e = np.exp(-g.radii)
    kl = KullbackLeiblerFitting(g, e, inte_val=1.)
    true_answer = kl.integrate_model_spherically(e)
    npt.assert_allclose(true_answer, 2. * 4 * np.pi)


def test_goodness_of_fit():
    r"""Test goodness of fit."""
    g = RadialGrid(np.arange(0., 10, 0.01))
    e = np.exp(-g.radii)
    kl = KullbackLeiblerFitting(g, e, inte_val=1.)
    model = np.exp(-g.radii**2.)
    true_answer = kl.goodness_of_fit(model)
    npt.assert_allclose(true_answer, 0.3431348, rtol=1e-3)


def test_goodness_of_fit_squared():
    r"""Test goodness of fit squared."""
    g = RadialGrid(np.arange(0., 10, 0.01))
    e = np.exp(-g.radii)
    kl = KullbackLeiblerFitting(g, e, inte_val=1.)
    model = np.exp(-g.radii ** 2.)
    true_answer = kl.goodness_of_fit_grid_squared(model)
    npt.assert_allclose(true_answer, 1.60909, rtol=1e-4)


def test_get_kullback_leibler():
    r"""Test kullback leibler formula."""
    # Test same probabiltiy distribution
    g = RadialGrid(np.arange(0., 26, 0.01))
    e = np.exp(-g.radii**2.)
    kl = KullbackLeiblerFitting(g, e)
    true_answer = kl.get_kullback_leibler(e)
    npt.assert_allclose(true_answer, 0.)

    # Test Different Model with wolfram
    # Integrate e^(-x^2) * log(e^(-x^2) / x) 4 pi r^2 dr from 0 to 25
    fit_model = g.radii
    true_answer = kl.get_kullback_leibler(fit_model)
    npt.assert_allclose(true_answer, -0.672755 * 4 * np.pi, rtol=1e-3)


def test_get_descriptors_of_model():
    r"""Test get descriptors of model."""
    g = RadialGrid(np.arange(0., 10, 0.001))
    e = np.exp(-g.radii)
    kl = KullbackLeiblerFitting(g, e, inte_val=1.)
    model = np.exp(-g.radii**2.)
    true_answer = kl.get_descriptors_of_model(model)
    desired_answer = [5.56833, 0.3431348, 1.60909, 4. * np.pi * 17.360]
    npt.assert_allclose(true_answer, desired_answer, rtol=1e-4)
