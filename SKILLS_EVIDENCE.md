# Skills Evidence

**Name:** Team 2
**Batch:** Sigmoid Bengaluru 2026
**GitHub Repo:** https://github.com/Tejpalsingh9/team2-edulearn-data-platform

---

## Section 1 — Python (15 marks)

### Q1. team2_edulearn_utils.py — Full file (Block 1)

```python
import csv

def read_csv(filepath):
    """
    Reads a CSV file using csv.DictReader and returns a list of dicts.
    Handles FileNotFoundError with a clear error message.
    Args:
        filepath (str): Path to the CSV file.
    Returns:
        list: A list of dictionaries, one per row.
    """
    try:
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        return data
    except FileNotFoundError:
        print(f"[EduLearn] ERROR: File not found → {filepath}")
        return []
    except Exception as e:
        print(f"[EduLearn] ERROR reading {filepath}: {str(e)}")
        return []


def validate_not_null(data, column):
    """
    Checks if any row has None or empty string in the given column.
    Args:
        data (list): List of dicts (output of read_csv).
        column (str): Column name to check for nulls.
    Returns:
        dict: {'column': col, 'null_count': n, 'valid': bool}
    """
    null_count = sum(
        1 for row in data
        if row.get(column) is None or str(row.get(column, '')).strip() == ''
    )
    return {
        'column': column,
        'null_count': null_count,
        'valid': null_count == 0
    }


def count_duplicates(data, key_column):
    """
    Counts duplicate values in key_column.
    Args:
        data (list): List of dicts (output of read_csv).
        key_column (str): Column name to check for duplicates.
    Returns:
        int: Count of duplicate rows (total rows minus unique values).
    """
    values = [row.get(key_column) for row in data if row.get(key_column)]
    unique_values = set(values)
    return len(values) - len(unique_values)


def log_summary(table_name, row_count, null_report, dup_count):
    """
    Prints a formatted summary for a dataset.
    Args:
        table_name (str): Name of the table or file.
        row_count (int): Total number of rows.
        null_report (dict): Output from validate_not_null().
        dup_count (int): Output from count_duplicates().
    """
    column = null_report['column']
    nulls = null_report['null_count']
    print(
        f"[EduLearn] {table_name} | "
        f"rows: {row_count} | "
        f"nulls in {column}: {nulls} | "
        f"duplicates: {dup_count}"
    )


def bronze_validator(df, table_name, key_column, expected_columns):
    """
    Validates a Spark DataFrame after Bronze ingestion.
    Checks row count, null %, schema, and metadata columns.
    Args:
        df: Spark DataFrame.
        table_name (str): Name of the Bronze table being validated.
        key_column (str): Primary key column to check for nulls.
        expected_columns (list): List of expected column names.

    Returns:
        dict: Results with pass/fail for each check.
    """
    results = {}

    # Check 1: Row count > 0
    row_count = df.count()
    results['row_count'] = 'pass' if row_count > 0 else 'fail'
    print(f"[EduLearn Bronze Validator] {table_name}")
    print(f"  ✔ row_count       : {row_count} → {results['row_count'].upper()}")

    # Check 2: Null % on key_column < 5%
    from pyspark.sql.functions import col, isnan, when, count
    null_count = df.filter(
        col(key_column).isNull() | (col(key_column) == '')
    ).count()
    null_pct = (null_count / row_count * 100) if row_count > 0 else 100
    results['null_check'] = 'pass' if null_pct < 5 else 'fail'
    results['null_count'] = null_count
    print(f"  ✔ null_check      : {null_count} nulls in {key_column} "
          f"({null_pct:.2f}%) → {results['null_check'].upper()}")

    # Check 3: All expected columns present
    missing = [c for c in expected_columns if c not in df.columns]
    results['schema_check'] = 'pass' if not missing else 'fail'
    results['missing_columns'] = missing
    print(f"  ✔ schema_check    : missing={missing} → {results['schema_check'].upper()}")

    # Check 4: Metadata columns present
    metadata_cols = ['_source', '_ingest_ts', '_file_name', '_run_id']
    meta_missing = [c for c in metadata_cols if c not in df.columns]
    results['metadata_check'] = 'pass' if not meta_missing else 'fail'
    print(f"  ✔ metadata_check  : missing={meta_missing} → {results['metadata_check'].upper()}")

    return results


# ── Main block: test all 4 functions on enrollments.csv ──────────────────────
if __name__ == '__main__':
    filepath = 'data/enrollments.csv'

    data = read_csv(filepath)
    print(f"Loaded {len(data)} rows from {filepath}\n")

    null_report = validate_not_null(data, 'enrollment_id')
    print(f"Null report: {null_report}")

    dup_count = count_duplicates(data, 'enrollment_id')
    print(f"Duplicate enrollment_ids: {dup_count}")

    log_summary('enrollments', len(data), null_report, dup_count)
```

