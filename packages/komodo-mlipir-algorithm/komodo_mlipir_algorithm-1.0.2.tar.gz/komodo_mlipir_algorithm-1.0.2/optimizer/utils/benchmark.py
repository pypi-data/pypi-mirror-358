import numpy as np

def sphere_function(x):
    return sum(xi**2 for xi in x)

def rosenbrock_function(x):
    return sum(100 * (xi**2 - yi**2) + (1 - xi)**2 for xi, yi in zip(x[0:-1], x[1:]))

def rastrigin_function(x):
    return 10 * len(x) + sum(xi**2 - 10 * np.cos(2 * np.pi * xi) for xi in x)

def ackley_function(x):
    n = len(x)
    a, b, c = 20, 0.2, 2 * np.pi
    sum1 = np.sum(x**2)
    sum2 = np.sum(np.cos(c*x))
    return -a * np.exp(-b * np.sqrt(sum1/n)) - np.exp(sum2/n) + a + np.exp(1)

def easom_function(x):
    if len(x) != 2:
        raise ValueError("Easom function hanya untuk 2 dimensi")
    return -np.cos(x[0]) * np.cos(x[1]) * np.exp(-(x[0]-np.pi)**2 - (x[1]-np.pi)**2)

def griewank_function(x):
    sum_part = np.sum(x**2) / 4000
    prod_part = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x)+1))))
    return sum_part - prod_part + 1

def schwefel_function(x):
    n = len(x)
    return 418.9829*n - np.sum(x * np.sin(np.sqrt(np.abs(x))))


def get_benchmark_function(name):
    if name == "sphere":
        return sphere_function
    elif name == "rosenbrock":
        return rosenbrock_function
    elif name == "rastrigin":
        return rastrigin_function
    elif name == "ackley":
        return ackley_function
    elif name == "easom":
        return easom_function
    elif name == "griewank":
        return griewank_function
    elif name == "schwefel":
        return schwefel_function
    else:
        raise ValueError(f"Unknown benchmark function: {name}")