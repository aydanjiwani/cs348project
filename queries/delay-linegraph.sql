SELECT date_format(f.departure_time, '%Y') as y, date_format(f.departure_time, '%M') as m, count(f.ID) as number_delayed
FROM flights as f
WHERE f.status = 'delayed'
GROUP BY YEAR(f.departrue_time), MONTH(f.departrue_time);