### Q2. data_profiler.py — Full file + sample output (Block 4)

```python
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
```

**Sample output from running the script:**

```
[EduLearn] enrollments.csv | rows: 503 | nulls in enrollment_id: 0 | duplicates: 0
[EduLearn] customers.csv   | rows: 100 | nulls in customer_id: 0   | duplicates: 0
...
```

### Q3. Producer/Sender class — Full class (Block 5)

```python
import boto3
import json
import csv
import random
import time
from datetime import datetime
from botocore.exceptions import ClientError


class EnrollmentEventProducer:
    """
    Reads EduLearn enrollment records from CSV and streams them to
    an Amazon Kinesis Data Stream one event at a time.
    Simulates real-time enrollment ingestion for the EduLearn platform.
    """

    CONFIG = {
        'stream_name'   : 'team2-edulearn-events-stream',
        'region'        : 'ap-south-1',
        'batch_size'    : 50,
        'delay_seconds' : 0.1
    }

    def __init__(self):
        """
        Initialises the boto3 Kinesis client and tracking counters.
        """
        self.kinesis_client = boto3.client(
            'kinesis',
            region_name=self.CONFIG['region']
        )
        self.sent   = 0
        self.failed = 0

    def build_event(self, row):
        """
        Takes a CSV row dict, enriches it with event_timestamp,
        and returns the JSON-encoded string ready to send to Kinesis.

        Args:
            row (dict): A row from csv.DictReader on enrollments.csv.

        Returns:
            str: JSON string representing the enrollment event.
        """
        event = dict(row)
        event['event_timestamp'] = datetime.utcnow().isoformat()
        event['ingest_date']     = datetime.utcnow().strftime("%Y-%m-%d")
        return json.dumps(event)

    def send_event(self, event_json):
        """
        Sends a single event to the configured Kinesis stream.
        On ClientError, increments self.failed and prints the error.
        On success, increments self.sent.

        Args:
            event_json (str): JSON string of the enrollment event.
        """
        try:
            event_data = json.loads(event_json)
            partition_key = event_data.get('enrollment_id', str(random.randint(1000, 9999)))
            self.kinesis_client.put_record(
                StreamName  = self.CONFIG['stream_name'],
                Data        = event_json,
                PartitionKey= partition_key
            )
            self.sent += 1
            print(f"[EduLearn] Sent: {partition_key} | city: {event_data.get('city')} "
                  f"| fees: ₹{event_data.get('total_fees')}")
        except ClientError as e:
            self.failed += 1
            print(f"[EduLearn] Failed: {str(e)}")

    def run(self, csv_path):
        """
        Reads enrollments.csv row by row using csv.DictReader,
        calls build_event + send_event up to CONFIG batch_size rows,
        sleeps CONFIG delay_seconds between sends, and prints final summary.

        Args:
            csv_path (str): Path to the enrollments CSV file.
        """
        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= self.CONFIG['batch_size']:
                        break
                    event_json = self.build_event(row)
                    self.send_event(event_json)
                    time.sleep(self.CONFIG['delay_seconds'])
        except FileNotFoundError:
            print(f"[EduLearn] ERROR: File not found → {csv_path}")

        print(f"\n[EduLearn] Summary: Sent={self.sent} | Failed={self.failed}")


if __name__ == '__main__':
    producer = EnrollmentEventProducer()
    producer.run('data/enrollments.csv')
```

### Q4. bronze_validator() function + sample output (Block 7)

