from scipy.interpolate import RegularGridInterpolator
import numpy as np
import xarray as xr


def convert_to_polar(variable, radius=5, resolution=None, coords=('hurricane_radial_distance_x', 'hurricane_radial_distance_y')):
    """
    Convert Cartesian coordinates to polar coordinates and interpolate values.

    This function takes a variable in Cartesian coordinates and converts it to polar coordinates.
    It then interpolates the values onto the new polar grid.

    Args:
        variable (xarray.DataArray): The variable to convert, typically wind speed or another meteorological variable.
        radius (float, optional): The maximum radius for polar coordinates in degrees. Defaults to 5.
        resolution (float, optional): The resolution of the polar grid. If None, it's calculated from the input data. Defaults to None.
        coords (tuple, optional): The names of the x and y coordinate variables in the input data. 
                                  Defaults to ('hurricane_radial_distance_x', 'hurricane_radial_distance_y').

    Returns:
        xarray.DataArray: A new DataArray with the variable interpolated onto a polar grid.
                          The dimensions are 'angle' (in radians) and 'radius' (in km).

    Note:
        - The function assumes that the input coordinates are in degrees and converts the radius to km (multiplied by 111.11).
        - The interpolation is performed using linear interpolation with NaN fill values for points outside the original grid.
    """
    if resolution is None:
        resolution = np.diff(variable[coords[0]])[0]
    r = np.arange(0, radius, resolution)
    ang = np.deg2rad(np.arange(0, 361))
    r_mesh, ang_mesh = np.meshgrid(r, ang)

    x_polar = r_mesh * np.cos(ang_mesh)
    y_polar = r_mesh * np.sin(ang_mesh)

    x_values = variable[coords[0]]
    y_values = variable[coords[1]]

    values = variable.values.T
    # print(x_values.shape, y_values.shape, values.shape)
    interp_func = RegularGridInterpolator(
        (x_values, y_values),
        values.T,
        method='linear',
        bounds_error=False,
        fill_value=np.nan
    )

    polar_coords = np.column_stack((x_polar.ravel(), y_polar.ravel()))
    polar_values = interp_func(polar_coords).reshape(x_polar.shape)

    polar_data = xr.DataArray(
        data=polar_values,
        dims=['angle', 'radius'],
        coords={
            'angle': ang,
            'radius': r*111.11,
        },
        attrs={
            'long_name': variable.attrs.get('long_name', 'Variable in polar coordinates'),
            'units': variable.attrs.get('units', 'km'),
        }
    )

    return polar_data



def get_polar_from_file(filename, radius=5, resolution=0.1):
    """
    Given a NetCDF filename, load the dataset and return a new xarray.Dataset
    containing model_outputs and merra_pcp in polar coordinates.

    Parameters
    ----------
    filename : str
        Path to the NetCDF file.
    radius : float
        Maximum radius (in degrees) for polar conversion.
    resolution : float
        Radial resolution (in degrees) for polar conversion.

    Returns
    -------
    polar_ds : xarray.Dataset
        Dataset with variables 'model_outputs_polar' and 'merra_pcp_polar'.
    """
    A = xr.open_dataset(filename)

    n_models = A.dims['model']
    n_times = A.dims['time']

    _tmp_data = A.isel(model=0, time=0)
    merra_pcp_da = xr.DataArray(
        _tmp_data['merra_pcp'].values,
        dims=('lat', 'lon'),
        coords={'lat': _tmp_data['lat'].values, 'lon': _tmp_data['lon'].values},
        attrs=_tmp_data['merra_pcp'].attrs
    )
    merra_pcp_da = merra_pcp_da.rename({'lat': 'hurricane_radial_distance_x', 'lon': 'hurricane_radial_distance_y'})
    polar_sample = convert_to_polar(
        merra_pcp_da,
        radius=radius,
        resolution=resolution,
        coords=('hurricane_radial_distance_x', 'hurricane_radial_distance_y')
    )
    polar_angle = polar_sample['angle'].values
    polar_radius = polar_sample['radius'].values

    polar_shape_model = (n_models, n_times, len(polar_angle), len(polar_radius))
    polar_shape_obs = (n_times, len(polar_angle), len(polar_radius))
    polar_model = np.full(polar_shape_model, np.nan, dtype=np.float32)
    polar_obs = np.full(polar_shape_obs, np.nan, dtype=np.float32)

    for model_index in range(n_models):
        for time_index in range(n_times):
            _tmp_data = A.isel(model=model_index, time=time_index)
            model_da = xr.DataArray(
                _tmp_data['model_outputs'].values,
                dims=('lat', 'lon'),
                coords={'lat': _tmp_data['lat'].values, 'lon': _tmp_data['lon'].values},
                attrs=_tmp_data['model_outputs'].attrs
            )
            model_da = model_da.rename({'lat': 'hurricane_radial_distance_x', 'lon': 'hurricane_radial_distance_y'})
            polar_model_data = convert_to_polar(
                model_da,
                radius=radius,
                resolution=resolution,
                coords=('hurricane_radial_distance_x', 'hurricane_radial_distance_y')
            )
            polar_model[model_index, time_index, :, :] = polar_model_data.values

    for time_index in range(n_times):
        _tmp_data = A.isel(model=0, time=time_index)  # Use any model, since ground truth is the same
        obs_da = xr.DataArray(
            _tmp_data['merra_pcp'].values,
            dims=('lat', 'lon'),
            coords={'lat': _tmp_data['lat'].values, 'lon': _tmp_data['lon'].values},
            attrs=_tmp_data['merra_pcp'].attrs
        )
        obs_da = obs_da.rename({'lat': 'hurricane_radial_distance_x', 'lon': 'hurricane_radial_distance_y'})
        polar_obs_data = convert_to_polar(
            obs_da,
            radius=radius,
            resolution=resolution,
            coords=('hurricane_radial_distance_x', 'hurricane_radial_distance_y')
        )
        polar_obs[time_index, :, :] = polar_obs_data.values

    polar_ds = xr.Dataset(
        {
            'model_outputs_polar': (('model', 'time', 'angle', 'radius'), polar_model, {
                'long_name': 'model_outputs in polar coordinates',
                'units': polar_sample.attrs.get('units', '')
            }),
            'merra_pcp_polar': (('time', 'angle', 'radius'), polar_obs, {
                'long_name': 'merra_pcp (observation) in polar coordinates',
                'units': polar_sample.attrs.get('units', '')
            })
        },
        coords={
            'model': A['model'].values if 'model' in A.coords else np.arange(n_models),
            'time': A['time'].values if 'time' in A.coords else np.arange(n_times),
            'angle': polar_angle,
            'radius': polar_radius
        }
    )

    return polar_ds
