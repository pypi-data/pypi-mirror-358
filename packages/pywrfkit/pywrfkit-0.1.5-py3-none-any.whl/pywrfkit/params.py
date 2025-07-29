import matplotlib.pyplot as plt

def get_params():
    """
    Update and return the Matplotlib rcParams with custom font size, weight, DPI, and savefig options.

    This function updates the Matplotlib rcParams to set the default font size to 16, font weight to bold,
    figure DPI to 300, and savefig bounding box to 'tight'.

    Returns:
    dict: The updated rcParams dictionary.

    Example:
    --------
    import matplotlib.pyplot as plt

    # Update the rcParams with custom settings
    get_params()

    # Create a simple plot to demonstrate the updated settings
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2, 3], [10, 20, 25, 30])
    ax.set_title("Sample Plot")
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")

    # Save the plot with the updated savefig parameters
    plt.savefig("sample_plot.png")

    # Show the plot
    plt.show()
    """
    return plt.rcParams.update({
        "font.size": 16,
        "font.weight": "bold",
        "figure.dpi": 300,          # Update DPI to 300 or any value you prefer
        "savefig.bbox": "tight"     # Update bbox_inches to 'tight' or any value you prefer
    })