```python
def bronze_validator(df, table_name, key_column, expected_columns):
    """
    Validates a Bronze Delta table DataFrame.
    Checks: row count, null %, schema completeness, metadata columns.
    """
    results = {}
    row_count = df.count()
    results['row_count'] = 'pass' if row_count > 0 else 'fail'
    print(f"\n[EduLearn Bronze Validator] ── {table_name} ──")
    print(f"  row_count       : {row_count} → {results['row_count'].upper()}")

    null_count = df.filter(
        F.col(key_column).isNull() | (F.col(key_column) == '')
    ).count()
    null_pct = (null_count / row_count * 100) if row_count > 0 else 100
    results['null_check'] = 'pass' if null_pct < 5 else 'fail'
    results['null_count'] = null_count
    print(f"  null_check      : {null_count} nulls in '{key_column}' "
          f"({null_pct:.2f}%) → {results['null_check'].upper()}")

    missing = [c for c in expected_columns if c not in df.columns]
    results['schema_check'] = 'pass' if not missing else 'fail'
    results['missing_columns'] = missing
    print(f"  schema_check    : missing={missing} → {results['schema_check'].upper()}")

    metadata_cols = ['_source', '_ingest_ts', '_file_name', '_run_id']
    meta_missing = [c for c in metadata_cols if c not in df.columns]
    results['metadata_check'] = 'pass' if not meta_missing else 'fail'
    print(f"  metadata_check  : missing_meta={meta_missing} → {results['metadata_check'].upper()}")

    return results

# Run on enrollments_bronze
df_e = spark.read.table(f"{YOUR_DB}.enrollments_bronze")
results_e = bronze_validator(
    df_e,
    table_name="enrollments_bronze",
    key_column="enrollment_id",
    expected_columns=["enrollment_id", "customer_id", "order_date", "total_fees", "enrollment_status", "city"]
)
assert results_e['row_count'] == 'pass', "FAIL: enrollments_bronze is empty!"

# Run on customers_bronze
df_c = spark.read.table(f"{YOUR_DB}.customers_bronze")
results_c = bronze_validator(
    df_c,
    table_name="customers_bronze",
    key_column="customer_id",
    expected_columns=["customer_id", "name", "city", "signup_date", "email"]
)
assert results_c['row_count'] == 'pass', "FAIL: customers_bronze is empty!"
```

**Output when called on enrollments_bronze:**

```
[EduLearn Bronze Validator] ── enrollments_bronze ──
  row_count       : 503 → PASS
  null_check      : 0 nulls in 'enrollment_id' (0.00%) → PASS
  schema_check    : missing=[] → PASS
  metadata_check  : missing_meta=[] → PASS
```

---

## Section 2 — SQL (20 marks)

### Q4. Athena Advanced Queries — S1a, S1b, S1c (Block 3)

```sql
-- S1a: RANK() by total fees within each city
-- S1b: LAG() month-over-month enrollment trend
-- S1c: CTE — customers with 3+ enrollments and 1+ COMPLETED
-- S1a:
SELECT
    customer_id,
    city,
    ROUND(SUM(total_fees), 2) AS total_fees,
    RANK() OVER (
        PARTITION BY city
        ORDER BY SUM(total_fees) DESC
    ) AS city_rank
FROM team2_edulearn_raw.enrollments
WHERE total_fees IS NOT NULL
GROUP BY customer_id, city
ORDER BY city, city_rank;

-- S1b: 
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', CAST(order_date AS DATE)) AS month,
        COUNT(*) AS enrollment_count
    FROM team2_edulearn_raw.enrollments
    WHERE order_date IS NOT NULL
    GROUP BY DATE_TRUNC('month', CAST(order_date AS DATE))
)
SELECT
    month,
    enrollment_count,
    LAG(enrollment_count) OVER (ORDER BY month) AS prev_month_count,
    enrollment_count - LAG(enrollment_count) OVER (ORDER BY month) AS change
FROM monthly
ORDER BY month;

-- S1c: 
WITH enrollment_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS total_enrollments,
        SUM(CASE WHEN UPPER(enrollment_status) = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_count
    FROM team2_edulearn_raw.enrollments
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_enrollments,
    completed_count
FROM enrollment_summary
WHERE total_enrollments > 3
  AND completed_count >= 1
ORDER BY total_enrollments DESC;
```

### Q5. Redshift Advanced Queries — S2a, S2b, S2c (Block 6)

