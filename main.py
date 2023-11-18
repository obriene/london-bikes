import constants
import ingest
import plotting

df_dep = ingest.get_deprivation_index()
df_bikes = ingest.get_bike_points()
london_map = ingest.get_london_map()
points_borough = ingest.get_points_borough(df_bikes, london_map)
comb_df = ingest.combine_dfs(london_map, df_dep, points_borough)

plotting.london_choropleth(comb_df, constants.DEP_DECILE, "Mean deprivation decile")
plotting.get_bike_points_bar(points_borough)
plotting.london_choropleth(comb_df, constants.BIKE_POINTS, constants.BIKE_POINTS)
plotting.get_points_map(london_map, df_bikes)

for metric_label, metric_code in constants.METRIC_DICT.items():
    df_latest, df_metric = ingest.get_london_df_metric(metric_code)
    plotting.obesity_range_plot(df_metric, metric_label)
