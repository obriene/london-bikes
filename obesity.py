import fingertips_py as ftp
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("https://fingertips.phe.org.uk/api/all_data/csv/for_one_indicator?indicator_id=20601")
df_london_las = df[df["Area Code"].str[:3] == "E09"]
latest_year = df_london_las["Time period"].max()
df_las_latest = df_london_las[df_london_las["Time period"] == latest_year]

df_london_las["Start year"] = pd.to_numeric(df_london_las["Time period"].str[:4], errors="coerce")
df_las_piv = df_london_las[["Area Name", "Value", "Start year"]].pivot(index="Start year", columns="Area Name", values="Value")

df_las_piv = df_las_piv[df_las_piv.index != 2020] # Very few responses and way higher than normal
df_las_piv["median"] = df_las_piv.median(axis=1)
df_las_piv["max"] = df_las_piv.max(axis=1)
df_las_piv["min"] = df_las_piv.min(axis=1)


def obesity_range_plot(df):
    las = [col for col in df.columns if col not in ["median", "max", "min"]]
    fig, ax = plt.subplots()
    ax.grid(linestyle="--", color="grey")
    for la in las:
        df_la = df[[la]].dropna()
        ax.plot(df_la.index, df_la[la], ms=0, ls="-", color="grey", lw=0.5)

    ax.fill_between(df.index, df["min"], df["max"], color="grey", alpha=0.5)
    ax.plot(df.index, df["median"], color="red", lw=1)

    return fig

obesity_range = obesity_range_plot(df_las_piv)
obesity_range.savefig("output/obesity_range.png", bbox_inches="tight")

# phof = ftp.get_profile_by_name('public health outcomes framework')
# phof_meta = ftp.get_metadata_for_profile_as_dataframe(phof['Id'])
# obesity_meta = phof_meta[phof_meta['Indicator'].str.lower().str.contains('obesity')]
# # GIves 3 indicators: obesity in early pregnancy (93584), reception overweight (20601), Year 6 overweight (20602)
# reception_obesity = ftp.retrieve_data.get_data_for_indicator_at_all_available_geographies('20601')