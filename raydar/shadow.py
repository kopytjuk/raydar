from datetime import datetime
import math

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely as sh
import shapely.geometry as shg
import shapely.ops as sho
import numpy as np
from pyproj import CRS, Transformer

from .utils import get_sun_state, project_sunray, Announce, R_z


# helper functions
crs_4326 = CRS.from_epsg(4326)  # WGS84
crs_25832 = CRS.from_epsg(25832)  # ETRS89 / UTM zone 32N
to_wgs_84_transformer = Transformer.from_crs(crs_25832, crs_4326)
to_utm_transformer = Transformer.from_crs(crs_4326, crs_25832)


class Raydar(object):

    def __init__(self, xyz_path, shadow_resolution=10):
        self._shadow_resolution = shadow_resolution
        with Announce("Reading points...", end="Done!"):
            df = pd.read_csv(xyz_path)
            df = gpd.GeoDataFrame(df)

            # creating a geometry column
            geometry = [sh.geometry.Point(xy)
                        for xy in zip(df['lat'], df['lon'])]

            # Coordinate reference system : WGS84
            crs = {'init': 'epsg:4326'}

            self.pts = gpd.GeoDataFrame(
                df[["x", "y", "z"]], crs=crs, geometry=geometry)

    def _get_points_around_query(self, lat_q, lon_q, R):

        query_point_xy = shg.Point(to_utm_transformer.transform(lat_q, lon_q))
        query_region_xy = query_point_xy.buffer(R, resolution=16)
        query_region_wgs84 = sho.transform(
            to_wgs_84_transformer.transform, query_region_xy)
        
        # TODO: maybe we can make that work faster ...
        gdf = self.pts.copy()
        res = gdf[gdf.intersects(query_region_wgs84)]
        return res

    def _get_internal_calculation(self, lat_q, lon_q, t_q, R):

        gdf_query = self._get_points_around_query(lat_q, lon_q, R)
        
        # get nearest point to the query point
        query_nearest_point = gdf_query.loc[gdf_query.distance(
            sh.geometry.Point(lat_q, lon_q)).idxmin()]

        # This point is now the origin of the projected axis,
        # so we have to remove the offset of other points
        gdf_query["x_proj"] = gdf_query["x"] - query_nearest_point["x"]
        gdf_query["y_proj"] = gdf_query["y"] - query_nearest_point["y"]
        gdf_query["z_proj"] = gdf_query["z"] - query_nearest_point["z"]

        query_time = t_q  # datetime(2019, 7, 21, 8, 0, 0)

        zen, azimut = get_sun_state(lat_q, lon_q, query_time)

        # project the origin axes to the axes of the sunray
        P = gdf_query[["x_proj", "y_proj", "z_proj"]].values
        P_ray = project_sunray(P, zen, azimut)

        return P_ray, gdf_query, P, zen, azimut

    def debug_plot(self, lat_q, lon_q, t_q, R):

        P_ray, gdf_query, P, zen, azimut = self._get_internal_calculation(
            lat_q, lon_q, t_q, R)

        az_radian = azimut/360 * 2 * math.pi
        
        # we rotate towards sun
        P_towards_sun = P @ R_z(-az_radian).T

        # remove all points with negative x, since they are behind the query point
        P_ray = P_ray[P_ray[:, 0] >= 0]

        # remove all points with z>0.15m
        P_ray = P_ray[P_ray[:, 2] >= 0.15]

        shadow_res_half = self._shadow_resolution//2

        fig, ax = plt.subplots(ncols=2, figsize=(15, 7))

        # now we only plot, y and z axis
        ax[0].scatter(P_ray[:, 1], P_ray[:, 2], )
        ax[0].scatter(0, 0, s=200, marker="+")
        ax[0].axvline(-shadow_res_half, color="y")
        ax[0].axvline(shadow_res_half, color="y")
        ax[0].axhline(0, color="k")
        ax[0].set_xlim([-R, R])

        query_point_xy = shg.Point(to_utm_transformer.transform(lat_q, lon_q))
        zen, azimuth = get_sun_state(lat_q, lon_q, t_q)

        ax[1].scatter(gdf_query["x"], gdf_query["y"], c=gdf_query["z"],
                      s=10, cmap="inferno", label="LIDAR points")
        #plt.colorbar()
        ax[1].scatter([query_point_xy.x], [query_point_xy.y],
                      marker='+', s=10000, color="red")
        dx = 100*np.sin(azimuth*2*np.pi/360)
        dy = 100*np.cos(azimuth*2*np.pi/360)
        ax[1].arrow(query_point_xy.x+dx, query_point_xy.y+dy, -dx, -dy, width=3,
                    head_width=5, length_includes_head=True, color="y", label="sun ray")
        ax[1].arrow(query_point_xy.x, query_point_xy.y, -dy, +dx,
                    head_width=5, length_includes_head=False, color="k")
        ax[1].text(query_point_xy.x-dy, query_point_xy.y +
                   dx+10, "y-axis", fontsize=12)
        ax[1].legend()

        #ax[1].title(t_q)
        fig.suptitle(t_q)

        return fig

    def is_shadow(self, lat_q, lon_q, t_q, R):

        P_ray, _, _, _, _ = self._get_internal_calculation(
            lat_q, lon_q, t_q, R)

        # remove all points with negative x,
        # since they are behind the query point
        P_ray = P_ray[P_ray[:, 0] >= 0]

        # remove all points with z>0.15m
        P_ray = P_ray[P_ray[:, 2] >= 0.15]

        P_ray_y = P_ray[:, 1]

        shadow_res_half = self._shadow_resolution//2

        # if there are points on the y-axis within [-res, +res] there is shadow
        if ((P_ray_y > -shadow_res_half) & (P_ray_y < shadow_res_half)).sum() > 0:
            return True
        else:
            return False
