import csv


def read_csv(filepath):
    """
    Reads a CSV file using csv.DictReader and returns a list of dictionaries.
    Handles FileNotFoundError with a clear error message.
    """
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
            return data
    except FileNotFoundError:
        print(f"[EduLearn ERROR] File not found: {filepath}")
        return []


def validate_not_null(data, column):
    """
    Checks if any row has None or empty string in the given column.
    Returns a dictionary with column name, null count, and validity.
    """
    null_count = 0

    for row in data:
        value = row.get(column)
        if value is None or value == "":
            null_count += 1

    return {
        "column": column,
        "null_count": null_count,
        "valid": null_count == 0
    }


def count_duplicates(data, key_column):
    """
    Counts duplicate values in the given key column.
    Returns the count of duplicates.
    """
    seen = set()
    duplicate_count = 0

    for row in data:
        key = row.get(key_column)

        if key in seen:
            duplicate_count += 1
        else:
            seen.add(key)

    return duplicate_count


def log_summary(table_name, row_count, null_report, dup_count):
    """
    Prints a formatted summary of the dataset.
    """
    print(
        f"[EduLearn] {table_name} | rows: {row_count} | "
        f"nulls in {null_report['column']}: {null_report['null_count']} | "
        f"duplicates: {dup_count}"
    )

if __name__ == "__main__":
    file_path = "data/enrollments.csv"

    data = read_csv(file_path)
    row_count = len(data)
    null_report = validate_not_null(data, "enrollment_id")
    dup_count = count_duplicates(data, "enrollment_id")
    log_summary("enrollments", row_count, null_report, dup_count)