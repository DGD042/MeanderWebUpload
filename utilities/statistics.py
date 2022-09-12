# -*- coding: utf-8 -*-
#______________________________________________________________________________
#______________________________________________________________________________
#
#                       Coded by Daniel Gonzalez-Duque
#                           Last revised 30/04/2019
#______________________________________________________________________________
#______________________________________________________________________________

"""
______________________________________________________________________________

 DESCRIPTION:
   This script have all the functions related to the Global Sensibility
   Analysis (GPA).
______________________________________________________________________________
"""
# -----------
# Libraries
# -----------
# Data Management
import numpy as np
# Statistics
from scipy.interpolate import interp1d
from scipy.interpolate import UnivariateSpline
from scipy.signal import cspline1d, cspline1d_eval
from statsmodels.distributions.empirical_distribution import ECDF
from sklearn.metrics import DistanceMetric


# -----------
# Functions 
# -----------
# Statistics and probability
def empirical_inverse_cdf(data):
    """
    DESCRIPTION:
         This code returns the inverse CDF mapping from an 
         empirical distribution.
    ____________________________________________________________
    INPUT:
        :param data: A ndarray, Data.
    ____________________________________________________________
    OUTPUT:
        :return datappf: An Interp1d function with the inverse
                         cdf (ppf) mapping.
    """
    # Empirical CDF
    ecdf = ECDF(data)
    x = ecdf.x
    y = ecdf.y
    # ----------------------------
    # Remove Infinity Values
    # ----------------------------
    i_infity = (np.isinf(x) | np.isinf(y))
    x = x[~i_infity]
    y = y[~i_infity]
    # ----------------------------
    # Fit Values
    # ----------------------------
    data_ppf = interp1d(y, x, fill_value='extrapolate')
    return data_ppf, x, y

def get_reach_distances(x_coord):
    """
    Description:
    ------------

        This function calculates the distance from the starting point
        the to the end points.

    ________________________________________________________________

    Args:
    ------------
    :param x_coord: numpy.ndarray,
        [x, y]coordinates.
    :type x_coord: numpy.ndarray
    :return: numpy.ndarray,
        Distance from the start point to the end point.
    :rtype: numpy.ndarray
    """
    dist = DistanceMetric.get_metric('euclidean')
    d = dist.pairwise(x_coord)
    d2 = [0]
    for i_d in range(1, d.shape[0]):
        d2.append(d[i_d - 1, i_d] + d2[-1])
    s = np.array(d2)
    return s

def fit_splines(x, y, smooth=0, cs_smooth=0.001):
    """
    Description:
    ------------

        This function fits a spline and smooths out the spline
        created using cs_spline.

    ________________________________________________________________

    Args:
    ------------
    :param x: numpy.ndarray,
        x points.
    :type x: numpy.ndarray
    :param y: numpy.ndarray,
        y points.
    :type y: numpy.ndarray
    :param smooth: float,
        Smoothing factor for the UnivariateSpline
    :type smooth: float
    :param cs_smooth: float,
        Smoothing factor for the cspline1d.
    :type cs_smooth: float
    :return: (numpy.ndarray, numpy.ndarray,
        scipy.interpolate.UnivariateSpline)
        - x_poly (numpy.ndarray) - X spline values.
        - y_poly (numpy.ndarray) - Y spline values.
        - y_spl (scipy.interpolate.UnivariateSpline) - Spline function.
    :rtype: (numpy.ndarray, numpy.ndarray,
        scipy.interpolate.UnivariateSpline)
    """
    # ------------------
    # Fit the splines
    # ------------------
    # Select the number of points
    # x_dif_min = 10**np.median(np.log10(np.diff(x)))
    # x_poly = np.arange(x[0], x[-1] + x_dif_min, x_dif_min)
    # if len(x_poly) <= 1000:
    #     x_poly = np.linspace(x[0], x[-1], 2000)
    #     x_dif_min = np.min(np.diff(x_poly))

    x_poly = np.linspace(x[0], x[-1], len(x)*100)

    # ---------------------------------------
    # Combination of Univariate and Cspline
    # ---------------------------------------
    # Create Univariate Splines
    y_spl = UnivariateSpline(x, y, k=3, s=0)
    # y_spl = UnivariateSpline(x, y, s=0, k=1, ext=3)
    # y_spl = CubicSpline(x, y, extrapolate=False)

    y_poly = y_spl(x_poly)

    # Verify begining and end points
    y_poly[0] = y[0]
    y_poly[-1] = y[-1]
    # ----------------------------
    # Further Smooth the Splines
    # ----------------------------
    if cs_smooth is not None:
        if len(x) >= 10:
            # Create cspline
            cy = cspline1d(y_poly, (len(y_poly)*cs_smooth))
            y_poly = cspline1d_eval(
                cy, x_poly, dx=(x_poly[1]-x_poly[0]))
        else:
            cy = cspline1d(y_poly, 0)
            y_poly = cspline1d_eval(
                cy, x_poly, dx=(x_poly[1]-x_poly[0]))

    # Verify beginning and end points
    y_poly[0] = y[0]
    y_poly[-1] = y[-1]

    y_spl = UnivariateSpline(x_poly, y_poly, s=0, k=3, ext=3)
    x_poly = np.linspace(x_poly[0], x_poly[-1], len(x)*10)
    y_poly = y_spl(x_poly)
    return x_poly, y_poly, y_spl

