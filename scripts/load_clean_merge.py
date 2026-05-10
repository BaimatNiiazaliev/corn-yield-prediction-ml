import pandas as pd
# This script loads, cleans, and merges the climate and yield data for the final project.
def load_data(files):
    dfs = [pd.read_csv(f) for f in files]
    return dfs


# Clean the yield data by filtering for rows that contain "YIELD" in the "Data Item" column, renaming columns, removing commas from the "Value" column, converting it to numeric, and creating a "GEOID" column by combining "State ANSI" and "County ANSI".
def clean_yield(df):
    df = df[df["Data Item"].str.contains("YIELD", case=False)]
    
    df = df.rename(columns={
        "Year": "year",
        "Value": "yield"
    })
    
    df["yield"] = df["yield"].astype(str).str.replace(",", "")
    df["yield"] = pd.to_numeric(df["yield"], errors="coerce")

    df = df[df["County ANSI"].notna()]

    df["State ANSI"] = df["State ANSI"].astype(int).astype(str).str.zfill(2)
    df["County ANSI"] = df["County ANSI"].astype(int).astype(str).str.zfill(3)

    df["GEOID"] = df["State ANSI"] + df["County ANSI"]

    return df[["GEOID", "year", "yield"]]


# Clean the climate data by renaming columns, converting the "year" column to numeric, and creating a "GEOID" column by combining "STATEFP" and "COUNTYFP".
def merge_data(climate, yield_df):
    climate["GEOID"] = climate["GEOID"].astype(str)
    yield_df["GEOID"] = yield_df["GEOID"].astype(str)

    final = climate.merge(yield_df, on=["GEOID", "year"], how="inner")
    return final


