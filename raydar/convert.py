"""Simple converter of XYZ (ETRS89 / UTM zone 32N) points into WGS84.
"""
import os
import glob
import argparse
import time

import pandas as pd
import numpy as np
import pyproj
from pyproj import CRS, Transformer
from tqdm import tqdm, tqdm_notebook
from .utils import Announce


def map_to_wgs84(src, dest, verbose=True):
    """Transforms a xyz point cloud to lat, lon
    
    Args:
        src (str): path to xyz file
        dest (str): destination output file
        verbose (bool): Default True. Set False for no status output.
    """

    crs_4326 = CRS.from_epsg(4326) # WGS84
    crs_25832 = CRS.from_epsg(25832) # ETRS89 / UTM zone 32N

    to_wgs_84_transformer = Transformer.from_crs(crs_25832, crs_4326)

    with Announce("Reading input file...", "Done!", disable=not verbose):
        df_file = pd.read_csv(src, header=None, names=["x", "y", "z"])

    with Announce("Projecting points to WGS84...", "Done!", disable=not verbose):

        lat_arr, lon_arr = list(), list()
        for _, row in tqdm(df_file.iterrows(), total=len(df_file), disable=not verbose):
            res = to_wgs_84_transformer.transform(row["x"], row["y"])
            lat_arr.append(res[0]), lon_arr.append(res[1])

        df_file["lat"] = lat_arr
        df_file["lon"] = lon_arr

        # alternatively
        #df_file[["lat", "lon"]] = df_file.apply(lambda row: pd.Series(to_wgs_84_transformer.transform(row["x"], row["y"])))

    with Announce("Writing output to file ...", "Done!", disable=not verbose):
        df_file.to_csv(dest, index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="LIDAR point cloud (ETRS89 / UTM zone 32N) to WGS84 converter")
    parser.add_argument("src", help="input xyz file", type=str)
    parser.add_argument("dest", help="destination path", type=str)
    parser.add_argument("--verbose", help="verbosity", action="store_true")
    args = parser.parse_args()
    src = args.src
    dest = args.dest
    verb = args.verbose
    map_to_wgs84(src, dest, verbose=verb)