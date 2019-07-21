"""Utilities collection.
"""

from datetime import datetime

import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u


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
