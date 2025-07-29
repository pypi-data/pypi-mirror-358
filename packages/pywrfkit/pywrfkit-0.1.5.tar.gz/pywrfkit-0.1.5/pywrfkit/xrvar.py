import xarray as xr

import pandas as pd

pd.set_option('display.max_rows', None)
def varlist(A, attrs_names):
    """
    Creates a DataFrame containing variable names, the specified attributes (or empty if not available), 
    and shapes from the given dataset.
    
    Parameters:
    A (Dataset): The input dataset containing variables.
    attrs_names (list): A list of attribute names to retrieve for each variable.

    Returns:
    pd.DataFrame: A DataFrame with columns for the variable names, the specified attribute values (or empty if not available), and shapes.
    """
    # Extract variables, their attribute values (or empty if not available), and their shapes

    if isinstance(attrs_names, str):
        attrs_names = [attrs_names]
    

    data = [
        [var] + [A[var].attrs.get(attr, '-') for attr in attrs_names] + [A[var].shape] 
        for var in list(A.variables.keys())
    ]
    
    # Define column names with 'Variable' and the provided attribute names
    columns = ['Variable'] + [attr.capitalize() for attr in attrs_names] + ['Shape']
    
    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data, columns=columns)
    
    return df
