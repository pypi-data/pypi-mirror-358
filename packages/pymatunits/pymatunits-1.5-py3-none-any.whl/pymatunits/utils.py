"""
Place for independent helper functions, e.g. for tolerancing and
geometric manipulation as part of `pymatunits`

Copyright (C) 2023 Adam Cox

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""
from math import cos, sin, sqrt
from numpy import array, mean, ndarray, radians


def percent_diff(val1, val2, signed=False):
    """
    Percent difference between two values. Absolute difference between
    the two values divided by their average and multiplied by 100.

    Parameters
    ----------
    val1 : float
    val2 : float
    signed : bool, optional

    Returns
    -------
    percent_diff : float
    """
    if val1 == val2:
        return 0.0
    else:
        diff = val1 - val2
        if not signed:
            diff = abs(diff)
        return diff / mean([val1, val2]) * 100


def percent_error(reference, value):
    """
    Percent error from reference value

    Parameters
    ----------
    reference : float
    value : float
    Returns
    -------
    percent_error : float
    """
    if reference == value:
        return 0.0
    else:
        return (value - reference) / reference * 100


def point_distance(p1, p2):
    """
    Euclidean distance between two points in cartesian coordinate frame

    Parameters
    ----------
    p1 : iterable[float]
        Point in two or three-space. Either (x, y) or (x, y, z).
    p2 : iterable[float]
        Point in two or three-space. Either (x, y) or (x, y, z).

    Raises
    ------
    ValueError
        When vectors are of different lengths

    Returns
    -------
    distance : float
    """
    if len(p1) != len(p2):
        raise ValueError('Dimensionality mismatch')
    return sqrt(sum((p2[_i] - p1[_i]) ** 2 for _i in range(len(p1))))


def rotate_vector(vector, angles, reverse=False):
    """
    Rotate vector about x, y, and z

    Parameters
    ----------
    vector : Iterable[float]
        Original (x, y, z) iterable describing vector to be rotated. Can
        also be in numpy array format already.
    angles : Iterable[float]
        Length three iterable containing alpha, beta, and gamma, or the
        angles in degrees about x, y, and z to rotate.
    reverse : bool, optional
        Flag to reverse rotation about z, y, then x. Default value is
        False.

    Returns
    -------
    vector : tuple
         Rotated (x, y, z) vector.
    """
    if not isinstance(vector, ndarray):
        x, y, z = vector
        vector = array([[x], [y], [z]])
    if not reverse:
        alpha, beta, gamma = [radians(_i) for _i in angles]
    else:
        alpha, beta, gamma = [-radians(_i) for _i in angles]
    r_x = array([[1, 0, 0],
                 [0, cos(alpha), -sin(alpha)],
                 [0, sin(alpha), cos(alpha)]])
    r_y = array([[cos(beta), 0, sin(beta)],
                 [0, 1, 0],
                 [-sin(beta), 0, cos(beta)]])
    r_z = array([[cos(gamma), -sin(gamma), 0],
                 [sin(gamma), cos(gamma), 0],
                 [0, 0, 1]])
    if not reverse:
        vector = r_z.dot(r_y.dot(r_x.dot(vector)))
    else:
        vector = r_x.dot(r_y.dot(r_z.dot(vector)))
    vector = tuple([float(_) for _ in vector])
    return vector
