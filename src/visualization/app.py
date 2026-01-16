# src/visualization/app.py

# -------------------------------
# Core Dash imports
# -------------------------------
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

# -------------------------------
# Leaflet-based mapping for Dash
# -------------------------------
import dash_leaflet as dl
import dash_leaflet.express as dlx

# -------------------------------
# Data handling
# -------------------------------
import geopandas as gpd
import json

# -------------------------------
# Configuration (hard-coded for MVP)
# -------------------------------

# Pick ONE scenario and ONE level for now
GEOJSON_PATH = "data/policy_maps/credit_reform_woreda.geojson"

# Column used for choropleth coloring
COLOR_COLUMN = "policy_effect"

# -------------------------------
# Load and prepare GeoJSON
# -------------------------------

# Read GeoJSON using GeoPandas
gdf = gpd.read_file(GEOJSON_PATH)

# Ensure CRS is WGS84 (Leaflet requirement)
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# Convert GeoDataFrame to GeoJSON dict
geojson = json.loads(gdf.to_json())

# -------------------------------
# Create color scale
# -------------------------------

# Define diverging color scale:
# red (negative) -> white (neutral) -> green (positive)
colorscale = [
    [0.0, "#b2182b"],
    [0.5, "#f7f7f7"],
    [1.0, "#1a9641"]
]

# Create a color mapping function
# This maps policy_effect values to colors
color_prop = dlx.choropleth(
    geojson,
    color_prop=COLOR_COLUMN,
    colorscale=colorscale,
    style={
        "weight": 1,
        "color": "black",
        "fillOpacity": 0.75
    }
)

# -------------------------------
# Initialize Dash app
# -------------------------------
app = dash.Dash(__name__)

# -------------------------------
# App layout
# -------------------------------
app.layout = html.Div([
    # Title
    html.H2("AI Adoption Policy Impact Map (MVP)", style={"textAlign": "center"}),

    # Map container
    dl.Map(
        center=[9.0, 38.7],  # Ethiopia center
        zoom=6,
        style={"width": "100%", "height": "80vh"},
        children=[
            # Base map tiles (light theme)
            dl.TileLayer(),

            # Choropleth GeoJSON layer
            dl.GeoJSON(
                data=geojson,
                id="geojson-layer",

                # Enable hover highlighting
                hoverStyle={
                    "weight": 3,
                    "color": "#333",
                    "fillOpacity": 0.9
                },

                # Attach style based on policy_effect
                options=dict(style=color_prop),

                # Enable click events
                zoomToBounds=True
            )
        ]
    ),

    # Info box (updates when user clicks a polygon)
    html.Div(
        id="info-box",
        style={
            "padding": "10px",
            "margin": "10px",
            "border": "1px solid #ccc",
            "borderRadius": "5px",
            "width": "50%",
            "marginLeft": "auto",
            "marginRight": "auto"
        }
    )
])

# -------------------------------
# Callback: update info box on click
# -------------------------------
@app.callback(
    Output("info-box", "children"),
    Input("geojson-layer", "click_feature")
)
def display_feature_info(feature):
    """
    This function runs whenever a user clicks
    an administrative boundary on the map.
    """

    # If nothing clicked yet
    if feature is None:
        return "Click a woreda to see details."

    props = feature["properties"]

    return html.Div([
        html.H4(f"📍 {props.get('woreda', 'Unknown Woreda')}"),
        html.P(f"Baseline adoption: {props.get('baseline_adoption_prob', 0):.2f}"),
        html.P(f"Counterfactual adoption: {props.get('counterfactual_adoption_prob', 0):.2f}"),
        html.P(
            f"Policy effect: {props.get('policy_effect', 0):+.2f}",
            style={"fontWeight": "bold"}
        ),
        html.P(f"Scenario: {props.get('scenario', 'N/A')}")
    ])

# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
