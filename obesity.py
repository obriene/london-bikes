import fingertips_py as ftp
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("https://fingertips.phe.org.uk/api/all_data/csv/for_one_indicator?indicator_id=20602")
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


for metric_label, metric_code in METRIC_DICT.items():
    _, df_metric = get_london_df_metric(metric_code)
    obesity_range_plot(df_metric, metric_label)

# obesity_range = obesity_range_plot(df_las_piv)
# obesity_range.savefig("output/obesity_range.png", bbox_inches="tight")
#
# phof = ftp.get_profile_by_name('public health outcomes framework')
# phof_meta = ftp.get_metadata_for_profile_as_dataframe(phof['Id'])
# obesity_meta = phof_meta[phof_meta['Indicator'].str.lower().str.contains('obesity')]
# breakpoint()
# # GIves 3 indicators: obesity in early pregnancy (93584), reception overweight (20601), Year 6 overweight (20602)
# reception_obesity = ftp.retrieve_data.get_data_for_indicator_at_all_available_geographies('20601')