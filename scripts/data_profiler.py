import pandas as pd
import sys
import os

# Allow import of team2_edulearn_utils from same /scripts/ folder
sys.path.append(os.path.dirname(__file__))
from team2_edulearn_utils import log_summary

# ── File configuration ────────────────────────────────────────────────────────
FILES = [
    {"file": "data/enrollments.csv",        "key_column": "enrollment_id"},
    {"file": "data/customers.csv",           "key_column": "customer_id"},
    {"file": "data/courses.csv",             "key_column": "course_id"},
    {"file": "data/enrollment_items.csv",    "key_column": "item_id"},
    {"file": "data/completions.csv",         "key_column": "completion_id"},
]

def profile_file(file_path, key_column):
    """
    Profiles a single CSV file using pandas.
    Prints row count, column count, null counts, and duplicate key count.

    Args:
        file_path (str): Path to the CSV file.
        key_column (str): Primary key column to check for duplicates.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"[EduLearn] ERROR: File not found → {file_path}")
        return

    file_name = os.path.basename(file_path)
    row_count  = len(df)
    col_count  = len(df.columns)

    # Null counts using list comprehension
    null_counts = {
        col: int(df[col].isnull().sum())
        for col in df.columns
        if df[col].isnull().sum() > 0
    }
    null_str = ', '.join(
        [f"{col}: {cnt}" for col, cnt in null_counts.items()]
    ) if null_counts else "None"

    # Duplicate key count
    dup_count = int(df.duplicated(subset=[key_column]).sum())

    # Data types summary
    dtype_str = ', '.join([f"{col}: {str(dtype)}" for col, dtype in df.dtypes.items()])

    print(f"\nFile: {file_name}")
    print(f"Rows: {row_count} | Columns: {col_count}")
    print(f"Null counts: {null_str}")
    print(f"Duplicate key ({key_column}): {dup_count} duplicates found")
    print(f"Data types: {dtype_str}")

    # Call log_summary from team2_edulearn_utils
    null_report = {
        'column': key_column,
        'null_count': int(df[key_column].isnull().sum()),
        'valid': df[key_column].isnull().sum() == 0
    }
    log_summary(file_name, row_count, null_report, dup_count)


if __name__ == '__main__':
    print("=" * 60)
    print("  [EduLearn] Data Profiler — Team 2")
    print("=" * 60)
    for config in FILES:
        profile_file(config["file"], config["key_column"])
    print("\n[EduLearn] Profiling complete.")
