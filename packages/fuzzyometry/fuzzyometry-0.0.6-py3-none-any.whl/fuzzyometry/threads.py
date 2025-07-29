import numpy as np
from numba import njit


@njit
def fz_thread_profile(pnt, a=1.0):
    y = pnt[1]
    if abs(y) > 2 * a:
        return y
    x = pnt[0] * 2 * np.pi
    sg = np.sign(np.sin(x))
    snglr = 2**-20 - 2**-19 * sg
    p = a / (-np.sin(x) / 2 + snglr)
    q = y / (np.sin(x) + snglr) - 1.0
    return a * (-p - sg * np.sqrt(max(0, p**2 - 4 * q)))


@njit
def fz_thread(pnt, radius, n=1, profile_depth=1.0, a=1.0):
    x, y, z = pnt
    ang = -np.atan2(y, x)
    r = (x**2 + y**2) ** 0.5
    r_arg = (r - radius) / profile_depth
    z_arg = z + n * ang / 2 / np.pi
    return profile_depth * fz_thread_profile((z_arg, r_arg), a)
