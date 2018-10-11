import numpy as np

from constants import OUT
from utils.bezier import interpolate
from utils.space_ops import rotation_matrix
from utils.space_ops import get_norm
from scipy.spatial import Delaunay

STRAIGHT_PATH_THRESHOLD = 0.01


def straight_path(start_points, end_points, alpha):
    """
    Same function as interpolate, but renamed to reflect
    intent of being used to determine how a set of points move
    to another set.  For instance, it should be a specific case
    of path_along_arc
    """
    return interpolate(start_points, end_points, alpha)


def path_along_arc(arc_angle, axis=OUT):
    """
    If vect is vector from start to end, [vect[:,1], -vect[:,0]] is
    perpendicular to vect in the left direction.
    """
    if abs(arc_angle) < STRAIGHT_PATH_THRESHOLD:
        return straight_path
    if get_norm(axis) == 0:
        axis = OUT
    unit_axis = axis / get_norm(axis)

    def path(start_points, end_points, alpha):
        vects = end_points - start_points
        centers = start_points + 0.5 * vects
        if arc_angle != np.pi:
            centers += np.cross(unit_axis, vects / 2.0) / np.tan(arc_angle / 2)
        rot_matrix = rotation_matrix(alpha * arc_angle, unit_axis)
        return centers + np.dot(start_points - centers, rot_matrix.T)
    return path


def clockwise_path():
    return path_along_arc(-np.pi)


def counterclockwise_path():
    return path_along_arc(np.pi)


"""
Shamelessly copied from https://stackoverflow.com/questions/23073170/calculate-bounding-polygon-of-alpha-shape-from-the-delaunay-triangulation
"""
def alpha_shape(points, alpha, only_outer=True):
    """
    Compute the alpha shape (concave hull) of a set of points.
    :param points: np.array of shape (n,2) points.
    :param alpha: alpha value.
    :param only_outer: boolean value to specify if we keep only the outer
    border or also inner edges.
    :return: set of (i,j) pairs representing edges of the alpha-shape. (i,j)
    are the indices in the points array.
    """
    assert points.shape[0] > 3, "Need at least four points"

    def add_edge(edges, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            assert (j, i) in edges, "Can't go twice over same directed edge right?"
            if only_outer:
                # if both neighboring triangles are in shape, it's not a boundary edge
                edges.remove((j, i))
            return
        edges.add((i, j))

    tri = Delaunay(points)
    edges = set()
    # Loop over triangles:
    # ia, ib, ic = indices of corner points of the triangle
    for ia, ib, ic in tri.vertices:
        pa = points[ia]
        pb = points[ib]
        pc = points[ic]
        # Computing radius of triangle circumcircle
        # www.mathalino.com/reviewer/derivation-of-formulas/derivation-of-formula-for-radius-of-circumcircle
        a = np.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
        b = np.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
        c = np.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
        s = (a + b + c) / 2.0
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        circum_r = a * b * c / (4.0 * area)
        if circum_r < alpha:
            add_edge(edges, ia, ib)
            add_edge(edges, ib, ic)
            add_edge(edges, ic, ia)
    return edges
