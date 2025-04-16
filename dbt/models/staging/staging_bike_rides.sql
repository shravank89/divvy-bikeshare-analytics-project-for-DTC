
with raw_data as (
    select * from {{ source('bigquery_dataset', 'divvy_bikeshare_chicago_data_' ~ var('table_var')) }}
)
select
    ride_id,
    rideable_type,
    start_station_id,
    start_station_name,
    end_station_id,
    end_station_name,
    start_lat,
    start_lng,
    end_lat,
    end_lng,
    -- Convert string date/time fields to proper timestamps
    cast(concat(start_date, ' ', start_time) as timestamp) as started_at,
    cast(concat(end_date, ' ', end_time) as timestamp) as ended_at,
    membership as member_casual,
    trip_duration_in_minutes as duration_minutes,
    start_date,
    end_date,
    start_time,
    end_time,
    start_timestamp,
    end_timestamp
from raw_data
where ride_id is not null
  and start_station_id is not null
  and end_station_id is not null