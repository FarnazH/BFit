from fitting.fit.model import *
from fitting.fit.GaussianBasisSet import *
import  matplotlib.pyplot as plt
from scipy.integrate import simps, trapz
import decimal
import numpy as np

d = decimal.Decimal
#Absolute difference= 314245.645194 15667.5795399 [ 329913.2247343]

def update_coefficients_using_decimal_lib(initial_coeffs, constant_exponents, electron_density, grid, masked_value=1e-6):
    #assert np.all(initial_coeffs > 0) == True
    assert len(initial_coeffs) == len(constant_exponents)
    assert len(np.ravel(electron_density)) == len(np.ravel(grid))

    def turn_float_array_into_decimal_array(float_array):
        if float_array.ndim == 2:
            decimal_s = [[decimal.Decimal(x) for x in y] for y in float_array]
            float_array = np.array(decimal_s)
        else:
            decimal_s = [d(x) for x in float_array]
            float_array = np.array(decimal_s)
        return float_array

    def turn_decimal_array_to_float_array(decimal_array):
        if decimal_array.ndim == 2:
            float_array = [[float(x) for x in y] for y in decimal_array]
            decimal_array = np.array(float_array)
        else:
            float_array = [float(x) for x in decimal_array]
            decimal_array = np.array(float_array)
        return decimal_array

    def simple_integration(y_array, x_array):
        integration_value = 0
        for i in range(0, len(y_array) - 1):
            integration_value += y_array[i] * (x_array[i+1] - x_array[i])
        return integration_value

    initial_coeffs = (turn_float_array_into_decimal_array(initial_coeffs))
    constant_exponents = turn_float_array_into_decimal_array(constant_exponents)
    electron_density = turn_float_array_into_decimal_array(electron_density)
    grid = turn_float_array_into_decimal_array(grid)
    grid_squared = turn_float_array_into_decimal_array(grid**2)

    exponential = np.exp(d(-1) * constant_exponents * grid_squared)
    gaussian_density = np.dot(exponential, initial_coeffs)

    mininum_value = min(gaussian_density)
    print(gaussian_density)
    gaussian_density[-1] = min(gaussian_density)
    gaussian_density[-2] = min(gaussian_density)
    gaussian_density[-3] = min(gaussian_density)
    ratio = np.ravel(electron_density) / gaussian_density

    new_coefficients = np.empty(len(initial_coeffs))
    for i in range(0, len(initial_coeffs)):
        factor = initial_coeffs[i] * (constant_exponents[i] / d(np.pi))**(d(1.5))
        integrand = ratio * np.ravel(np.exp(d(-1) *constant_exponents[i] * grid_squared))
        if False:
            factor = float(factor)
            grid = turn_decimal_array_to_float_array(grid)
            integrand = turn_decimal_array_to_float_array(integrand)
            new_coefficients[i] = factor * np.trapz(y=integrand, x=np.ravel(grid))
        else:
            print(factor * simple_integration(integrand, np.ravel(grid)), factor)
            new_coefficients[i] = factor * simple_integration(integrand, np.ravel(grid))
    print(new_coefficients)

    return new_coefficients

def update_coefficients(initial_coeffs, constant_exponents, electron_density, grid, masked_value=1e-6):
    assert np.all(initial_coeffs > 0) == True
    assert len(initial_coeffs) == len(constant_exponents)
    assert len(np.ravel(electron_density)) == len(np.ravel(grid))

    exponential = np.exp(-constant_exponents * np.power(grid, 2.))
    assert exponential.shape[1] == len(constant_exponents)
    assert exponential.shape[0] == len(np.ravel(grid))
    gaussian_density = np.dot(exponential, initial_coeffs)
    assert gaussian_density.shape[0] == len(np.ravel(grid))

    masked_gaussian_density = np.ma.asarray(gaussian_density)
    masked_electron_density = np.ma.asarray(np.ravel(electron_density))
    masked_gaussian_density[masked_gaussian_density <= masked_value] = masked_value

    ratio = masked_electron_density / masked_gaussian_density
    #print(masked_electron_density[200:250], masked_gaussian_density[200:250])
    #print(np.where(masked_gaussian_density < masked_value))
    #print(ratio[len(ratio) - 10:])
    #print(masked_gaussian_density[len(ratio) - 10:])
    #print("max and min", np.max(ratio), np.min(ratio))
    max_val = np.max(ratio)
    min_val = np.min(ratio)
    index_max, index_min = (np.argmax(ratio), np.argmin(ratio))
    #index_max, index_min = (np.where(ratio == max_val), np.where(ratio==min_val))
    #print("index_max", index_max, "index_min", index_min)
    #print("max",ratio[index_max], "=", masked_electron_density[index_max],"/", masked_gaussian_density[index_max])
    #print("min",ratio[index_min], "=", masked_electron_density[index_min],"/", masked_gaussian_density[index_min])

    new_coefficients = np.empty(len(initial_coeffs))
    for i in range(0, len(initial_coeffs)):
        factor = initial_coeffs[i] * (constant_exponents[i] / np.pi)**(1/2) * 2.
        integrand = ratio * np.ravel(np.ma.asarray(np.exp(- constant_exponents[i] * np.power(grid, 2.))))
        new_coefficients[i] = factor * np.trapz(y=integrand, x=np.ravel(grid))
    return new_coefficients