```sql

-- S2a: DENSE_RANK — Rank instructors by average student rating per category
-- (Uses completions joined with courses)
WITH instructor_ratings AS (
    SELECT
        co.instructor,
        co.category,
        ROUND(AVG(cp.rating)::NUMERIC, 2) AS avg_rating
    FROM team2_edulearn_db.public.completions cp
    JOIN team2_edulearn_db.public.enrollments e
        ON cp.enrollment_id = e.enrollment_id
    JOIN team2_edulearn_db.public.courses co
        ON co.course_id = co.course_id
    WHERE cp.rating IS NOT NULL
    GROUP BY co.instructor, co.category
),
ranked AS (
    SELECT
        instructor,
        category,
        avg_rating,
        DENSE_RANK() OVER (
            PARTITION BY category
            ORDER BY avg_rating DESC
        ) AS category_rank
    FROM instructor_ratings
)
SELECT instructor, category, avg_rating, category_rank
FROM ranked
WHERE category_rank <= 2
ORDER BY category, category_rank;

-- S2b: Correlated subquery — Learners whose total fees > city average
SELECT
    e.customer_id,
    cu.name,
    e.city,
    ROUND(SUM(e.total_fees)::NUMERIC, 2) AS total_fees,
    ROUND(
        (SELECT AVG(e2.total_fees)
         FROM team2_edulearn_db.public.enrollments e2
         WHERE e2.city = e.city
           AND e2.total_fees IS NOT NULL)::NUMERIC, 2
    ) AS city_avg_fees
FROM team2_edulearn_db.public.enrollments e
JOIN team2_edulearn_db.public.customers cu
    ON e.customer_id = cu.customer_id
WHERE e.total_fees IS NOT NULL
GROUP BY e.customer_id, cu.name, e.city
HAVING ROUND(SUM(e.total_fees)::NUMERIC, 2) >
    (SELECT AVG(e3.total_fees)
     FROM team2_edulearn_db.public.enrollments e3
     WHERE e3.city = e.city AND e3.total_fees IS NOT NULL)
ORDER BY e.city, total_fees DESC;

-- S2c: CASE WHEN — Fee bracket classification
SELECT
    CASE
        WHEN total_fees > 5000 THEN 'Premium'
        WHEN total_fees BETWEEN 2000 AND 5000 THEN 'Standard'
        WHEN total_fees < 2000 THEN 'Budget'
        ELSE 'Unknown'
    END AS fee_bracket,
    COUNT(enrollment_id)                  AS enrollment_count,
    ROUND(SUM(total_fees)::NUMERIC, 2)    AS total_fees_sum
FROM team2_edulearn_db.public.enrollments
WHERE total_fees IS NOT NULL
GROUP BY fee_bracket
ORDER BY total_fees_sum DESC;


```

### Q6. Silver CTE + Window Functions — S3a, S3b (Block 8)

```sql
-- S3a: Running total revenue per city by month
-- S3b: Top 3 learners per city by enrollment count

-- S3a: 
spark.sql(f"""
    WITH monthly_revenue AS (
        SELECT
            city,
            DATE_TRUNC('month', order_date) AS month,
            ROUND(SUM(total_fees), 2) AS monthly_revenue
        FROM {YOUR_DB}.enrollments_silver
        WHERE order_date IS NOT NULL AND total_fees IS NOT NULL
        GROUP BY city, DATE_TRUNC('month', order_date)
    )
    SELECT
        city,
        month,
        monthly_revenue,
        ROUND(SUM(monthly_revenue) OVER (
            PARTITION BY city
            ORDER BY month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2) AS running_total
    FROM monthly_revenue
    ORDER BY city, month
""").show(50)

-- S3b: 
spark.sql(f"""
    WITH customer_counts AS (
        SELECT
            customer_id,
            city,
            COUNT(*) AS enrollment_count
        FROM {YOUR_DB}.enrollments_silver
        GROUP BY customer_id, city
    ),
    ranked AS (
        SELECT
            customer_id,
            city,
            enrollment_count,
            RANK() OVER (
                PARTITION BY city
                ORDER BY enrollment_count DESC
            ) AS city_rank
        FROM customer_counts
    )
    SELECT customer_id, city, enrollment_count, city_rank
    FROM ranked
    WHERE city_rank <= 3
    ORDER BY city, city_rank
""").show()

```

### Q7. Gold CTE queries + Cohort Analysis — S4a, S4b (Block 9)

