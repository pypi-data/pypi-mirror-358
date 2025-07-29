import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
import cartopy


def get_proj():
    """
    Return a dictionary containing the transform and subplot keyword arguments for a Plate Carree projection.

    Returns:
    dict: A dictionary with 'transform' and 'subplot_kws' keys. The 'transform' key has the Plate Carree 
          coordinate reference system, and the 'subplot_kws' key contains a dictionary with the projection set to Plate Carree.

    Example:
    --------
    import matplotlib.pyplot as plt

    # Get the projection dictionary
    proj_dict = get_proj()

    # Create a figure and an axes with the Plate Carree projection
    fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=proj_dict['subplot_kws'])

    # Add coastlines to the axes
    ax.coastlines()

    # Add a grid with the specified transform
    ax.gridlines(crs=proj_dict['transform'])

    # Show the plot
    plt.show()
    """
    return {'transform': ccrs.PlateCarree(), 'subplot_kws': {"projection": ccrs.PlateCarree()}}


def plot_coast(axes: cartopy.mpl.geoaxes.GeoAxes, color='black', linewidth=2, gridlines_alpha=0.5, states=False) -> None:
    """
    Add coastlines, country borders, and optional state/provincial borders to a Cartopy GeoAxes.

    Parameters:
    axes (cartopy.mpl.geoaxes.GeoAxes): The GeoAxes instance to plot on.
    color (str, optional): Color of the coastlines and borders. Default is 'black'.
    linewidth (int or float, optional): Width of the coastlines and borders. Default is 2.
    gridlines_alpha (float, optional): Transparency level of the gridlines. Default is 0.5.
    states (bool, optional): If True, include state/provincial borders. Default is False.

    Returns:
    gl (cartopy.mpl.gridliner.Gridliner): The gridliner instance with longitude and latitude formatting.

    Example:
    --------
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
    plot_coast(ax, color='blue', linewidth=1.5, gridlines_alpha=0.7, states=True)
    plt.show()
    """

    countries = cfeature.NaturalEarthFeature(
        scale="10m", category="cultural", name="admin_0_countries", facecolor="none"
    )
    axes.add_feature(countries, edgecolor=color, linewidth=linewidth)

    if states:
        states = cfeature.NaturalEarthFeature(
            scale="10m",
            category="cultural",
            name="admin_1_states_provinces_lines",
            facecolor="none",
        )
        axes.add_feature(states, edgecolor=color, linewidth=linewidth)
    
    gl = axes.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=True,
        linewidth=1,
        color="gray",
        alpha=gridlines_alpha,
        linestyle="--",
    )
    gl.top_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = False
    gl.xlines = True
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    
    axes.add_feature(cfeature.LAND)
    axes.add_feature(cfeature.OCEAN, color='#C6E2FF')

    return gl

