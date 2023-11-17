import requests

import fiona
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
from pyproj import Transformer, Proj
from shapely.geometry import Point

URL = "https://api.tfl.gov.uk/BikePoint"


resp = requests.get(url=URL)
if resp.status_code != 200:
    raise requests.exceptions.RequestException()
data = resp.json()

df = pd.DataFrame(data)

lo=df["lon"]
la=df["lat"]

trans = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:27700",
    always_xy=True,
)
xx, yy = trans.transform(df["lon"].values, df["lat"].values)

#uk_map = gpd.read_file("data/MSOA_Dec_2011_Boundaries_Super_Generalised_Clipped_BSC_EW_V3_2022_7707677027087735278.geojson") #https://geoportal.statistics.gov.uk/datasets/ons::msoa-dec-2011-boundaries-super-generalised-clipped-bsc-ew-v3/explore

# Cut down to London and save as geojson
london_plus_map = gpd.read_file("data/Local_Authority_Districts_May_2023_UK_BGC_V2_-6664827264414594220.geojson")
london_map = london_plus_map[london_plus_map["LAD23CD"].str[:3] == "E09"]
london_map.to_file("data/london.geojson", driver="GeoJSON")


#london_map = gpd.read_file("data/MSOA_2011_London_gen_MHW.shp") # https://data.london.gov.uk/dataset/statistical-gis-boundary-files-london -- needs shx file too
#london_map = gpd.read_file("data/MSOA_2011_EW_BSC_V3.shp")
# london_geo = london_map.to_crs(epsg=4326)
fig,ax = plt.subplots(figsize = (15,15))
london_map.plot(ax=ax)
geometry = [Point(xy) for xy in zip(xx,yy)]
geo_df = gpd.GeoDataFrame(geometry = geometry)
g = geo_df.plot(ax = ax, markersize = 20, color = 'red',marker = '.',alpha=0.4)

combined_geodf = gpd.sjoin(geo_df, london_map, how="inner", predicate="within")
points_borough = combined_geodf[["LAD23NM", "geometry"]].groupby("LAD23NM").count().reset_index().rename(columns={"geometry": "bike_points"}) # Only 12 boroughs have bike points
points_borough["percentage_bike_points"] = points_borough["bike_points"] / points_borough["bike_points"].sum()
num_boroughs = len(london_map["LAD23NM"].drop_duplicates()) # 33 boroughs

points_borough = points_borough.sort_values(by="bike_points", ascending=False).reset_index(drop=True)

comb_df = london_map.merge(points_borough, on="LAD23NM", how="left")
london_map = london_map.reset_index()
london_map = london_map.to_crs("EPSG:4326")
geojson = london_map.__geo_interface__

fig = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=comb_df.index, z=comb_df["bike_points"].fillna(0),
                                    colorscale="Viridis", zmin=0, zmax=comb_df["bike_points"].max(),
                                    marker_opacity=0.5, marker_line_width=0, text=comb_df["LAD23NM"],
                                    hovertemplate="<b>%{text}</b><br>" + "%{z:,.0f}<br><extra></extra>"))
fig.update_layout(width=750, height=750, mapbox_style="white-bg",
                  mapbox_zoom=8.5, mapbox_center = {"lat": 51.5, "lon": -0.1})
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
breakpoint()
def get_bike_points_bar(df):
    fig, ax = plt.subplots()
    ax.grid(axis="x", linestyle="--", color="grey", alpha=0.5)
    ax.barh(df.index, df["bike_points"])
    ax.set_yticks(df.index, df["LAD23NM"])
    ax.set_xlabel("Number of Bike Points")
    return fig

bike_bar = get_bike_points_bar(points_borough)
bike_bar.savefig("output/bike_bar.png", bbox_inches='tight')

# from requests.auth import HTTPBasicAuth
# import requests
#
# url = 'https://api_url'
# headers = {'Accept': 'application/json'}
# auth = HTTPBasicAuth('apikey', '1234abcd')
# files = {'file': open('filename', 'rb')}
#
# req = requests.get(url, headers=headers, auth=auth, files=files)