def measure_error_by_integration_of_difference(true_model, approximate_model, grid):
        error = np.trapz(y=np.ravel(grid**2) * (np.absolute(np.ravel(true_model) - np.ravel(approximate_model))), x=np.ravel(grid))
        return error

def iterative_MBIS_method(initial_coeffs, constant_exponents, electron_density, grid, error=1e-5, masked_value=1e-6):
    current_error = 1e10
    old_coefficients = np.copy(initial_coeffs)
    new_coefficients = np.copy(initial_coeffs)

    #while current_error > error * len(initial_coeffs):
    list_of_obj_func = []
    for x in range(0, 100):
        temp = np.copy(new_coefficients)
        new_coefficients = update_coefficients(old_coefficients, constant_exponents, electron_density, grid)
        old_coefficients = np.copy(temp)
        current_error = np.sum(np.abs((old_coefficients - new_coefficients)))
        model = np.dot(np.exp(-constant_exponents * grid**2), new_coefficients)
        print("Currenterror", current_error,  measure_error_by_integration_of_difference(model, np.ravel(electron_density), np.ravel(grid)),"\n")

        exponential = np.exp(-constant_exponents * np.power(grid, 2.))
        assert exponential.shape[1] == len(constant_exponents)
        assert exponential.shape[0] == len(np.ravel(grid))
        gaussian_density = np.dot(exponential, new_coefficients)
        assert gaussian_density.shape[0] == len(np.ravel(grid))

        masked_gaussian_density = np.ma.asarray(gaussian_density)
        masked_electron_density = np.ma.asarray(np.ravel(electron_density))
        masked_gaussian_density[masked_gaussian_density <= masked_value] = 0.0

        log_ratio = np.log(masked_electron_density / masked_gaussian_density)
        list_of_obj_func.append(np.trapz(y=masked_electron_density * log_ratio, x=np.ravel(grid)))

    return new_coefficients, current_error



if __name__ == "__main__":
    ELEMENT_NAME = "be"
    ATOMIC_NUMBER = 4

    file_path = r"C:\Users\Alireza\PycharmProjects\fitting\fitting\data\examples\\" + ELEMENT_NAME + ".slater"
    #Create Grid for the modeling
    from fitting.density.radial_grid import *
    radial_grid = Radial_Grid(ATOMIC_NUMBER)
    NUMBER_OF_CORE_POINTS = 300; NUMBER_OF_DIFFUSED_PTS = 400
    row_grid_points = radial_grid.grid_points(NUMBER_OF_CORE_POINTS, NUMBER_OF_DIFFUSED_PTS, [50, 75, 100])
    column_grid_points = np.reshape(row_grid_points, (len(row_grid_points), 1))

    be =  GaussianTotalBasisSet(ELEMENT_NAME, column_grid_points, file_path)
    fitting_obj = Fitting(be)
    exps = be.UGBS_s_exponents
    coeffs = fitting_obj.optimize_using_nnls(be.create_cofactor_matrix(exps))
    parameters = fitting_obj.optimize_using_slsqp(np.append(coeffs, exps), len(exps))


    coeffs[coeffs == 0] = 1E-6



    coeffs = update_coefficients(coeffs, exps, be.electron_density, be.grid)

    params = np.append(coeffs, exps)
    print(be.integrate_model_using_trapz(be.create_model(params, len(exps))))
    print(be.integrated_total_electron_density)
    while True:
        coeffs = update_coefficients(coeffs, exps, be.electron_density, be.grid)
        #print(coeffs)
        params = np.append(coeffs, exps)

        mod = be.create_model(params, len(exps))

        print(be.integrate_model_using_trapz(mod), be.measure_error_by_difference_of_integration(be.electron_density, mod))






