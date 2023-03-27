SELECT flights.ID as flight_id, departure_time, end_time
FROM flights
RIGHT JOIN routes
	ON (flights.route_id = routes.ID)
WHERE routes.origin_ap_code = '{src}' AND routes.dest_ap_code = '{dest}'
ORDER BY flights.departure_time;