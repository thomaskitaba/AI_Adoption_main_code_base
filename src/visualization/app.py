# src/visualization/app.py

import dash
from dash import html, dcc, Output, Input
import dash_leaflet as dl

from .loader import load_geojson
from .utils import get_diverging_color


# ---------------------------
# Dash app initialization
# ---------------------------
app = dash.Dash(__name__)
server = app.server  # for deployment later


# ---------------------------
# UI Layout
# ---------------------------
app.layout = html.Div([
    html.H3("AI Adoption Policy Impact Map"),

    # Scenario selector
    dcc.Dropdown(
        id="scenario",
        options=[
            {"label": s.replace("_", " ").title(), "value": s}
            for s in [
                "baseline",
                "extension_reform",
                "credit_reform",
                "education_investment",
                "market_infrastructure",
                "land_tenure_reform",
                "full_transformation_package",
            ]
        ],
        value="credit_reform",
        clearable=False
    ),

    # Administrative level selector
    dcc.RadioItems(
        id="level",
        options=[
            {"label": "Woreda", "value": "woreda"},
            {"label": "Zone", "value": "zone"},
            {"label": "Region", "value": "region"},
        ],
        value="woreda",
        inline=True
    ),

    # Map container
    dl.Map(
        id="map",
        center=[9.0, 40.0],  # Ethiopia center
        zoom=6,
        style={"width": "100%", "height": "600px"},
        children=[
            dl.TileLayer(),  # Default OpenStreetMap basemap
            dl.GeoJSON(
                id="geojson",
                style={
                    "fillColor": "{fillColor}",
                    "color": "black",
                    "weight": 0.5,
                    "fillOpacity": 0.7,
                },
                hoverStyle={"weight": 2, "color": "blue"},
                children=[
                    dl.Tooltip(content="Policy Effect: {policy_effect}")
                ]
            )
        ]
    ),

    # Click info panel
    html.Div(id="info", style={"marginTop": "10px"})
])


# ---------------------------
# Map update callback
# ---------------------------
@app.callback(
    Output("geojson", "data"),
    Input("scenario", "value"),
    Input("level", "value")
)
def update_map(scenario, level):
    """
    Update the map when scenario or level changes.
    """

    geojson = load_geojson(scenario, level)

    return geojson


# ---------------------------
# App entry point
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
