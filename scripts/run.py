from data_retrieving import run_pipeline as run_annual
from data_retrieving_seasonal import run_pipeline as run_seasonal

if __name__ == "__main__":
    print("Running annual...")
    run_annual()

    print("Running seasonal...")
    run_seasonal()