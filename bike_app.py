import json

import geopandas as gpd
import plotly.graph_objects as go
import streamlit as st

st.title("London Bike Hire")

london_map = gpd.read_file("data/london_map.geojson")

fig = go.Figure(go.Choroplethmapbox(geojson=london_map.geometry, locations=london_map.index, z=df.unemp,
                                    colorscale="Viridis", zmin=0, zmax=12,
                                    marker_opacity=0.5, marker_line_width=0))
fig.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129})
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()