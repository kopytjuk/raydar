import unittest
from datetime import datetime

from utils import get_sun_state, project_sunray
import numpy as np


def test_sun_state():

    query_time = datetime(2019, 7, 21, 9, 0, 0)
    lat_q, lon_q = 49.1426929, 9.210879

    zen, az = get_sun_state(lat_q, lon_q, query_time)

    assert zen < 80
    assert az < 180


class TestProjections(unittest.TestCase):

    def test_project_sunray_1(self):
        azimut = 90
        zenith = 90 - np.arctan(0.5/1)*360/(2*np.pi)

        xp, yp, zp = 0, 1, 0.5
        P = np.asarray([[xp, yp, zp], [xp, yp, zp]])
        R = project_sunray(P, zenith, azimut)

        # y & z components should disappear, x should > 1
        assert R[0, 0] >= 1.0  # x
        self.assertAlmostEqual(R[0, 1], 0.0)  # x
        self.assertAlmostEqual(R[0, 2], 0.0)  # y

    def test_project_sunray_2(self):
        azimut = 45
        zenith = 90 - np.arctan(1/np.sqrt(2))*360/(2*np.pi)

        xp, yp, zp = 1, 1, 1
        P = np.asarray([[xp, yp, zp], [xp, yp, zp]])
        R = project_sunray(P, zenith, azimut)

        # y & z components should disappear, x should > 1
        assert R[0, 0] >= 1.0  # x
        self.assertAlmostEqual(R[0, 1], 0.0)  # x
        self.assertAlmostEqual(R[0, 2], 0.0)  # y
