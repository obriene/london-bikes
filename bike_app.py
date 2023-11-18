import streamlit as st

import constants
import ingest
import plotting


def get_obesity_metrics(comb_df):
    for metric_label, metric_code in constants.METRIC_DICT.items():
        df_latest, _ = ingest.get_london_df_metric(metric_code)
        df_latest = df_latest[df_latest[ingest.VALUE].notna()]
        df_latest = df_latest[["Area Code", ingest.VALUE]].rename(
            columns={ingest.VALUE: metric_label, "Area Code": constants.LA_CODE}
        )
        comb_df = comb_df.merge(df_latest, how="left", on=constants.LA_CODE)
    return comb_df


def bike_or_metric_colour():
    val_choice = st.selectbox(
        "Colour set by bike points or metric:", ["Bike Points", "Metric"], key="colour"
    )
    return val_choice


def comparator_selector():
    values = [constants.DEP_DECILE] + [key for key in constants.METRIC_DICT.keys()]
    val_choice = st.selectbox("Health/deprivation metric", values, key="metric")
    return val_choice


st.title("London Bike Hire")

df_dep = ingest.get_deprivation_index()
df_bikes = ingest.get_bike_points()
london_map = ingest.get_london_map()
points_borough = ingest.get_points_borough(df_bikes, london_map)
comb_df = ingest.combine_dfs(london_map, df_dep, points_borough)
comb_df = get_obesity_metrics(comb_df)

columns = st.columns([1, 1], gap="small")

with columns[0]:
    metric = comparator_selector()

with columns[1]:
    colour_selector = bike_or_metric_colour()

if colour_selector == "Bike Points":
    colour_col = "Bike Points"
    other_col = metric
else:
    colour_col = metric
    other_col = "Bike Points"

fig = plotting.get_plotly_map(
    london_map, comb_df, colour_col=colour_col, other_col=other_col
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<p style='font-size:20px'>The map can be toggled with the dropdowns to change metric and whether"
            "colour is given by the number of bike points or the metric.<br>"
            "The deprivation index is the mean of the deciles of all the wards in the borough. A lower deprivation "
            "index means more deprived (decile 1 is the most deprived 10%).<br>"
            "City of London does not have obesity data, so will show as blank on the map in this case.</p>",
            unsafe_allow_html=True)