```sql
-- S4a: All 3 Gold table queries as CTEs
spark.sql(f"""
    CREATE OR REPLACE TABLE {GOLD_DB}.gold_city_revenue
    USING DELTA
    AS
    WITH cleaned AS (
        SELECT
            city,
            enrollment_id,
            total_fees
        FROM {YOUR_DB}.enrollments_silver
        WHERE city IS NOT NULL
          AND total_fees IS NOT NULL
    ),
    summary AS (
        SELECT
            city,
            COUNT(enrollment_id)        AS total_enrollments,
            ROUND(SUM(total_fees), 2)   AS total_fees_collected,
            ROUND(AVG(total_fees), 2)   AS avg_fee
        FROM cleaned
        GROUP BY city
    )
    SELECT * FROM summary
    ORDER BY total_fees_collected DESC
""")

display(spark.read.table(f"{GOLD_DB}.gold_city_revenue"))


spark.sql(f"""
    CREATE OR REPLACE TABLE {GOLD_DB}.gold_course_performance
    USING DELTA
    AS
    WITH enrollment_data AS (
        SELECT
            ei.course_id,
            c.course_name,
            c.category,
            e.completion_days,
            ei.final_fee
        FROM {YOUR_DB}.enrollments_silver e
        JOIN {YOUR_DB}.enrollment_items_silver ei
            ON e.enrollment_id = ei.enrollment_id
        JOIN {YOUR_DB}.courses_silver c
            ON ei.course_id = c.course_id
        WHERE ei.final_fee IS NOT NULL
    ),
    aggregated AS (
        SELECT
            course_id,
            course_name,
            category,
            COUNT(*)                          AS total_enrollments,
            ROUND(SUM(final_fee), 2)          AS total_revenue,
            ROUND(AVG(completion_days), 1)    AS avg_completion_days
        FROM enrollment_data
        GROUP BY course_id, course_name, category
    )
    SELECT * FROM aggregated
    ORDER BY total_revenue DESC
""")

display(spark.read.table(f"{GOLD_DB}.gold_course_performance"))


spark.sql(f"""
    CREATE OR REPLACE TABLE {GOLD_DB}.gold_completion_rate
    USING DELTA
    AS
    WITH city_data AS (
        SELECT
            city,
            COUNT(*)                                                 AS total_enrollments,
            SUM(CASE WHEN enrollment_status = 'COMPLETED' THEN 1
                     ELSE 0 END)                                     AS completed_count,
            ROUND(AVG(completion_days), 1)                           AS avg_completion_days
        FROM {YOUR_DB}.enrollments_silver
        WHERE city IS NOT NULL
        GROUP BY city
    )
    SELECT
        city,
        total_enrollments,
        completed_count,
        avg_completion_days,
        ROUND(completed_count * 100.0 / total_enrollments, 1) AS completion_rate_pct
    FROM city_data
    ORDER BY completion_rate_pct DESC
""")

display(spark.read.table(f"{GOLD_DB}.gold_completion_rate"))

-- S4b: Customer cohort acquisition analysis


spark.sql(f"""
    WITH first_enrollments AS (
        SELECT
            customer_id,
            DATE_TRUNC('month', MIN(order_date)) AS acquisition_month
        FROM {YOUR_DB}.enrollments_silver
        WHERE order_date IS NOT NULL
        GROUP BY customer_id
    ),
    latest_month AS (
        SELECT DATE_TRUNC('month', MAX(order_date)) AS max_month
        FROM {YOUR_DB}.enrollments_silver
        WHERE order_date IS NOT NULL
    ),
    active_in_latest AS (
        SELECT DISTINCT customer_id
        FROM {YOUR_DB}.enrollments_silver e, latest_month lm
        WHERE DATE_TRUNC('month', e.order_date) = lm.max_month
    )
    SELECT
        fe.acquisition_month,
        COUNT(fe.customer_id)                                                AS customers_acquired,
        COUNT(CASE WHEN al.customer_id IS NOT NULL THEN 1 END)               AS still_active
    FROM first_enrollments fe
    LEFT JOIN active_in_latest al ON fe.customer_id = al.customer_id
    GROUP BY fe.acquisition_month
    ORDER BY fe.acquisition_month
""").show(50)
```

---

## Section 3 — Spark & DE Concepts (10 marks)

### Q8. Execution Plan — .explain(True) output + explanation (Block 7)

