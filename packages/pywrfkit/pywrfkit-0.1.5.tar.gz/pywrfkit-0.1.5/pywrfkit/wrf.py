import xarray as xr

def add_coords(var: xr.DataArray, rename: bool = False) -> xr.DataArray:
    """
    Add coordinate information to an xarray DataArray by averaging longitude and latitude over 
    specific dimensions and assigning these as coordinates. Optionally, rename the coordinates.

    Parameters:
    var (xr.DataArray): The input DataArray that contains 'XLONG' and 'XLAT' coordinates.
    rename (bool, optional): If True, rename 'west_east' to 'longitudes' and 'south_north' 
                             to 'latitudes'. Default is False.

    Returns:
    xr.DataArray: The DataArray with updated coordinates. If rename is True, coordinates are also renamed.

    Example:
    --------
    import xarray as xr
    import numpy as np

    # Create a sample DataArray with dummy dimensions and coordinates
    data = np.random.rand(10, 10)
    lon = np.linspace(-180, 180, 10)
    lat = np.linspace(-90, 90, 10)
    ds = xr.DataArray(data, coords=[('south_north', lat), ('west_east', lon)],
                      name='temperature', attrs={'XLONG': lon, 'XLAT': lat})

    # Add coordinates and rename
    ds = add_coords(ds, rename=True)
    print(ds)
    """
    lon_1d = var.XLONG.mean(dim="south_north").values
    lat_1d = var.XLAT.mean(dim="west_east").values
    updated_var = var.drop(["XLONG", "XLAT"]).assign_coords(
        south_north=lat_1d, west_east=lon_1d
    )
    
    if rename:
        updated_var = renamelatlon(updated_var)
    
    return updated_var

def renamelatlon(var: xr.DataArray) -> xr.DataArray:
    """
    Rename coordinates in an xarray DataArray from 'west_east' to 'longitudes' 
    and from 'south_north' to 'latitudes'.

    Parameters:
    var (xr.DataArray): The input DataArray with 'west_east' and 'south_north' coordinates.

    Returns:
    xr.DataArray: The DataArray with renamed coordinates.

    Example:
    --------
    import xarray as xr
    import numpy as np

    # Create a sample DataArray
    data = np.random.rand(10, 10)
    lon = np.linspace(-180, 180, 10)
    lat = np.linspace(-90, 90, 10)
    ds = xr.DataArray(data, coords=[('latitudes', lat), ('longitudes', lon)],
                      name='temperature')

    # Rename coordinates
    ds = renamelatlon(ds)
    print(ds)
    """
    return var.rename({"west_east": "longitudes", "south_north": "latitudes"})

