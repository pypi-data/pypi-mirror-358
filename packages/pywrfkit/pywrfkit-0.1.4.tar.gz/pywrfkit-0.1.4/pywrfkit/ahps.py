import xarray as xr
import numpy as np
import cartopy.crs as ccrs


def read_ahps(ahps_filename):

    """
    Read and process the AHPS (Advanced Hydrologic Prediction Service) dataset from a given file. The AHPS dataset is
    transformed to Plate Carree projection and invalid observation values are replaced with NaN.

            Parameters
            ----------
            ahps_filename : str
                Filename for the AHPS dataset.

            Returns
            -------
            lon_platecarre : numpy.ndarray
                Longitude values in Plate Carree projection.

            lat_platecarre : numpy.ndarray
                Latitude values in Plate Carree projection.

            obs : numpy.ndarray
                Observation values from the AHPS dataset, with invalid values replaced with NaN and converted to millimeters.

        Example
        --------
        >>> read_ahps("my_ahps_dataset.nc")
        (array([[-180., -178., ...,  178.,  180.],
                [-180., -178., ...,  178.,  180.],
                ...,
                [-180., -178., ...,  178.,  180.],
                [-180., -178., ...,  178.,  180.]]),
         array([[-90., -90., ..., -90., -90.],
                [-88., -88., ..., -88., -88.],
                ...,
                [ 88.,  88., ...,  88.,  88.],
                [ 90.,  90., ...,  90.,  90.]]),
         array([[nan, nan, ..., nan, nan],
                [nan, nan, ..., nan, nan],
                ...,
                [nan, nan, ..., nan, nan],
                [nan, nan, ..., nan, nan]]))

    """

    ahps = xr.open_dataset(ahps_filename)
    crs = ahps["crs"]
    lon = ahps.variables["x"][:]
    lat = ahps.variables["y"][:]

    polar_proj = ccrs.NorthPolarStereo(
        central_longitude=crs.attrs["straight_vertical_longitude_from_pole"],
        true_scale_latitude=crs.attrs["standard_parallel"],
        globe=None,
    )
    plate_proj = ccrs.PlateCarree(central_longitude=0.0, globe=None)
    x_mesh, y_mesh = np.meshgrid(lon, lat)
    ahps_latlon = plate_proj.transform_points(polar_proj, x_mesh, y_mesh)
    lon_platecarre = ahps_latlon[:, :, 0]
    lat_platecarre = ahps_latlon[:, :, 1]
    obs = ahps.variables["observation"].values * 25.4
    obs[obs <= 0] = np.nan

    return lon_platecarre, lat_platecarre, obs