```
== Parsed Logical Plan ==
'Project ['enrollment_id, 'customer_id, 'total_fees]
+- 'Filter '`==`('enrollment_status, COMPLETED)
   +- 'UnresolvedRelation [team2_edulearn, enrollments_bronze], [], false

== Analyzed Logical Plan ==
enrollment_id: string, customer_id: string, total_fees: string
Project [enrollment_id#9227, customer_id#9222, total_fees#9228]
+- Filter (enrollment_status#9230 = COMPLETED)
   +- SubqueryAlias de_workspace26.team2_edulearn.enrollments_bronze
      +- Relation de_workspace26.team2_edulearn.enrollments_bronze[customer_id#9222,order_date#9223,order_time#9224,payment_method#9225,city#9226,enrollment_id#9227,total_fees#9228,completion_days#9229,enrollment_status#9230,payment_status#9231,_source#9232,_ingest_ts#9233,_file_name#9234,_run_id#9235,ingest_date#9236] parquet

== Optimized Logical Plan ==
Project [enrollment_id#9227, customer_id#9222, total_fees#9228]
+- Filter (isnotnull(enrollment_status#9230) AND (enrollment_status#9230 = COMPLETED))
   +- Relation de_workspace26.team2_edulearn.enrollments_bronze[customer_id#9222,order_date#9223,order_time#9224,payment_method#9225,city#9226,enrollment_id#9227,total_fees#9228,completion_days#9229,enrollment_status#9230,payment_status#9231,_source#9232,_ingest_ts#9233,_file_name#9234,_run_id#9235,ingest_date#9236] parquet

== Physical Plan ==
*(1) Project [enrollment_id#9227, customer_id#9222, total_fees#9228]
+- *(1) Filter ((if (isnotnull(_databricks_internal_edge_computed_column_skip_row#9253)) (_databricks_internal_edge_computed_column_skip_row#9253 = false) else isnotnull(raise_error(DELTA_SKIP_ROW_COLUMN_NOT_FILLED, map(keys: [], values: []), NullType)) AND isnotnull(enrollment_status#9230)) AND (enrollment_status#9230 = COMPLETED))
   +- *(1) ColumnarToRow
      +- FileScan parquet de_workspace26.team2_edulearn.enrollments_bronze[customer_id#9222,enrollment_id#9227,total_fees#9228,enrollment_status#9230,_databricks_internal_edge_computed_column_skip_row#9253,ingest_date#9236] Batched: true, DataFilters: [isnotnull(enrollment_status#9230), (enrollment_status#9230 = COMPLETED)], Format: Parquet, Location: PreparedDeltaFileIndex(1 paths)[s3://databricks-storage-7474660560922927/unity-catalog/7474660560..., PartitionFilters: [], PushedFilters: [IsNotNull(enrollment_status), EqualTo(enrollment_status,COMPLETED)], ReadSchema: struct<customer_id:string,enrollment_id:string,total_fees:string,enrollment_status:string,_databr...

== Optimizer Statistics (table names per statistics state) ==
  missing = enrollments_bronze
  partial = 
  full    = 
Corrective actions: consider running the following command on all tables with missing or partial statistics
  ANALYZE TABLE <table-name> COMPUTE STATISTICS FOR ALL COLUMNS

```

**a. What does lazy evaluation mean? What triggered computation here?**

Lazy evaluation means Spark does not execute transformations immediately
when you write code — it builds a logical plan (DAG) and waits. Actual
computation is triggered only when an action is called. In this case,
calling .explain(True) shows the plan, but actual data processing would
be triggered by actions like .count(), .show(), or .collect(). Spark
defers execution to allow the optimizer to reorganize operations for
efficiency before any data moves.

**b. What does 'PushedFilters' in the physical plan tell you?**

PushedFilters means Spark has pushed the filter condition (enrollment_status
= 'COMPLETED') down to the data source level, so only matching rows are
read from Delta/Parquet files rather than reading all rows and filtering
in memory. This is called predicate pushdown and significantly reduces
the amount of data read from storage.

### Q9. Broadcast Join — explain output + explanation (Block 8)

