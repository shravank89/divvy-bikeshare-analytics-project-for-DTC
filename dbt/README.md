# Divvy Bikeshare dbt Models

This directory contains the dbt models that transform Divvy Bikeshare data into analytics-ready datasets. The models are organized into three layers: staging, intermediate, and marts.

## Model Architecture

### Staging Layer
- **staging_bike_rides**: Initial data cleaning and type casting of raw bikeshare trip data
  - Standardizes timestamp formats
  - Filters out null ride and station IDs
  - Performs basic data quality checks

### Intermediate Layer
- **intermediate_bike_rides**: Enriches staging data with calculated metrics
  - Calculates ride distance using Haversine formula
  - Adds time-based metrics (time of day, day of week)
  - Identifies weekend vs weekday rides
  - Computes ride duration

### Marts Layer

#### Peak Usage Time Analysis
- **peak_usage_time**: Analyzes ride patterns across different times
  - Aggregates rides by time of day and hour
  - Calculates average duration per time block
  - Determines percentage distribution of rides

#### Station Popularity Analysis
- **station_popularity**: Measures station utilization
  - Tracks rides started and ended at each station
  - Calculates average ride duration and distance per station
  - Identifies high-traffic stations

#### User Behavior Analysis
- **user_behavior_analysis**: Compares member vs casual rider patterns
  - Analyzes ride patterns by user type
  - Tracks weekend vs weekday usage
  - Calculates average speed and distance metrics
  - Identifies preferred riding times per user type

## Model Dependencies

```
stagingbike_rides
    └── intermediate_bike_rides
        ├── peak_usage_time
        ├── station_popularity
        └── user_behavior_analysis
```

## Usage

These models power the Looker Studio dashboards that help stakeholders understand:
- Peak usage patterns for capacity planning
- Popular stations for maintenance and rebalancing
- User behavior differences for membership strategy
