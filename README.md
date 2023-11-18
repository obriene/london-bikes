# london-bikes

## Setup
This was done in Python 3.10. To set up your environment, please use the `requirements.txt` file in a clean environment:
`pip install -r requirements.txt`

## Data
All data is public and has been added to the `data` folder (other than that using APIs) for ease of the user.

The Local Authority geojson can be found here: https://geoportal.statistics.gov.uk/datasets/ons::local-authority-districts-may-2023-boundaries-uk-bgc/explore.
Generalised boundaries were used to keep the file manageable but to keep important structure.

To cut down on the file size needing to be loaded each time, `london.geojson` was created (see `exploratory.py`), 
cutting down to just the relevant authorities.

The `london_deprivation.csv` was found at https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019. 
File 1 was downloaded and the second tab saved as a csv.

## Structure
Ingestion and manipulation is done in `ingest.py`, while plotting is in `plotting.py`. Constants used across multiple
files can be found in `constants.py`.

To generate the static charts used in the presentation, run `python main.py`.

To kickstart the streamlit app (the MVP) run `streamlit run bike_app.py`.

## Notes
This was a very quick hack. Along with considering more metrics, here are some areas for improvement:

* Better validation. Very basic validation checks have been added in, but more should be done, particularly when pulling from the API (check the response status and data types, for example)
* Tests. No unit or integration tests have been added -- ideally, these would be for a finished product.
* Peer review. Only I have looked at this (as expected for a technical exercise...), but a full product would be reviewed.
* Dockerisation. To help ensure reproducibility, the MVP at least should be containerised.
* Linting. I have run linters on the code but not added an explicit check.
* Better styling. Both the charts and presentation could do with some aesthetic tweaks!

Possible expansions of the MVP:

* Allow a fuller list of metrics to be viewed. In this case, it may make sense to do the API calls as the chart is generated, not at the top of the script.
* Cache some data. This should improve performance.
* More pages can be added as further data is included.