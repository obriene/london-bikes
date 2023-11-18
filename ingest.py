import requests

import fiona
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
from pyproj import Transformer, Proj
from shapely.geometry import Point

URL = "https://api.tfl.gov.uk/BikePoint"
DEP_CODE = "Local Authority District code (2019)"
DEP_DECILE = "Index of Multiple Deprivation (IMD) Decile"
LA_CODE = "LAD23CD"


def get_deprivation_index():
    df_dep = pd.read_csv("data/london_deprivation.csv")
    df_dep_london = df_dep[df_dep[DEP_CODE].str[:3] == "E09"]
    df_dep_london_agg = df_dep_london[[DEP_CODE, DEP_DECILE]].groupby(DEP_CODE).mean()
    return df_dep_london_agg.reset_index(drop=False).rename(columns={DEP_CODE: LA_CODE})


def london_choropleth(df, column, column_name):
    fig, ax = plt.subplots()
    df.plot(ax=ax, linewidth=50, column=column, legend=True, legend_kwds={"label": column_name}, cmap="viridis")
    ax.axis("off")
    fig.savefig(f"output/{column_name}.png", dpi=300, bbox_inches="tight")
    return None


df_dep = get_deprivation_index()


resp = requests.get(url=URL)
if resp.status_code != 200:
    raise requests.exceptions.RequestException()
data = resp.json()

df = pd.DataFrame(data)

# Cut down to London and save as geojson
london_plus_map = gpd.read_file("data/Local_Authority_Districts_May_2023_UK_BGC_V2_-6664827264414594220.geojson")
london_map = london_plus_map[london_plus_map["LAD23CD"].str[:3] == "E09"]
london_map.to_file("data/london.geojson", driver="GeoJSON")


#london_map = gpd.read_file("data/MSOA_2011_London_gen_MHW.shp") # https://data.london.gov.uk/dataset/statistical-gis-boundary-files-london -- needs shx file too
#london_map = gpd.read_file("data/MSOA_2011_EW_BSC_V3.shp")
# london_geo = london_map.to_crs(epsg=4326)
fig, ax = plt.subplots()
london_map = london_map.reset_index()
london_map = london_map.to_crs("EPSG:4326")
london_map.plot(ax=ax, linewidth=50)
geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
geo_df = gpd.GeoDataFrame(geometry = geometry)
g = geo_df.plot(ax = ax, markersize=4, color='red', marker="o", linewidths=0, alpha=0.4)
ax.axis("off")
fig.savefig("output/bikepoint_locations.png", dpi=300, bbox_inches="tight")

dep_london_map = london_map.merge(df_dep, how="left", on=LA_CODE)
# fig_dep, ax_dep = plt.subplots()
# dep_london_map.plot(ax=ax_dep, linewidth=50, column=DEP_DECILE, legend=True,
#                     legend_kwds={"label": "Mean deprivation decile"}, cmap="viridis")
# ax_dep.axis("off")
# fig_dep.savefig("output/deprivation_map.png", dpi=300, bbox_inches="tight")
london_choropleth(dep_london_map, DEP_DECILE, "Mean deprivation decile")

combined_geodf = gpd.sjoin(geo_df, london_map, how="inner", predicate="within")
points_borough = combined_geodf[["LAD23CD", "LAD23NM", "geometry"]].groupby(["LAD23CD", "LAD23NM"]).count().reset_index().rename(columns={"geometry": "Bike Points"}) # Only 12 boroughs have bike points
points_borough["percentage_Bike Points"] = points_borough["Bike Points"] / points_borough["Bike Points"].sum()
num_boroughs = len(london_map["LAD23NM"].drop_duplicates()) # 33 boroughs

points_borough = points_borough.sort_values(by="Bike Points", ascending=False).reset_index(drop=True)

comb_df = london_map.merge(points_borough, on="LAD23NM", how="left")
geojson = london_map.__geo_interface__

fig = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=comb_df.index, z=comb_df["Bike Points"].fillna(0),
                                    colorscale="Viridis", zmin=0, zmax=comb_df["Bike Points"].max(),
                                    marker_opacity=0.5, marker_line_width=0, text=comb_df["LAD23NM"],
                                    hovertemplate="<b>%{text}</b><br>" + "%{z:,.0f}<br><extra></extra>"))
fig.update_layout(width=750, height=750, mapbox_style="white-bg",
                  mapbox_zoom=8.5, mapbox_center = {"lat": 51.5, "lon": -0.1})
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

def get_bike_points_bar(df):
    fig, ax = plt.subplots()
    ax.grid(axis="x", linestyle="--", color="grey", alpha=0.5)
    ax.barh(df.index, df["Bike Points"])
    ax.set_yticks(df.index, df["LAD23NM"])
    ax.set_xlabel("Number of Bike Points")
    return fig

bike_bar = get_bike_points_bar(points_borough)
points_borough["cumulative_points"] = points_borough["Bike Points"].cumsum()
points_borough["cumulative_perc"] = points_borough["cumulative_points"] / points_borough["Bike Points"].sum()
dep_london_map = dep_london_map.merge(points_borough.drop(columns=["LAD23NM"]), how="left", on=LA_CODE).fillna(0)
london_choropleth(dep_london_map, "Bike Points", "Bike Points")
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
