[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20114056.svg)](https://doi.org/10.5281/zenodo.20114056)

# Final Project – Climate & Corn Yield Analysis

## Overview

This project analyzes how climate variables affect corn yield across US Corn Belt counties.
We combine high-resolution climate data from TerraClimate with county-level yield data from USDA to explore both linear and nonlinear relationships.

The workflow is fully reproducible and includes data retrieval, preprocessing, modeling, and visualization.

---

## Research Question

How do climate variables (e.g., temperature and water availability) affect crop yield, and do these relationships differ between annual and seasonal aggregations?

---

## Data Sources

### 1. Climate Data (TerraClimate)

Source: https://climate.northwestknowledge.net/TERRACLIMATE-DATA/

High-resolution gridded climate data aggregated to the county level.

#### Variables:

* Temperature: `tmax`, `tmin`
* Water availability: `ppt`, `aet`, `soil`
* Stress indicators: `vpd`, `def`, `pet`

---

### 2. Yield Data (USDA NASS QuickStats)

Source: https://quickstats.nass.usda.gov/

County-level corn yield data (bushels per acre).

#### Filters used:

* Commodity: Corn
* Data Item: Yield (BU / ACRE)
* Geographic Level: County
* States: IA, IL, IN, NE, MN (Corn Belt)
* Years: 1990–2024

#### How to reproduce:

1. Go to the QuickStats website
2. Apply the filters listed above
3. Click "Get Data"
4. Download as CSV
5. Save as:

```
data/corn_yields.csv
```

**Note:** This dataset is included in the repository.

---

## Project Structure

```
final_project/
├── data/              # raw and processed data
├── scripts/           # data pipeline and modeling
│   ├── run.py
│   ├── data_retrieving.py
│   ├── data_retrieving_seasonal.py
│   ├── load_clean_merge.py
│   ├── ML.py
├── notebooks/
│   └── final_project.qmd
├── results/
└── job_scripts/
```

---

## Pipeline Overview

The project follows this workflow:

1. Data retrieval:

   * Climate data is downloaded via scripts
   * Yield data is obtained from USDA

2. Data processing:

   * `scripts/load_clean_merge.py` cleans and merges datasets

3. Modeling:

   * `scripts/ML.py` trains:

     * Random Forest
     * Linear Regression
   * Uses **year-based cross-validation** (no data leakage)

4. Outputs:

   * `results/model_results.csv`
   * `results/summary.csv`

5. Analysis:

   * Visualized in `notebooks/final_project.qmd`

---

## Data Retrieval Pipeline

Climate data is fully reproducible.

Run:

```
python scripts/run.py
```

This will:

1. Download TerraClimate data (1990–2024)
2. Extract county-level values
3. Generate:

   * `data/cornbelt_climate_1990_2024.csv`
   * `data/cornbelt_climate_seasonal_1990_2024.csv`

Seasonal data includes only April–October (growing season).

---

## How to Reproduce the Project

### Step 1: Ensure yield data exists

Either:

* Use included file: `data/corn_yields.csv`
  OR
* Download from USDA (see instructions above)

---

### Step 2: Run data pipeline

```
python scripts/run.py
```

---

### Step 3: Train models

```
python scripts/ML.py
```

---

### Step 4: Render analysis

```
quarto render notebooks/final_project.qmd
```

---

## Running on CRC (Optional)

The project can also be run on the CRC cluster.

Submit job:

```
qsub job_scripts/submit_python_job.sh
```

### Job details:

* Uses conda environment: `dsip_lab4`
* Uses 10 CPU cores
* Runs: `scripts/ML.py`

---

## Key Methodological Choices

* **Detrending yield** to remove technological progress
* **Seasonal vs annual comparison**
* **Nonlinear exploration** (binned plots)
* **Year-based cross-validation** to mimic real forecasting

---

## Results Summary

* Linear Regression slightly outperforms Random Forest
* Overall performance is moderate (R² ≈ 0.4)
* Climate explains part of yield variation, but not all

---

## Limitations

* Aggregated data may mask extreme events
* No explicit spatial modeling
* Missing variables (soil quality, management, technology)

---

## Reproducibility

All steps are fully reproducible:

```
python scripts/run.py
python scripts/ML.py
quarto render notebooks/final_project.qmd
```

This repository is fully reproducible.
