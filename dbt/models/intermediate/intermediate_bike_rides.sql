-- CTE created to use value of Pi as bigquery does not give function to get pi value.
with constants as (
    select 3.14159265359 as PI
),

staged_rides as (
    select * from {{ ref('staging_bike_rides') }}
),

-- CTE to calculate distance using Haversine formula
distance_calculation as (
    select *, 6371 * acos(LEAST(1, GREATEST(-1, cos(start_lat * (select PI from constants)/180) * cos(end_lat * (select PI from constants)/180) * cos(end_lng * (select PI from constants)/180 - start_lng * (select PI from constants)/180) + sin(start_lat * (select PI from constants)/180) * sin(end_lat * (select PI from constants)/180)))) as calculated_distance_km from staged_rides
),

time_metrics as (
    select 
        *,
        -- Extract time components
        extract(hour from started_at) as start_hour,
        extract(DAYOFWEEK from started_at) as day_of_week,
        -- Categorize time of day
        case 
            when extract(hour from started_at) between 6 and 10 then 'Morning Rush'
            when extract(hour from started_at) between 11 and 15 then 'Midday'
            when extract(hour from started_at) between 16 and 19 then 'Evening Rush'
            else 'Off Peak'
        end as time_of_day,
        -- Calculate ride duration in minutes
        TIMESTAMP_DIFF(ended_at, started_at, MINUTE) as calculated_duration_minutes,
        -- Flag for weekend rides
        case 
            when extract(DAYOFWEEK from started_at) in (1, 7) then true 
            else false 
        end as is_weekend_ride
    from distance_calculation
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
    started_at,
    ended_at,
    member_casual,
    -- Use calculated duration if available, fallback to provided duration
    coalesce(calculated_duration_minutes, duration_minutes) as ride_duration_minutes,
    start_hour,
    day_of_week,
    time_of_day,
    is_weekend_ride,
    -- Calculate ride distance in kilometers
    calculated_distance_km as ride_distance_km
from time_metrics
where calculated_duration_minutes > 0  -- Filter out invalid durations
  and start_lat is not null
  and start_lng is not null
  and end_lat is not null
  and end_lng is not null
  and calculated_distance_km < 100  -- Filter out unrealistic distances