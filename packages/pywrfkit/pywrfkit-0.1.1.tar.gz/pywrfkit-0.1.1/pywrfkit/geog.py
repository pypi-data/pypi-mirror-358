import numpy as np
import xarray as xr
import copy
import numpy as np

from osgeo import gdal, osr
import pyproj
from scipy.interpolate import interp2d

from scipy.interpolate import griddata




############# DON'T EDIT BELOW THIS LINE, UNLESS YOU ARE ############
#################### VERY SURE ABOUT YOUR EDITS #####################
#####################################################################

def update_geog(geog_file, modis_lulc_file, modis_ndvi_file, new_filename):
    '''
    import glob

    geog_files = sorted(glob.glob("/nas/rstor/akumar/USA/PhD/2024_Hurricanes/Helene/Helene_def/WPS_dumy/geo_em.d0*.nc"))
    geog_files = sorted(glob.glob("/nas/rstor/akumar/USA/PhD/2024_Hurricanes/Milton/Milton_def/WPS_dumy/geo_em.d0*.nc"))

    year = '2001'

    modis_lulc_file = f"/nas/rstor/akumar/USA/PhD/2024_Hurricanes/NDVI_LULC/Helene_Milton_LULC_LC_Type1_{year}-01.tif"
    modis_ndvi_file = f"/nas/rstor/akumar/USA/PhD/2024_Hurricanes/NDVI_LULC/Helene_Milton_NDVI_NDVI_{year}-01.tif"

    for geog_file in geog_files:

        new_filename = geog_file + f"_{year}"

        update_geog(geog_file, modis_lulc_file, modis_ndvi_file, new_filename)
        
    '''
    A = xr.open_dataset(geog_file)

    wrf_longitudes = A["XLONG_M"].squeeze().values
    wrf_latitudes = A["XLAT_M"].squeeze().values
    wrf_lulc = A["LU_INDEX"].squeeze().squeeze().values


    ds = gdal.Open(modis_lulc_file)
    obsdat = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    width = ds.RasterXSize
    height = ds.RasterYSize

    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]

# Getting Projection
    proj = ds.GetProjection()
    inproj = osr.SpatialReference()
    inproj.ImportFromWkt(proj)
#projcs = inproj.GetAuthorityCode("PROJCS")
    projcs = inproj.GetAuthorityCode('GEOGCS')

# Transforming coordinates
    xcord = np.array([minx, minx, maxx, maxx])
    ycord = np.array([miny, maxy, miny, maxy])

    proj_convert = pyproj.Transformer.from_crs(int(projcs), 4326, always_xy=True)

    cords = np.vstack(
    [
        proj_convert.transform(xcord[index], ycord[index])
        for index in range(xcord.shape[0])
    ]
)
    lon_start = cords[0, 0]
    lon_end = cords[2, 0]
    lat_start = cords[0, 1]
    lat_end = cords[1, 1]

    modis_longitudes = np.linspace(lon_start, lon_end, obsdat.shape[1])
    modis_latitudes = np.flip(np.linspace(lat_start, lat_end, obsdat.shape[0]))
    modis_lon_mesh, modis_lat_mesh = np.meshgrid(modis_longitudes, modis_latitudes)
    modis_lulc = obsdat


    regridded_LUINDEX = griddata(
    np.array((modis_lon_mesh.ravel(), modis_lat_mesh.ravel())).T,
    modis_lulc.ravel(),
    (wrf_longitudes, wrf_latitudes),
    method="nearest",
)

    regridded_LANDUSEF = np.array(
    [(regridded_LUINDEX == lulc_index) * 1 for lulc_index in np.arange(1, 22)]
)


####################################################################################

    wrf = geog_file


    ds = gdal.Open(modis_ndvi_file)
    obsdat = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    width = ds.RasterXSize
    height = ds.RasterYSize

    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]

# Getting Projection
    proj = ds.GetProjection()
    inproj = osr.SpatialReference()
    inproj.ImportFromWkt(proj)
#projcs = inproj.GetAuthorityCode("PROJCS")
    projcs = inproj.GetAuthorityCode('GEOGCS')

# Transforming coordinates
    xcord = np.array([minx, minx, maxx, maxx])
    ycord = np.array([miny, maxy, miny, maxy])

    proj_convert = pyproj.Transformer.from_crs(int(projcs), 4326, always_xy=True)

    cords = np.vstack(
    [
        proj_convert.transform(xcord[index], ycord[index])
        for index in range(xcord.shape[0])
    ]
)
    lon_start = cords[0, 0]
    lon_end = cords[2, 0]
    lat_start = cords[0, 1]
    lat_end = cords[1, 1]
    print(np.round(np.array([lon_start, lon_end, lat_start, lat_end]), 2))

    longitudes = np.linspace(lon_start, lon_end, obsdat.shape[1])
    latitudes = np.linspace(lat_start, lat_end, obsdat.shape[0])
    scale_factor = 0.0001
    ndvi_obs = np.flip(obsdat, 0) * scale_factor