```
== Parsed Logical Plan ==
'Join UsingJoin(LeftOuter, [course_id])
:- 'UnresolvedRelation [team2_edulearn, enrollment_items_silver], [], false
+- 'UnresolvedHint broadcast
   +- 'UnresolvedRelation [team2_edulearn, courses_silver], [], false

== Analyzed Logical Plan ==
course_id: string, item_id: string, enrollment_id: string, fee: double, discount_pct: double, final_fee: double, _source: string, _ingest_ts: string, _file_name: string, _run_id: string, ingest_date: date, processing_date: date, course_name: string, category: string, price: double, delivery_mode: string, instructor: string, available: string, _source: string, _ingest_ts: string, _file_name: string, _run_id: string, ingest_date: date, processing_date: date
Project [course_id#19524, item_id#19522, enrollment_id#19523, fee#19525, discount_pct#19526, final_fee#19527, _source#19528, _ingest_ts#19529, _file_name#19530, _run_id#19531, ingest_date#19532, processing_date#19533, course_name#19535, category#19536, price#19537, delivery_mode#19538, instructor#19539, available#19540, _source#19541, _ingest_ts#19542, _file_name#19543, _run_id#19544, ingest_date#19545, processing_date#19546]
+- Join LeftOuter, (course_id#19524 = course_id#19534)
   :- SubqueryAlias de_workspace26.team2_edulearn.enrollment_items_silver
   :  +- Relation de_workspace26.team2_edulearn.enrollment_items_silver[item_id#19522,enrollment_id#19523,course_id#19524,fee#19525,discount_pct#19526,final_fee#19527,_source#19528,_ingest_ts#19529,_file_name#19530,_run_id#19531,ingest_date#19532,processing_date#19533] parquet
   +- ResolvedHint (strategy=broadcast)
      +- SubqueryAlias de_workspace26.team2_edulearn.courses_silver
         +- Relation de_workspace26.team2_edulearn.courses_silver[course_id#19534,course_name#19535,category#19536,price#19537,delivery_mode#19538,instructor#19539,available#19540,_source#19541,_ingest_ts#19542,_file_name#19543,_run_id#19544,ingest_date#19545,processing_date#19546] parquet

== Optimized Logical Plan ==
Project [course_id#19524, item_id#19522, enrollment_id#19523, fee#19525, discount_pct#19526, final_fee#19527, _source#19528, _ingest_ts#19529, _file_name#19530, _run_id#19531, ingest_date#19532, processing_date#19533, course_name#19535, category#19536, price#19537, delivery_mode#19538, instructor#19539, available#19540, _source#19541, _ingest_ts#19542, _file_name#19543, _run_id#19544, ingest_date#19545, processing_date#19546]
+- Join LeftOuter, (course_id#19524 = course_id#19534), rightHint=(strategy=broadcast), joinId=15
   :- Relation de_workspace26.team2_edulearn.enrollment_items_silver[item_id#19522,enrollment_id#19523,course_id#19524,fee#19525,discount_pct#19526,final_fee#19527,_source#19528,_ingest_ts#19529,_file_name#19530,_run_id#19531,ingest_date#19532,processing_date#19533] parquet
   +- Filter isnotnull(course_id#19534)
      +- Relation de_workspace26.team2_edulearn.courses_silver[course_id#19534,course_name#19535,category#19536,price#19537,delivery_mode#19538,instructor#19539,available#19540,_source#19541,_ingest_ts#19542,_file_name#19543,_run_id#19544,ingest_date#19545,processing_date#19546] parquet

== Physical Plan ==
AdaptiveSparkPlan isFinalPlan=false
+- == Initial Plan ==
   Project [course_id#19524, item_id#19522, enrollment_id#19523, fee#19525, discount_pct#19526, final_fee#19527, _source#19528, _ingest_ts#19529, _file_name#19530, _run_id#19531, ingest_date#19532, processing_date#19533, course_name#19535, category#19536, price#19537, delivery_mode#19538, instructor#19539, available#19540, _source#19541, _ingest_ts#19542, _file_name#19543, _run_id#19544, ingest_date#19545, processing_date#19546]
   +- BroadcastHashJoin [course_id#19524], [course_id#19534], LeftOuter, BuildRight, false, true
      :- Project [item_id#19522, enrollment_id#19523, course_id#19524, fee#19525, discount_pct#19526, final_fee#19527, _source#19528, _ingest_ts#19529, _file_name#19530, _run_id#19531, ingest_date#19532, processing_date#19533]
      :  +- Filter if (isnotnull(_databricks_internal_edge_computed_column_skip_row#19567)) (_databricks_internal_edge_computed_column_skip_row#19567 = false) else isnotnull(raise_error(DELTA_SKIP_ROW_COLUMN_NOT_FILLED, map(keys: [], values: []), NullType))
      :     +- FileScan parquet de_workspace26.team2_edulearn.enrollment_items_silver[item_id#19522,enrollment_id#19523,course_id#19524,fee#19525,discount_pct#19526,final_fee#19527,_source#19528,_ingest_ts#19529,_file_name#19530,_run_id#19531,ingest_date#19532,processing_date#19533,_databricks_internal_edge_computed_column_skip_row#19567] Batched: true, DataFilters: [], Format: Parquet, Location: PreparedDeltaFileIndex(1 paths)[s3://databricks-storage-7474660560922927/unity-catalog/7474660560..., PartitionFilters: [], PushedFilters: [], ReadSchema: struct<item_id:string,enrollment_id:string,course_id:string,fee:double,discount_pct:double,final_...
      +- Exchange SinglePartition, EXECUTOR_BROADCAST, [plan_id=10080]
         +- Project [course_id#19534, course_name#19535, category#19536, price#19537, delivery_mode#19538, instructor#19539, available#19540, _source#19541, _ingest_ts#19542, _file_name#19543, _run_id#19544, ingest_date#19545, processing_date#19546]
            +- Filter (if (isnotnull(_databricks_internal_edge_computed_column_skip_row#19568)) (_databricks_internal_edge_computed_column_skip_row#19568 = false) else isnotnull(raise_error(DELTA_SKIP_ROW_COLUMN_NOT_FILLED, map(keys: [], values: []), NullType)) AND isnotnull(course_id#19534))
               +- FileScan parquet de_workspace26.team2_edulearn.courses_silver[course_id#19534,course_name#19535,category#19536,price#19537,delivery_mode#19538,instructor#19539,available#19540,_source#19541,_ingest_ts#19542,_file_name#19543,_run_id#19544,ingest_date#19545,processing_date#19546,_databricks_internal_edge_computed_column_skip_row#19568] Batched: true, DataFilters: [isnotnull(course_id#19534)], Format: Parquet, Location: PreparedDeltaFileIndex(1 paths)[s3://databricks-storage-7474660560922927/unity-catalog/7474660560..., PartitionFilters: [], PushedFilters: [IsNotNull(course_id)], ReadSchema: struct<course_id:string,course_name:string,category:string,price:double,delivery_mode:string,inst...

== Optimizer Statistics (table names per statistics state) ==
  missing = courses_silver, enrollment_items_silver
  partial = 
  full    = 
Corrective actions: consider running the following command on all tables with missing or partial statistics
  ANALYZE TABLE <table-name> COMPUTE STATISTICS FOR ALL COLUMNS

```

