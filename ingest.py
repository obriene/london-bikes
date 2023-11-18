import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import Point

import constants

DEPRIVATION_PATH = "data/london_deprivation.csv"
LONDON_GEOJSON_PATH = "data/london.geojson"

URL_BIKE = "https://api.tfl.gov.uk/BikePoint"
DEP_CODE = "Local Authority District code (2019)"
GEOMETRY = "geometry"
PERC_POINTS = "percentage Bike Points"
CUMULATIVE_POINTS = "cumulative points"
CUMULATIVE_PERC = "cumulative perc"

API_START = (
    "https://fingertips.phe.org.uk/api/all_data/csv/for_one_indicator?indicator_id="
)

AREA_CODE = "Area Code"
TIME_PERIOD = "Time period"
START_YEAR = "Start Year"
AREA_NAME = "Area Name"
VALUE = "Value"


def get_deprivation_index():
    """
    Gets the mean deprivation index decile by London Borough
    :return: dataframe
    """
    df_dep = pd.read_csv(DEPRIVATION_PATH)
    df_dep_london = df_dep[df_dep[DEP_CODE].str[:3] == constants.LONDON_CODE_START]
    df_dep_london_agg = (
        df_dep_london[[DEP_CODE, constants.DEP_DECILE]].groupby(DEP_CODE).mean()
    )
    return df_dep_london_agg.reset_index(drop=False).rename(
        columns={DEP_CODE: constants.LA_CODE}
    )


def get_bike_points():
    """
    Gets the coordinates of bike points
    :return: geodataframe
    """
    resp = requests.get(url=URL_BIKE)
    if resp.status_code != 200:
        raise requests.exceptions.RequestException()
    data = resp.json()
    df = pd.DataFrame(data)
    geometry = [
        Point(xy) for xy in zip(df["lon"], df["lat"])
    ]  # Combine the longitude and latitude to a point
    geo_df = gpd.GeoDataFrame(geometry=geometry)
    return geo_df


def get_london_map():
    """
    Gets the London map geodataframe, converting coordinates to EPSG 4326
    :return: geodataframe
    """
    london_map = gpd.read_file(LONDON_GEOJSON_PATH)
    london_map = london_map.reset_index()
    london_map = london_map.to_crs("EPSG:4326")
    return london_map


def get_points_borough(geo_df, london_map):
    """
    Gets the number of bike points in each borough
    :param geo_df: geodataframe with bike point coordinates
    :param london_map: geodataframe with London borough outlines
    :return: geodataframe
    """
    combined_geodf = gpd.sjoin(geo_df, london_map, how="inner", predicate="within")
    points_borough = (
        combined_geodf[[constants.LA_CODE, constants.LA_NAME, GEOMETRY]]
        .groupby(["LAD23CD", "LAD23NM"])
        .count()
        .reset_index()
        .rename(columns={GEOMETRY: constants.BIKE_POINTS})
    )  # Only 12 boroughs have bike points out of 33
    points_borough[PERC_POINTS] = (
        points_borough[constants.BIKE_POINTS]
        / points_borough[constants.BIKE_POINTS].sum()
    )

    points_borough = points_borough.sort_values(
        by=constants.BIKE_POINTS, ascending=False
    ).reset_index(drop=True)
    points_borough[CUMULATIVE_POINTS] = points_borough[constants.BIKE_POINTS].cumsum()  # Get a running total of points
    points_borough[CUMULATIVE_PERC] = (
        points_borough[CUMULATIVE_POINTS] / points_borough[constants.BIKE_POINTS].sum()
    )
    return points_borough


def combine_dfs(london_map, df_dep, points_borough):
    """
    Combines the relevant dataframes/geodataframes
    :param london_map: geodataframe with borough outlines
    :param df_dep: dataframe with deprivation
    :param points_borough: dataframe with bike points by borough
    :return: geodataframe, combined dataframe with columns from the above
    """
    dep_london_map = london_map.merge(df_dep, how="left", on=constants.LA_CODE)
    comb_df = dep_london_map.merge(
        points_borough.drop(columns=[constants.LA_NAME]),
        how="left",
        on=constants.LA_CODE,
    )
    comb_df[constants.BIKE_POINTS] = comb_df[constants.BIKE_POINTS].fillna(0)
    return comb_df


def get_london_df_metric(metric_code):
    """
    Get dataframe with London borough data for a health metric
    :param metric_code: int, metric code
    :return: dataframe
    """
    df = pd.read_csv(f"{API_START}{metric_code}")
    if len(df.index) < 1:
        raise ValueError("No data pulled through.")
    df_london_las = df[df[AREA_CODE].str[:3] == constants.LONDON_CODE_START]
    latest_year = df_london_las[TIME_PERIOD].max()
    df_las_latest = df_london_las[df_london_las[TIME_PERIOD] == latest_year]

    df_london_las[START_YEAR] = pd.to_numeric(
        df_london_las[TIME_PERIOD].str[:4], errors="coerce"
    )  # Time periods are of the form 2006/07, so the first four characters gives the start year
    df_las_piv = df_london_las[[AREA_NAME, VALUE, START_YEAR]].pivot(
        index=START_YEAR, columns=AREA_NAME, values=VALUE
    )

    df_las_piv = df_las_piv[
        df_las_piv.index != 2020
    ]  # Very few responses for Covid year and way higher than normal, so remove
    df_las_piv[constants.MEDIAN] = df_las_piv.median(axis=1)
    df_las_piv[constants.MAX] = df_las_piv.max(axis=1)
    df_las_piv[constants.MIN] = df_las_piv.min(axis=1)

    return df_las_latest, df_las_piv
