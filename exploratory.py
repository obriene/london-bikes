import fingertips_py as ftp
import geopandas as gpd

import constants


def cut_map_to_london():
    london_plus_map = gpd.read_file(
        "data/Local_Authority_Districts_May_2023_UK_BGC_V2_-6664827264414594220.geojson"
    )
    london_map = london_plus_map[
        london_plus_map["LAD23CD"].str[:3] == constants.LONDON_CODE_START
    ]
    london_map.to_file("data/london.geojson", driver="GeoJSON")
    return None


# Exploratory work finding possible metrics below

# phof = ftp.get_profile_by_name('public health outcomes framework')
# phof_meta = ftp.get_metadata_for_profile_as_dataframe(phof['Id'])
# obesity_meta = phof_meta[phof_meta['Indicator'].str.lower().str.contains('obesity')]
# # GIves 3 indicators: obesity in early pregnancy (93584), reception overweight (20601), Year 6 overweight (20602)
# reception_obesity = ftp.retrieve_data.get_data_for_indicator_at_all_available_geographies('20601')
