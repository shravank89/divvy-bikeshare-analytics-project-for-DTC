"""Divvy Bikeshare Data Processing Module

This module processes Divvy Bikeshare trip data using Apache Spark. It transforms raw CSV files
into a structured format with additional computed fields and handles data cleaning operations.

The processed data is saved in Parquet format, organized by year and month directories.

Dependencies:
    - PySpark
    - argparse
    - os
"""

import argparse
import os
import glob
import shutil
from typing import Tuple
from pyspark.sql import SparkSession
from pyspark.sql.functions import round, unix_timestamp, to_date, dayofweek, hour, month, year, col, when, date_format
from pyspark.sql.types import StructType, StructField, IntegerType, TimestampType, StringType, DoubleType

def extract_date_from_filename(file_path: str) -> Tuple[str, str]:
    # Extract the filename from the path
    filename = os.path.basename(file_path)
    # Extract year and month from filename - assuming format contains YYYY and MM
    # This is a simple implementation - adjust the parsing logic based on your actual filename format
    parts = str(filename.split('.')[0]).split('_')
    for part in parts:
        if part.isdigit() and len(part) == 6:  # YYYYMM format
            return part[:4], part[4:]
        elif part.isdigit() and len(part) == 4:  # YYYY format
            # If only year is in filename, use first month as default
            return part, '01'
    # Default values if parsing fails
    return '2020', '01'

class DataProcessor:
    """Handles the processing of Divvy Bikeshare trip data.
    
    This class manages the data transformation pipeline, including:
    - Reading CSV files
    - Cleaning and validating data
    - Computing derived fields
    - Saving processed data in Parquet format
    """
    
    def process_data(self, input_path: str, output_path: str) -> None:
        """Process bikeshare trip data from CSV to Parquet format.
        
        Args:
            input_path: Path to the input CSV file(s)
            output_path: Base path for output Parquet files
            
        The output will be organized in year/month subdirectories.
        """
        # Initialize Spark session
        spark = SparkSession.builder \
            .appName("Bikeshare Data Processor") \
            .getOrCreate()
        
        # Define schema for files
        schema = StructType([
			StructField("ride_id", StringType(), True),            # Unique ID for each ride
			StructField("rideable_type", StringType(), True),      # Type of bike (e.g., electric, standard)
			StructField("started_at", TimestampType(), True),      # Timestamp for when the ride started
			StructField("ended_at", TimestampType(), True),        # Timestamp for when the ride ended
			StructField("start_station_name", StringType(), True), # Name of the starting station
			StructField("start_station_id", StringType(), True),   # ID of the starting station
			StructField("end_station_name", StringType(), True),   # Name of the ending station
			StructField("end_station_id", StringType(), True),     # ID of the ending station
			StructField("start_lat", DoubleType(), True),          # Latitude of the starting location
			StructField("start_lng", DoubleType(), True),          # Longitude of the starting location
			StructField("end_lat", DoubleType(), True),            # Latitude of the ending location
			StructField("end_lng", DoubleType(), True),            # Longitude of the ending location
			StructField("member_casual", StringType(), True)       # User type (member or casual)
		])
        
        
        # Read and process CSV files
        df = spark.read \
            .option("header", "true") \
            .schema(schema) \
            .csv(input_path)  # Choose schema to avoid any issues with delta format's stricter requirements for column names.
        
        # Handle null values according to requirements
        df = df.na.drop(subset=["ride_id", "started_at", "ended_at"]) \
            .na.fill(value="unknown", subset=["rideable_type", "member_casual"])
        
        # Calculate trip duration in minutes and add membership column
        processed_df = df.withColumn("trip_duration_in_minutes", round((unix_timestamp(col("ended_at")) - unix_timestamp(col("started_at"))) / 60)) \
                         .withColumn("start_date", to_date(col("started_at"))) \
                         .withColumn("start_time", date_format(col("started_at"), "HH:mm:ss")) \
                         .withColumn("end_date", to_date(col("ended_at"))) \
                         .withColumn("end_time", date_format(col("ended_at"), "HH:mm:ss")) \
                         .withColumn("start_timestamp", unix_timestamp(col("started_at"))) \
                         .withColumn("end_timestamp", unix_timestamp(col("ended_at"))) \
                         .withColumn("membership", when(col("member_casual") == "member", "Yes")
                                                .when(col("member_casual") == "casual", "No")
                                                .otherwise("unknown")) \
                         .drop("started_at", "ended_at", "member_casual")
        
        # Extract year and month from input filename
        year, month = extract_date_from_filename(input_path)
        
        # Construct the output path with year and month folders
        final_output_path = f"{output_path}/{year}/{month}"
        
        # Write to parquet for efficient storage - coalesce to single file
        processed_df.coalesce(1) \
                    .write \
                    .parquet(final_output_path, mode="overwrite")

            
        spark.stop()

def main():
    """Main entry point for the Spark job.
    
    Parses command line arguments and initiates data processing.
    """
    parser = argparse.ArgumentParser(description='Process Divvy Bikeshare trip data using Spark')
    parser.add_argument('--input_path', type=str, required=True, help='Path to input CSV file(s)')
    parser.add_argument('--output_path', type=str, required=True, help='Base path for output Parquet files')
    
    args = parser.parse_args()
    
    processor = DataProcessor()
    processor.process_data(args.input_path, args.output_path)

if __name__ == '__main__':
    main()
