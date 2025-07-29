import numpy as np

# Функция Растригина для n переменных
def rastrigin(x):
    A = 10
    x = np.array(x)
    return A * len(x) + np.sum(x ** 2 - A * np.cos(2 * np.pi * x))

# Функция Бута
def booth(x):
    return (x[0] + 2 * x[1] - 7)**2 + (2 * x[0] + x[1] - 5)**2

# Функция Розенброка для n переменных
def rosenbrock(x):
    x = np.array(x)
    return np.sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
