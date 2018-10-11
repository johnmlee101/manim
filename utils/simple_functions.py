import numpy as np
import operator as op
import inspect
from functools import reduce


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


CHOOSE_CACHE = {}


def choose_using_cache(n, r):
    if n not in CHOOSE_CACHE:
        CHOOSE_CACHE[n] = {}
    if r not in CHOOSE_CACHE[n]:
        CHOOSE_CACHE[n][r] = choose(n, r)
    return CHOOSE_CACHE[n][r]


def choose(n, r):
    if n < r:
        return 0
    if r == 0:
        return 1
    denom = reduce(op.mul, range(1, r + 1), 1)
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    return numer // denom


def get_num_args(function):
    return len(inspect.signature(function).parameters)

# Just to have a less heavyweight name for this extremely common operation
#
# We may wish to have more fine-grained control over division by zero behavior
# in the future (separate specifiable values for 0/0 and x/0 with x != 0),
# but for now, we just allow the option to handle indeterminate 0/0.


def clip_in_place(array, min_val=None, max_val=None):
    if max_val is not None:
        array[array > max_val] = max_val
    if min_val is not None:
        array[array < min_val] = min_val
    return array


def fdiv(a, b, zero_over_zero_value=None):
    if zero_over_zero_value is not None:
        out = np.full_like(a, zero_over_zero_value)
        where = np.logical_or(a != 0, b != 0)
    else:
        out = None
        where = True

    return np.true_divide(a, b, out=out, where=where)


def update_without_overwrite(d1, d2):
    for key in d2:
        if key not in d1:
            d1[key] = d2[key]
    return d1


def circular_binary_structure(radius):
    two_d_coordinates = np.indices((2 * radius + 1, 2 * radius + 1)) \
                          .swapaxes(0, 2) \
                          .swapaxes(0, 1)
    two_d_coordinates_origin = two_d_coordinates[radius, radius]
    circular_structure = np.zeros((2 * radius + 1, 2 * radius + 1))
    circular_structure[np.where(
        np.linalg.norm(
            two_d_coordinates - two_d_coordinates_origin, axis=2) <= radius
    )] = 1
    return circular_structure
