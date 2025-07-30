import csv
import os
import time
from functools import wraps


def log_performance_to_csv(file_name, function_name, runtime, implementation_type):
    """Log performance data to a CSV file."""
    file_exists = os.path.isfile(file_name)
    headers = ["function_name", "runtime", "Implementation Type"]
    existing_rows = []  # Initialize as an empty list to avoid UnboundLocalError

    if file_exists:
        # Open the file in read mode to check for duplicates
        with open(file_name, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            if "Implementation Type" in reader.fieldnames:
                # Load existing rows for deduplication
                existing_rows = list(reader)

    # Avoid duplicate rows
    if any(row["Implementation Type"] == implementation_type for row in existing_rows):
        print(f"Row with Implementation Type '{implementation_type}' already exists. Skipping write.")
        return

    # Append new row to the CSV
    with open(file_name, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "function_name": function_name,
            "runtime": runtime,
            "Implementation Type": implementation_type,
        })


def measure_runtime_and_log_to_csv(implementation_type, file_name="performance_table.csv"):
    """Decorator to measure function runtime and log it to a CSV file."""

    def decorator(test_function):
        @wraps(test_function)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            result = test_function(*args, **kwargs)

            end_time = time.time()
            runtime = end_time - start_time

            log_performance_to_csv(file_name, test_function.__name__, runtime, implementation_type)

            return result

        return wrapper

    return decorator
