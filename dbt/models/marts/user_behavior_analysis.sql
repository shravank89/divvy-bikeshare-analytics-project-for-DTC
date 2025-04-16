with user_behaviour as (
    select * from {{ ref('intermediate_bike_rides') }}
),

time_patterns as (
    select 
        member_casual as user_type,
        time_of_day,
        count(*) as rides_in_timeblock
    from user_behaviour
    group by member_casual, time_of_day
),

most_common_times as (
    select 
        user_type,
        time_of_day as most_common_time_of_day,
        rides_in_timeblock
    from time_patterns qualify row_number() over (partition by user_type order by rides_in_timeblock desc) = 1
),

user_metrics as (
    select 
        member_casual as user_type,
        count(*) as total_rides,
        avg(ride_duration_minutes) as avg_ride_duration,
        avg(ride_distance_km) as avg_ride_distance,
        countif(is_weekend_ride) as weekend_rides,
        countif(not is_weekend_ride) as weekday_rides,
        min(ride_distance_km) as min_ride_distance,
        max(ride_distance_km) as max_ride_distance,
        avg(ride_distance_km / nullif(ride_duration_minutes, 0) * 60) as avg_speed
    from user_behaviour
    group by member_casual
)

select 
    u.user_type,
    u.total_rides,
    u.avg_ride_duration,
    u.avg_ride_distance,
    u.weekend_rides,
    u.weekday_rides,
    m.most_common_time_of_day,
    u.min_ride_distance,
    u.max_ride_distance,
    round(u.avg_speed, 2) as avg_speed_kmh,
    round(u.weekend_rides * 100.0 / nullif(u.total_rides, 0), 2) as weekend_ride_percentage
from user_metrics u
join most_common_times m on u.user_type = m.user_type
order by u.total_rides desc