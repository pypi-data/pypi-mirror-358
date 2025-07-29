import numpy as np
from numba import njit


@njit
def fz_and_chamfer(r, *args):
    s = 0.0
    for a in args:
        s += max(r + a, 0) ** 2
    return s**0.5 - r


@njit
def fz_or_chamfer(r, *args):
    s = 0.0
    for a in args:
        s += max(r - a, 0) ** 2
    return r - s**0.5


@njit
def grad(f, p, h=0.001):
    x, y, z, par = p
    f0 = f(p)
    return (
        np.array([f((x + h, y, z, par)), f((x, y + h, z, par)), f((x, y, z + h, par))])
        - f0
    ) / h
