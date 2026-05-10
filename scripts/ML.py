import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

# ===== Paths =====
# This script performs machine learning modeling to predict crop yields based on climate variables and engineered features. It uses a year-based cross-validation approach to evaluate model performance and saves the results and feature importance plots to the results directory.
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE, "data", "final_seasonal.csv")
results_path = os.path.join(BASE, "results")

os.makedirs(results_path, exist_ok=True)

# ===== Load data =====
final = pd.read_csv(data_path)

# ===== Feature engineering  =====
# Create a detrended yield variable by removing the annual mean to focus on climate-driven variation.
final = final.sort_values(["GEOID", "year"])

# Lag features
# Create lagged yield features to capture temporal dependencies. Lag 1 and Lag 2 represent the yield from the previous year and two years ago, respectively.
final["yield_lag1"] = final.groupby("GEOID")["yield_detrended"].shift(1)
final["yield_lag2"] = final.groupby("GEOID")["yield_detrended"].shift(2)

# Rolling mean
# Create a rolling mean of the detrended yield over the past 3 years (excluding the current year) to capture longer-term trends and smooth out short-term fluctuations.
final["yield_roll3"] = (
    final.groupby("GEOID")["yield_detrended"]
    .shift(1)   # exclude current year to prevent leakage
    .rolling(3)
    .mean()
)

# Time trend
# Normalize the year variable to capture any remaining time trends in the data. This can help the model account for technological progress or other temporal factors that may influence yields.
final["year_norm"] = final["year"] - final["year"].min()

# Interaction features
# Create interaction features between key climate variables to capture potential synergistic effects. For example, the interaction between maximum temperature and precipitation may be important for understanding heat stress under different moisture conditions.
final["tmax_x_ppt"] = final["tmax"] * final["ppt"]
final["vpd_x_aet"] = final["vpd"] * final["aet"]

# Drop missing values from lagging
# The lag and rolling features introduce NaN values for the first few years of each GEOID. We drop these rows to ensure a clean dataset for modeling.
final = final.dropna()

# ===== Features =====
# Define the list of features to be used in the modeling. This includes the original climate variables, engineered lag and rolling features, normalized year, and interaction terms.
features = [
    "tmax", "tmin", "aet", "ppt", "vpd", "def",
    "yield_lag1", "yield_lag2", "yield_roll3", "year_norm", "tmax_x_ppt", "vpd_x_aet"
]

years = sorted(final["year"].unique())

from sklearn.metrics import mean_absolute_error, mean_squared_error


# ===== Metrics storage =====
rf_scores = []
rf_mae = []
rf_rmse = []

lin_scores = []
lin_mae = []
lin_rmse = []


# ===== Year-based CV =====
for i in range(10, len(years)-1):
    train_years = years[:i]
    test_year = years[i]

    train = final[final["year"].isin(train_years)]
    test = final[final["year"] == test_year]

    X_train = train[features]
    y_train = train["yield_detrended"]

    X_test = test[features]
    y_test = test["yield_detrended"]

    # ===== Random Forest =====
    rf = RandomForestRegressor(
        n_estimators=600,
        max_depth=8,
        min_samples_leaf=5,
        n_jobs=10,
        random_state=42
    )
    rf.fit(X_train, y_train)

    rf_pred = rf.predict(X_test)

    rf_scores.append(rf.score(X_test, y_test))
    rf_mae.append(mean_absolute_error(y_test, rf_pred))
    rf_rmse.append(np.sqrt(mean_squared_error(y_test, rf_pred)))


    # ===== Linear Regression =====
    lin = LinearRegression()
    lin.fit(X_train, y_train)

    lin_pred = lin.predict(X_test)

    lin_scores.append(lin.score(X_test, y_test))
    lin_mae.append(mean_absolute_error(y_test, lin_pred))
    lin_rmse.append(np.sqrt(mean_squared_error(y_test, lin_pred)))

# ===== PRINT RESULTS =====
print("\n=== Random Forest ===")
print("R²:", rf_scores)
print("Mean R²:", np.mean(rf_scores))
print("Mean MAE:", np.mean(rf_mae))
print("Mean RMSE:", np.mean(rf_rmse))

print("\n=== Linear Regression ===")
print("R²:", lin_scores)
print("Mean R²:", np.mean(lin_scores))
print("Mean MAE:", np.mean(lin_mae))
print("Mean RMSE:", np.mean(lin_rmse))


# ===== SAVE FULL RESULTS =====
results = pd.DataFrame({
    "rf_r2": rf_scores,
    "rf_mae": rf_mae,
    "rf_rmse": rf_rmse,
    "lin_r2": lin_scores,
    "lin_mae": lin_mae,
    "lin_rmse": lin_rmse
})

results.to_csv(os.path.join(results_path, "model_results.csv"), index=False)


# ===== SAVE SUMMARY =====
summary = pd.DataFrame({
    "model": ["Random Forest", "Linear Regression"],
    "R2": [np.mean(rf_scores), np.mean(lin_scores)],
    "MAE": [np.mean(rf_mae), np.mean(lin_mae)],
    "RMSE": [np.mean(rf_rmse), np.mean(lin_rmse)]
})

summary.to_csv(os.path.join(results_path, "summary.csv"), index=False)

print("\nSaved: model_results.csv and summary.csv")

all_preds = []

df_preds = pd.DataFrame({
    "year": test["year"],
    "y_true": y_test,
    "rf_pred": rf_pred,
    "lin_pred": lin_pred
})

all_preds.append(df_preds)

preds_df = pd.concat(all_preds)

preds_df.to_csv(os.path.join(results_path, "predictions.csv"), index=False)