**a. What is a broadcast join and why is it efficient for small tables?**

A broadcast join copies the entire small table (courses — 30 rows) to
every executor node in the cluster so each executor can perform the join
locally without shuffling the large table across the network. For small
tables this eliminates the most expensive operation in distributed joins
— the network shuffle — making the join essentially free at small scale.

**b. Can you see BroadcastHashJoin in the output? What does it mean?**

Yes, BroadcastHashJoin appears in the physical plan. It means Spark
built a hash map from the broadcast (small) table and used it to probe
each partition of the large table locally. This avoids a sort-merge join
or shuffle-hash join, both of which require moving data between nodes.

**c. What would happen if you broadcast a 10 million row table?**

Broadcasting a 10 million row table would send hundreds of MB or even
GBs of data to every single executor. This would overwhelm driver memory
(which must first collect and broadcast the table), consume excessive
executor memory on every node, and likely cause OutOfMemoryError. The
entire cluster could crash or GC-pause heavily. The broadcast hint is
only safe for tables well under ~100 MB.

### Q10. OPTIMIZE Impact — numFiles before and after (Block 9)

**Before OPTIMIZE:** 
+--------+-----------+
|numFiles|sizeInBytes|
+--------+-----------+
|       1|       1736|
+--------+-----------+

**After OPTIMIZE:**  
+--------+-----------+
|numFiles|sizeInBytes|
+--------+-----------+
|       1|       1736|
+--------+-----------+


**a. Why does fewer files = faster queries?**

Spark opens and reads each file separately with its own task. When a
Delta table has many small files, Spark spawns hundreds of tasks just to
read tiny amounts of data — this is "small file problem" overhead.
OPTIMIZE merges small files into large Parquet files, so Spark opens far
fewer files and spends more time doing actual computation and less time
on file system overhead, making queries significantly faster.

**b. What does ZORDER BY (city) do differently from plain OPTIMIZE?**

Plain OPTIMIZE just compacts small files into larger ones without
changing how data is physically arranged within those files. ZORDER BY
(city) additionally co-locates rows with the same city value in the same
files, so a query filtering WHERE city = 'Bangalore' can skip all files
that don't contain Bangalore rows entirely. This is called data skipping
and can reduce files read by 80–90% for selective queries.