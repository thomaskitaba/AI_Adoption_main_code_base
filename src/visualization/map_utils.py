import geopandas as gpd
import matplotlib.pyplot as plt


def plot_choropleth(
    gdf: gpd.GeoDataFrame,
    column: str,
    title: str,
    cmap: str = "OrRd",
    figsize=(10, 10)
):
    """
    Generic choropleth plot for geospatial indicators.
    """

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    gdf.plot(
        column=column,
        ax=ax,
        legend=True,
        cmap=cmap,
        missing_kwds={"color": "lightgrey", "label": "No data"}
    )

    ax.set_title(title, fontsize=14)
    ax.axis("off")
    plt.show()
