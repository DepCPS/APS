import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta, time


def find_filenames(path, suffix=".csv"):
    """Return a list of CSV files in the given path (recursive)."""
    fileset = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(suffix):
                fileresult = os.path.join(root, file)
                fileset.append(fileresult)
    return fileset


def readtracefile(filename):
    """Simple wrapper to read a CSV into Pandas."""
    data = pd.read_csv(filename, index_col=False)
    return data


def extract_data(src_dir, parent_dir):
    """
    This function merges CGM (df_BG) and pump record data (df_rate).
    It outputs day-partitioned CSV files by patient, skipping data
    between 7:30 AM and 7:00 PM.
    """
    # Load data
    df_BG = readtracefile(os.path.join(src_dir, "combined_cgm.csv"))
    df_rate = readtracefile(os.path.join(src_dir, "pumprecord.csv"))

    # Strip whitespace from column names
    df_BG.columns = df_BG.columns.str.strip()
    df_rate.columns = df_rate.columns.str.strip()

    # Ensure 'rate' and 'carbs' columns are numeric
    df_rate["rate"] = pd.to_numeric(df_rate["rate"], errors="coerce").fillna(0)
    df_rate["carbs"] = pd.to_numeric(df_rate["carbs"], errors="coerce").fillna(0)
    df_rate["insulin"] = pd.to_numeric(df_rate["insulin"], errors="coerce").fillna(0)

    # Preprocess 'DataDtTm' column to handle mixed formats
    try:
        df_rate["DataDtTm"] = pd.to_datetime(df_rate["DataDtTm"], format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")
        df_rate["DataDtTm"].fillna(pd.to_datetime(df_rate["DataDtTm"], format="%Y-%m-%d %H:%M:%S", errors="coerce"), inplace=True)
    except Exception as e:
        print(f"Error while parsing 'DataDtTm' column: {e}")
        raise

    # Ensure all timestamps in 'DataDtTm' are parsed correctly
    if df_rate["DataDtTm"].isna().any():
        print("Warning: Some timestamps in 'DataDtTm' could not be parsed. They will be ignored.")
        df_rate = df_rate.dropna(subset=["DataDtTm"])

    # Skip BG data in [7:30 AM, 7:00 PM]
    t730am = time(7, 30, 0)
    t7pm = time(19, 0, 0)

    current_patient = None
    current_date = None
    day = 1
    fp_patient = None
    skipped_rows = 0

    # Iterate through BG data
    for i in df_BG.index:
        # Extract CGM record
        BG_patient = int(df_BG["DeidentID"][i])
        BG_time_str = df_BG["DataDtTm"][i]
        BG_val = df_BG["CGM"][i]
        rec_id = df_BG["RecID"][i]

        # Parse BG timestamp
        try:
            t_BG = datetime.strptime(BG_time_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            t_BG = datetime.strptime(BG_time_str, "%Y-%m-%d %H:%M:%S")

        # Handle patient switching
        if BG_patient != current_patient:
            # Close previous file, if any
            if fp_patient is not None:
                fp_patient.close()

            # Reset variables for the new patient
            current_patient = BG_patient
            day = 1
            current_date = t_BG.date()

            # Filter df_rate for the current patient
            patient_rate_data = df_rate[df_rate["DeidentID"] == current_patient]

            # Debug: Ensure patient data exists
            if patient_rate_data.empty:
                print(f"No pump records found for patient {current_patient}. Skipping.")
                continue

            # Create directory for the patient
            save_dir = os.path.join(parent_dir, f"patient{current_patient}")
            os.makedirs(save_dir, exist_ok=True)

            # Open new file for the patient
            fp_patient = open(os.path.join(save_dir, f"data_patient{current_patient}_day{day}.csv"), 'w')
            fp_patient.write("patient,RecID,Time,CGM_glucose,rate,Carbs\n")

        # Handle day changes
        if current_date is None or t_BG.date() != current_date:
            current_date = t_BG.date()
            day += 1
            if fp_patient is not None:
                fp_patient.close()
            save_dir = os.path.join(parent_dir, f"patient{current_patient}")
            fp_patient = open(os.path.join(save_dir, f"data_patient{current_patient}_day{day}.csv"), 'w')
            fp_patient.write("patient,RecID,Time,CGM_glucose,rate,Carbs\n")

        # Skip daytime BG records
        if t730am < t_BG.time() < t7pm:
            skipped_rows += 1
            continue

        # Accumulate insulin rate and carbs
        rate = 0.0
        carbs = 0.0

        # Find matching pump records within ±10 minutes
        matching_records = patient_rate_data[
            (patient_rate_data["DataDtTm"] >= t_BG - timedelta(minutes=10)) &
            (patient_rate_data["DataDtTm"] <= t_BG + timedelta(minutes=10))
        ]

        # Accumulate rate and carbs from matching records
        for _, row in matching_records.iterrows():
            rate += row["rate"] / 12.0 if row["rate"] > 0 else 0
            carbs += row["carbs"] if row["carbs"] > 0 else 0

            # Debug: Print accumulation process
            print(f"Matched! BG time: {t_BG}, Pump time: {row['DataDtTm']}, Adding rate: {row['rate'] / 12.0}, carbs: {row['carbs']}")

        # Write the result to the patient file
        fp_patient.write(f"{current_patient},{rec_id},{BG_time_str},{BG_val},{rate},{carbs}\n")

    # Close the last file
    if fp_patient is not None:
        fp_patient.close()

    print(f"Total rows skipped due to time condition: {skipped_rows}")
    return 0




if __name__ == "__main__":
    src_dir = "/Users/liuyushen/Desktop/BG Prediction/data/openAPS_data/"
    dest_dir = "/Users/liuyushen/Desktop/BG Prediction/data/openAPS_data/"
    extract_data(src_dir, dest_dir)
    print("Done!")