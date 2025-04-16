with station_popularity as (
    select * from {{ ref('intermediate_bike_rides') }}
),

station_metrics as (
    select
        start_station_name,
        count(*) as rides_started,
        avg(ride_duration_minutes) as avg_start_duration,
        avg(ride_distance_km) as avg_start_distance
    from station_popularity
    where start_station_name is not null
    group by start_station_name
),

end_station_metrics as (
    select
        end_station_name,
        count(*) as rides_ended,
        avg(ride_duration_minutes) as avg_end_duration,
        avg(ride_distance_km) as avg_end_distance
    from station_popularity
    where end_station_name is not null
    group by end_station_name
)

select
    coalesce(s.start_station_name, e.end_station_name) as station_name,
    coalesce(s.rides_started, 0) as total_rides_started,
    coalesce(e.rides_ended, 0) as total_rides_ended,
    coalesce(s.rides_started, 0) + coalesce(e.rides_ended, 0) as total_station_activity,
    coalesce(s.avg_start_duration, 0) as avg_start_ride_duration,
    coalesce(e.avg_end_duration, 0) as avg_end_ride_duration,
    coalesce(s.avg_start_distance, 0) as avg_start_ride_distance,
    coalesce(e.avg_end_distance, 0) as avg_end_ride_distance
from station_metrics s
full outer join end_station_metrics e
    on s.start_station_name = e.end_station_name
where coalesce(s.start_station_name, e.end_station_name) is not null
order by total_station_activity desc