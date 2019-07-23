"""Utilities collection.
"""

from datetime import datetime
import math
import time

import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u

import numpy as np


class Announce(object):
    def __init__(self, action, end, disable=False):
        self.action = action
        self.end = end
        self.disable = disable

    def __enter__(self):
        if not self.disable:
            print(self.action)
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        duration = time.time() - self.start_time
        if not self.disable:
            print(self.end, "(%.2fs)" % duration)


def R_x(alpha):
    return np.asarray([[1, 0, 0],
                       [0, np.cos(alpha), -np.sin(alpha)],
                       [0, np.sin(alpha), np.cos(alpha)]])


def R_y(alpha):
    return np.asarray([[np.cos(alpha), 0, np.sin(alpha)],
                       [0, 1, 0],
                       [-np.sin(alpha), 0, np.cos(alpha)]])


def R_z(alpha):
    return np.asarray([[np.cos(alpha), -np.sin(alpha), 0],
                       [np.sin(alpha), np.cos(alpha), 0],
                       [0, 0, 1]])


def get_sun_state(lat: float, lon: float, t: datetime):
    """Given a time and location get the sun position relative to this location.

    Args:
        lat (float): latitude
        lon (float): longitude
        t (datetime): query time

    Returns:
        tuple: zenith and azimuth angles
    """

    loc = coord.EarthLocation(lon=lon * u.deg,
                              lat=lat * u.deg)

    query_time_string = t.strftime("%Y-%m-%dT%H:%M:%S.%f")
    t = Time(query_time_string, format="isot", scale="utc")

    altaz = coord.AltAz(location=loc, obstime=t)
    sun = coord.get_sun(t)

    transformer = sun.transform_to(altaz)
    theta_z = transformer.zen
    theta_A = transformer.az

    return theta_z.degree, theta_A.degree


def project_sunray(P, zenith, azimut):

    az_radian = azimut/360 * 2 * math.pi
    zen_radian = zenith/360 * 2 * math.pi
    elev_radian = math.pi/2 - zen_radian

    # projected points on the sunray
    R = P @ R_z(-az_radian).T @ R_y(elev_radian).T
    return R
