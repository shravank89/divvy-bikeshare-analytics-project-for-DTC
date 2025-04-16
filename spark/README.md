# Divvy Bikeshare Spark Data Processing

This directory contains the Apache Spark job implementation for processing Divvy Bikeshare trip data. The job transforms raw CSV files into a structured format with additional computed fields and handles data cleaning operations.

## Overview

The Spark job (`spark-job.py`) processes Divvy Bikeshare trip data by:
- Reading CSV files with trip data
- Cleaning and validating data
- Computing derived fields
- Saving processed data in Parquet format, organized by year and month

## Data Schema

The job processes the following fields:

### Input Schema (CSV)
- `ride_id`: Unique identifier for each ride
- `rideable_type`: Type of bike (electric, standard)
- `started_at`: Trip start timestamp
- `ended_at`: Trip end timestamp
- `start_station_name`: Name of starting station
- `start_station_id`: ID of starting station
- `end_station_name`: Name of ending station
- `end_station_id`: ID of ending station
- `start_lat`: Starting latitude
- `start_lng`: Starting longitude
- `end_lat`: Ending latitude
- `end_lng`: Ending longitude
- `member_casual`: User type (member or casual)

### Computed Fields
- `trip_duration_in_minutes`: Calculated trip duration
- `start_date`: Extracted start date
- `start_time`: Extracted start time
- `end_date`: Extracted end date
- `end_time`: Extracted end time
- `start_timestamp`: Unix timestamp for start
- `end_timestamp`: Unix timestamp for end
- `membership`: Standardized membership status (Yes/No)

## Data Processing

The job performs the following transformations:
1. Drops rows with null values in critical fields (ride_id, started_at, ended_at)
2. Fills missing values in categorical fields with "unknown"
3. Computes trip duration and time-based fields
4. Standardizes membership status
5. Organizes output by year/month partitions

## Usage

Run the Spark job using the airflow DAG divvy_bikeshare_pyspark_transformation

### Arguments
- `--input_path`: Path to input CSV file(s)
- `--output_path`: Base path for output Parquet files

### Output Structure
The processed data is saved in Parquet format with the following directory structure:
```
<output_path>/
    └── <year>/
        └── <month>/
            └── part-*.parquet
```

## Dependencies
- PySpark
- Python 3.x
- argparse