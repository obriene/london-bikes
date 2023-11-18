import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go

URL = "https://api.tfl.gov.uk/BikePoint"
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


def london_choropleth(df, column, column_name):
    fig, ax = plt.subplots()
    df.plot(ax=ax, linewidth=50, column=column, legend=True, legend_kwds={"label": column_name}, cmap="viridis")
    ax.axis("off")
    fig.savefig(f"output/{column_name}.png", dpi=300, bbox_inches="tight")
    return None


def get_points_map(london_map, points_df):
    fig, ax = plt.subplots()
    london_map.plot(ax=ax, linewidth=50)
    _ = points_df.plot(ax=ax, markersize=4, color='red', marker="o", linewidths=0, alpha=0.4)
    ax.axis("off")
    fig.savefig("output/bikepoint_locations.png", dpi=300, bbox_inches="tight")
    return None


def get_plotly_map(london_map, comb_df, colour_col, other_col):
    geojson = london_map.__geo_interface__
    fig = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=comb_df.index, z=comb_df[colour_col].fillna(0),
                                        customdata=comb_df[other_col],
                                        colorscale="Viridis", zmin=0, zmax=comb_df[colour_col].max(),
                                        marker_opacity=0.5, marker_line_width=0, text=comb_df["LAD23NM"],
                                        hovertemplate="<b>%{text}</b><br>" + colour_col +
                                                      ": %{z:,.0f}<br>" + other_col +
                                                      ": %{customdata:.0f}<extra></extra>",
                    colorbar=dict(title=colour_col)))
    fig.update_layout(width=750, height=750, mapbox_style="white-bg",
                      mapbox_zoom=8.5, mapbox_center={"lat": 51.5, "lon": -0.1})
    return fig


def get_bike_points_bar(df):
    fig, ax = plt.subplots()
    ax.grid(axis="x", linestyle="--", color="grey", alpha=0.5)
    ax.barh(df.index, df["Bike Points"])
    ax.set_yticks(df.index, df["LAD23NM"])
    ax.set_xlabel("Number of Bike Points")
    fig.savefig("output/bike_bar.png", bbox_inches='tight')
    return None


def obesity_range_plot(df, metric_name):
    las = [col for col in df.columns if col not in [MEDIAN, MIN, MAX]]
    fig, ax = plt.subplots()
    ax.grid(linestyle="--", color="grey", alpha=0.5)
    for n, la in enumerate(las):
        if n == 0:
            label = "London local authorities"
        else:
            label = None
        df_la = df[[la]].dropna()
        ax.plot(df_la.index, df_la[la], ms=0, ls="-", color="grey", lw=0.5, label=label)

    ax.fill_between(df.index, df[MIN], df[MAX], color="grey", alpha=0.5)
    ax.plot(df.index, df[MEDIAN], color="red", lw=1, zorder=3, label="Median")
    xticks = [x for x in range(df.index.min(), df.index.max()+1, 4)]
    xtick_labels = [f"{x}/{x+1}" for x in xticks]
    ax.set_xticks(xticks, xtick_labels)
    ax.axvline(2010.25, color="blue", ls="--", zorder=2)  # Scheme introduced in July 2010 -- approx here
    ax.annotate("Bike scheme\nintroduced", (2010.4, df[MAX].max()), va="center")
    ax.set_ylabel(metric_name)
    ax.legend(bbox_to_anchor=[0.5, -0.1], loc="center", ncol=2, frameon=False)

    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}%'))

    fig.savefig(f"output/{metric_name}.png", bbox_inches="tight", dpi=DPI)

    return None
