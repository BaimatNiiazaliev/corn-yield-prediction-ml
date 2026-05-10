# This script retrieves annual climate data for Corn Belt counties from TerraClimate.
# The script uses multiprocessing to speed up the retrieval and processing of data for multiple years.
# The script is designed to be run as part of a larger pipeline, as indicated by its import in `run.py`.
# TerraClimate provides high-resolution climate data
# 
def process_year(year, lats, lons, geoids, DATA_PATH):
    import xarray as xr
    import pandas as pd
    import numpy as np
    import os
    import urllib.request
    from os.path import join as oj
# The script retrieves the following climate variables: precipitation (ppt), maximum temperature (tmax), minimum temperature (tmin), soil moisture (soil), actual evapotranspiration (aet), vapor pressure deficit (vpd), drought index (def), and potential evapotranspiration (pet).

    variables = ["ppt", "tmax","tmin","soil","aet","vpd","def","pet"]

    yearly_df = pd.DataFrame({
        "GEOID": geoids,
        "year": year
    })

    for var in variables:
        filename = oj(DATA_PATH, f"TerraClimate_{var}_{year}.nc")
# # The script handles potential issues with data retrieval and processing, such as missing files or variables, by using try-except blocks and filling in NaN values when necessary.

        # download if not exists
        if not os.path.exists(filename):
            url = f"https://climate.northwestknowledge.net/TERRACLIMATE-DATA/TerraClimate_{var}_{year}.nc"
            try:
                print(f"Downloading {var} {year}")
                urllib.request.urlretrieve(url, filename)
            except Exception as e:
                print(f"Download failed {var} {year}: {e}")
                yearly_df[var] = np.nan
                continue

        try:
            ds = xr.open_dataset(filename)
            if var not in ds:
                print(f"{var} not found in dataset {year}")
                yearly_df[var] = np.nan
                ds.close()
                continue

            data = ds[var].sel(
                lat=xr.DataArray(lats, dims="points"),
                lon=xr.DataArray(lons, dims="points"),
                method="nearest"
            )

            # aggregate over time: mean for temperature and soil, sum for others
            if var in ["tmax", "tmin", "soil", "vpd"]:
                values = data.mean(dim="time").values
            else:
                values = data.sum(dim="time").values

            yearly_df[var] = values
            ds.close()

        except Exception as e:
            print(f"Processing failed {var} {year}: {e}")
            yearly_df[var] = np.nan

    print(f"Finished {year}")
    return yearly_df

# The main function `run_pipeline()` orchestrates the entire process, from reading county data to saving the final CSV file.

def run_pipeline():
    import os
    from os.path import join as oj
    import geopandas as gpd
    import pandas as pd
    import numpy as np
    from multiprocessing import Pool, cpu_count

    DATA_PATH = "data"
    os.makedirs(DATA_PATH, exist_ok=True)

    # -----------------------------
    # counties
    # -----------------------------
    counties = gpd.read_file(oj(DATA_PATH, "cb_2018_us_county_500k.shp"))

    corn_states = ["19","17","18","31","27"]
    corn_counties = counties[counties["STATEFP"].isin(corn_states)]

    corn_counties = corn_counties[["GEOID","NAME","STATEFP","geometry"]]
# centroids are calculated for each county to determine the representative latitude and longitude for data retrieval from TerraClimate.

    # centroids
    corn_proj = corn_counties.to_crs(epsg=5070)
    centroids = corn_proj.geometry.centroid
    centroids = gpd.GeoSeries(centroids, crs=5070).to_crs(epsg=4326)

    corn_counties["lon"] = centroids.x
    corn_counties["lat"] = centroids.y

    # TerraClimate

    lats = corn_counties["lat"].values
    lons = corn_counties["lon"].values
    geoids = corn_counties["GEOID"].values

    # -----------------------------
    # multiprocessing
    # -----------------------------
    years = list(range(1990, 2025))

    # N of cores
    n_cores = min(6, cpu_count())

    print(f"Running on {n_cores} cores")

    with Pool(n_cores) as p:
        results = p.starmap(
            process_year,
            [(year, lats, lons, geoids, DATA_PATH) for year in years]
        )

    # -----------------------------
    # combine results
    # -----------------------------
    climate = pd.concat(results, ignore_index=True)

    # scale temperature
    climate["tmax"] /= 10
    climate["tmin"] /= 10

    # save
    output_file = oj(DATA_PATH, "cornbelt_climate_1990_2024.csv")
    climate.to_csv(output_file, index=False)

    print("Saved:", output_file)
    print("Done")