###################### READ GREENFRAC FROM WRF ###########################
# wrf lon and lat are in 2d data
    data = xr.open_dataset(wrf)

    wrf_latitude = np.nanmean(np.squeeze(data["XLAT_M"].values), axis=1)
    wrf_longitude = np.nanmean(np.squeeze(data["XLONG_M"].values), axis=0)

    wrf_ndvi = np.squeeze(data["GREENFRAC"].values)[1, :, :]
###################### READ GREENFRAC FROM WRF ###########################


    lon_ind = np.logical_and(wrf_longitude >= lon_start, wrf_longitude <= lon_end)
    lat_ind = np.logical_and(wrf_latitude >= lat_start, wrf_latitude <= lat_end)

    wrf_lon_cropped = wrf_longitude[lon_ind]
    wrf_lat_cropped = wrf_latitude[lat_ind]

    wrf_ndvi_cropped = wrf_ndvi[np.ix_(lat_ind, lon_ind)]

    z = copy.deepcopy(ndvi_obs)

    filled_z = z.copy()
    filled_z[np.isnan(z)] = np.nanmean(z)
    f = interp2d(longitudes, latitudes, filled_z, kind="linear")

    nan_map = np.zeros_like(z)
    nan_map[np.isnan(z)] = 1
    f_nan = interp2d(longitudes, latitudes, nan_map, kind="linear")

    wrf_interp = f(wrf_lon_cropped, wrf_lat_cropped)
    nan_new = f_nan(wrf_lon_cropped, wrf_lat_cropped)
    wrf_interp[nan_new > 0.5] = np.nan
    wrf_interp[np.isnan(wrf_interp)] = 0

    wrf_ndvi_updated = copy.deepcopy(wrf_ndvi)
# wrf_ndvi_updated=wrf_ndvi.copy()
    wrf_ndvi_updated[np.ix_(lat_ind, lon_ind)] = wrf_interp
    wrf_ndvi_updated[wrf_ndvi_updated < 0.1] = 0

    wrf_ndvi_updated_1d = wrf_ndvi_updated.ravel()
    wrf_ndvi_updated_1d = wrf_ndvi_updated_1d[wrf_ndvi_updated_1d > 0.15]

# CROSS CHECK NEEDED
    greenfrac = (wrf_ndvi_updated - wrf_ndvi_updated_1d.min()) / (
    wrf_ndvi_updated_1d.max() - wrf_ndvi_updated_1d.min()
)
    greenfrac[greenfrac < 0] = 0
    greenfrac[greenfrac > 1] = 1

# REPLACING IN FILE


    new_wrf = xr.open_dataset(wrf)
    greenfrac_updated_reshape = (
    np.ones(shape=(new_wrf["GREENFRAC"].values.shape)) * greenfrac
)
    new_wrf["GREENFRAC"].values = greenfrac_updated_reshape

    luindex_updated_reshape = (
    np.ones(shape=(new_wrf["LU_INDEX"].values.shape)) * regridded_LUINDEX
)
    new_wrf["LU_INDEX"].values = luindex_updated_reshape

    landusef_updated_reshape = (
    np.ones(shape=(new_wrf["LANDUSEF"].values.shape)) * regridded_LANDUSEF
)
    new_wrf["LANDUSEF"].values = landusef_updated_reshape

    new_wrf.to_netcdf(new_filename)





#  start_date = '2024-10-08_00:00:00', '2024-10-08_00:00:00','2024-10-08_00:00:00'
#  end_date   = '2024-10-11_00:00:00', '2024-10-11_00:00:00', '2024-10-11_00:00:00'
#  interval_seconds = 10800
#  io_form_geogrid = 2,
# /

# &geogrid
#  parent_id         =   1, 1,2
#  parent_grid_ratio =   1, 3,3
#  i_parent_start    =   1, 160, 148
#  j_parent_start    =   1, 74, 74
#  e_we              =   370, 334, 280
#  e_sn              =   271, 295, 223
#  geog_data_res     = 'default', 'default','default'
#  dx = 9000,
#  dy = 9000,
#  map_proj = 'mercator',
#  ref_lat   =  29.0,
#  ref_lon   =  -85.0,
#  truelat1  =  29.0,
#  truelat2  =  29.0,
#  stand_lon =  -85.0,
#  geog_data_path = '/nas/rstor/akumar/WRF/geog'
#  opt_geogrid_tbl_path='/nas/rstor/akumar/WRF/WRF433/WPS/geogrid'
# /
