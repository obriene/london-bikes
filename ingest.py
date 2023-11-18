import requests

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

URL_BIKE = "https://api.tfl.gov.uk/BikePoint"
DEP_CODE = "Local Authority District code (2019)"
DEP_DECILE = "Index of Multiple Deprivation (IMD) Decile"
LA_CODE = "LAD23CD"

API_START = "https://fingertips.phe.org.uk/api/all_data/csv/for_one_indicator?indicator_id="

AREA_CODE = "Area Code"
TIME_PERIOD = "Time period"
START_YEAR = "Start Year"
AREA_NAME = "Area Name"
VALUE = "Value"
MEDIAN = "Median"
MIN = "Min"
MAX = "Max"

DPI = 300

METRIC_DICT = {"Proportion of overweight Year 6 children": 20602,
               "Proportion of overweight Reception children": 20601}


def get_deprivation_index():
    df_dep = pd.read_csv("data/london_deprivation.csv")
    df_dep_london = df_dep[df_dep[DEP_CODE].str[:3] == "E09"]
    df_dep_london_agg = df_dep_london[[DEP_CODE, DEP_DECILE]].groupby(DEP_CODE).mean()
    return df_dep_london_agg.reset_index(drop=False).rename(columns={DEP_CODE: LA_CODE})


def get_bike_points():
    resp = requests.get(url=URL_BIKE)
    if resp.status_code != 200:
        raise requests.exceptions.RequestException()
    data = resp.json()
    df = pd.DataFrame(data)
    geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
    geo_df = gpd.GeoDataFrame(geometry=geometry)
    return geo_df


def get_london_map():
    london_plus_map = gpd.read_file("data/Local_Authority_Districts_May_2023_UK_BGC_V2_-6664827264414594220.geojson")
    london_map = london_plus_map[london_plus_map["LAD23CD"].str[:3] == "E09"]
    london_map.to_file("data/london.geojson", driver="GeoJSON")
    london_map = london_map.reset_index()
    london_map = london_map.to_crs("EPSG:4326")
    return london_map


def get_points_borough(geo_df, london_map):
    combined_geodf = gpd.sjoin(geo_df, london_map, how="inner", predicate="within")
    points_borough = combined_geodf[["LAD23CD", "LAD23NM", "geometry"]].groupby(["LAD23CD", "LAD23NM"]).count().reset_index().rename(columns={"geometry": "Bike Points"}) # Only 12 boroughs have bike points
    points_borough["percentage_Bike Points"] = points_borough["Bike Points"] / points_borough["Bike Points"].sum()
    num_boroughs = len(london_map["LAD23NM"].drop_duplicates()) # 33 boroughs

    points_borough = points_borough.sort_values(by="Bike Points", ascending=False).reset_index(drop=True)
    points_borough["cumulative_points"] = points_borough["Bike Points"].cumsum()
    points_borough["cumulative_perc"] = points_borough["cumulative_points"] / points_borough["Bike Points"].sum()
    return points_borough


def combine_dfs(london_map, df_dep, points_borough):
    dep_london_map = london_map.merge(df_dep, how="left", on=LA_CODE)
    comb_df = dep_london_map.merge(points_borough.drop(columns=["LAD23NM"]), how="left", on=LA_CODE).fillna(0)
    return comb_df


def get_london_df_metric(metric_code):
    df = pd.read_csv(f"{API_START}{metric_code}")
    df_london_las = df[df[AREA_CODE].str[:3] == "E09"]  # 'E09' is the start of codes for London local authorities
    latest_year = df_london_las[TIME_PERIOD].max()
    df_las_latest = df_london_las[df_london_las[TIME_PERIOD] == latest_year]

    df_london_las[START_YEAR] = pd.to_numeric(df_london_las[TIME_PERIOD].str[:4], errors="coerce")
    df_las_piv = df_london_las[[AREA_NAME, VALUE, START_YEAR]].pivot(index=START_YEAR, columns=AREA_NAME, values=VALUE)

    df_las_piv = df_las_piv[df_las_piv.index != 2020]  # Very few responses for Covid year and way higher than normal
    df_las_piv[MEDIAN] = df_las_piv.median(axis=1)
    df_las_piv[MAX] = df_las_piv.max(axis=1)
    df_las_piv[MIN] = df_las_piv.min(axis=1)

    return df_las_latest, df_las_piv

