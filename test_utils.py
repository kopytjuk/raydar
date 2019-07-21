import unittest
from datetime import datetime
import math

from utils import get_sun_state


def test_sun_state():

    query_time = datetime(2019, 7, 21, 9, 0, 0)
    lat_q, lon_q = 49.1426929, 9.210879

    zen, az = get_sun_state(lat_q, lon_q, query_time)

    assert zen < 80
    assert az < 180
