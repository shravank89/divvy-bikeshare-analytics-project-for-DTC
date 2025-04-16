with peak_usage as (
    select * from {{ ref('intermediate_bike_rides') }}
),

hourly_usage as (
    select
        time_of_day,
        start_hour,
        count(*) as rides_count,
        avg(ride_duration_minutes) as avg_duration
    from peak_usage
    group by time_of_day, start_hour
)

select
    time_of_day,
    start_hour,
    rides_count,
    avg_duration,
    rides_count * 100.0 / sum(rides_count) over() as percentage_of_total_rides
from hourly_usage
order by rides_count desc