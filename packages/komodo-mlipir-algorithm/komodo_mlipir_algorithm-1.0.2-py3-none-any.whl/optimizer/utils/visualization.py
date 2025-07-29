import numpy as np
import matplotlib.pyplot as plt

def plot_convergence(convergence, title):
    plt.plot(convergence)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title(title)
    plt.show()

def plot_2d_landscape(func, bounds, title, num_points=100):
    x = np.linspace(bounds[0], bounds[1], num_points)
    y = np.linspace(bounds[0], bounds[1], num_points)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    
    for i in range(num_points):
        for j in range(num_points):
            Z[i,j] = func([X[i,j], Y[i,j]])
    
    plt.contourf(X, Y, Z, 10)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.title(title)
    plt.show()


def plot_population_distribution(population, title):
    plt.scatter(population[:, 0], population[:, 1])
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.title(title)
    plt.show()