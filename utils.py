"""Utilities collection.
"""

from datetime import datetime
import math

import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u

import numpy as np


def R_x(alpha):
    return np.asarray([[1, 0, 0],[0, np.cos(alpha), -np.sin(alpha)],[0, np.sin(alpha), np.cos(alpha)]])


def R_y(alpha):
    return np.asarray([[np.cos(alpha), 0, np.sin(alpha)],[0, 1, 0],[-np.sin(alpha), 0, np.cos(alpha)]])


def R_z(alpha):
    return np.asarray([[np.cos(alpha), -np.sin(alpha), 0], [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])


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

    print(az_radian, zen_radian)

    # projected points on the sunray
    R = P @ R_z(-az_radian).T @ R_y(elev_radian).T
    return R
