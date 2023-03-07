SET @origin = "JFK"
SET @destination = "SFO"

SELECT Flights.ID as flight_id
FROM Flights
RIGHT JOIN Routes
	ON (Flights.route_id = Routes.ID)
WHERE (
	SELECT *
	FROM Routes
	WHERE Routes.origin_ap_code = @origin AND Routes.dest_ap_code = @destination
)
ORDER BY Flights.departure_time;
