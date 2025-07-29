import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs


import numpy as np
import matplotlib.pyplot as plt
import glob
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.crs as ccrs
import matplotlib.patches as patches
# from osgeo import gdal, osr
# import pyproj

from scipy.interpolate import griddata
# from src.lulc_colormap import get_lulc_colormap

from pyhelpme import coast

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from matplotlib import colors


def get_lulc_colormap():
    lulc_classes = {
        "Evergreen Needleleaf Forest": "#05450a",
        "Evergreen Broadleaf Forest": "#086a10",
        "Deciduous Needleleaf Forest": "#54a708",
        "Deciduous Broadleaf Forest": "#78d203",
        "Mixed Forest": "#009900",
        "Closed Shrublands": "#c6b044",
        "Open Shrublands": "#dcd159",
        "Woody Savannas": "#dade48",
        "Savannas": "#fbff13",
        "Grasslands": "#b6ff05",
        "Permanent wetlands": "#27ff87",
        "Croplands": "#006400",
        "Urban and Built-Up": "#FF0000",
        "cropland/natural vegetation mosaic": "#ADFF2F",
        "Snow and Ice": "#69fff8",
        "Barren or Sparsely Vegetated": "#f9ffa4",
        "Water": "#1c0dff",
    }

    lulc_colormap = ListedColormap(list(lulc_classes.values()))
    return lulc_colormap, lulc_classes

plt.rcParams.update({"font.size": 18, "font.weight": "bold"})


def get_bb(file_name):
    return np.array(
        (
            file_name["XLONG_M"].min().values,
            file_name["XLONG_M"].max().values,
            file_name["XLAT_M"].min().values,
            file_name["XLAT_M"].max().values,
        )
    )


def draw_box(bb):
        return patches.Rectangle(
            (bb[0], bb[2]),
            bb[1] - bb[0],
            bb[3] - bb[2],
            linewidth=2,
            edgecolor="m",
            facecolor="none",
            alpha=1,
        )



def plot_lulc_geogrid(geog_file, label='LULC 2001', legend=False, axes=None):
    pre_geog_file = xr.open_dataset(geog_file, engine="netcdf4")

    wrf_longitudes_pre = pre_geog_file["XLONG_M"].squeeze().values
    wrf_latitudes_pre = pre_geog_file["XLAT_M"].squeeze().values
    wrf_lulc_pre = pre_geog_file["LU_INDEX"].squeeze().squeeze().values

    lulc_cmap, lulc_classes = get_lulc_colormap()


    img = axes.pcolormesh(
        wrf_longitudes_pre,
        wrf_latitudes_pre,
        wrf_lulc_pre,
        vmin=1,
        vmax=18,
        cmap=lulc_cmap,
        shading="auto",
    )
    coast.plot_coast(axes)

    if legend:
     cbar = plt.colorbar(img, ticks=np.arange(1, 18, 1) + 0.5, shrink=0.8)
     cbar.ax.set_yticklabels(list(lulc_classes.keys()), fontsize=12)  # horizontal colorbar
     axes.set_extent(get_bb(pre_geog_file))

    urban_count = f'{np.where(wrf_lulc_pre==13)[0].shape[0]} ({np.round(np.where(wrf_lulc_pre==13)[0].shape[0]*100/(wrf_lulc_pre.ravel().shape[0]), 2)} %)'

    axes.set_title(f'{label} | {urban_count}')
    plot_domain(axes)
    plt.tight_layout()
    #plt.savefig('.'.join(geog_file.split("/")[-1].split(".")[:2])+'_LULC_pre_map.jpeg', dpi=300)
    return axes

def plot_domain(ax):
 geog_files = sorted(glob.glob(f'/nas/rstor/akumar/USA/PhD/2024_Hurricanes/{hurr}/{hurr}_def/WPS_dumy/geo_em.d*.nc'))
 d1bb = get_bb(xr.open_dataset(geog_files[0]))
 d2bb = get_bb(xr.open_dataset(geog_files[1]))
 d3bb = get_bb(xr.open_dataset(geog_files[2]))
 [ax.add_patch(draw_box(dbb)) for dbb in (d1bb, d2bb, d3bb)]
 return None


# plt.rcParams.update({"font.size": 14, "font.weight": "bold", "savefig.dpi": 300})

# hurr = 'Milton'

# domain = 'd03'
# geog_2001 =  f"/nas/rstor/akumar/USA/PhD/2024_Hurricanes/{hurr}/{hurr}_def/WPS_dumy/geo_em.d01.nc_2001"
# geog_2020 =  f"/nas/rstor/akumar/USA/PhD/2024_Hurricanes/{hurr}/{hurr}_def/WPS_dumy/geo_em.d01.nc_2023"

# geog_2050 =  f"/nas/rstor/akumar/USA/PhD/2024_Hurricanes/{hurr}/{hurr}_def/WPS_dumy/geo_em.d03.nc_2001"
# geog_2100 =  f"/nas/rstor/akumar/USA/PhD/2024_Hurricanes/{hurr}/{hurr}_def/WPS_dumy/geo_em.d03.nc_2023"

# fig = plt.figure(figsize=(10.5, 9))

# # Create subplots with specific projection
# axes1 = plt.subplot(2, 2, 1, projection=ccrs.PlateCarree())
# axes2 = plt.subplot(2, 2, 2, projection=ccrs.PlateCarree())
# axes3 = plt.subplot(2, 2, 3, projection=ccrs.PlateCarree())
# axes4 = plt.subplot(2, 2, 4, projection=ccrs.PlateCarree())

# plot_lulc_geogrid(geog_2001, label=f"(a) {geog_2001.split('/')[-1].split('.')[1]} LULC 2001", axes=axes1)
# plot_lulc_geogrid(geog_2020, label=f"(a) {geog_2020.split('/')[-1].split('.')[1]} LULC 2024", axes=axes2)
# plot_lulc_geogrid(geog_2050, label=f"(a) {geog_2050.split('/')[-1].split('.')[1]} LULC 2001", axes=axes3)
# plot_lulc_geogrid(geog_2100, label=f"(a) {geog_2100.split('/')[-1].split('.')[1]} LULC 2024", axes=axes4)

# plt.subplots_adjust(hspace=0.25)
# # plt.savefig(f'../figures_draft01/fig01_{domain}_cropland.jpeg', dpi=400)
# plt.show()

