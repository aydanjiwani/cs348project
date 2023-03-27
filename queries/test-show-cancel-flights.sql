-- Set variables - in the application these will be dynamic (supplied by the user)
SET @route_id = 1, @date_time = cast('2023-01-27 12:34:56' as datetime);

SELECT Airlines.name AS airline_name, a1.code AS origin_airport_code, a2.code AS dest_airport_code, T.ID, T.route_id, T.airplane_code, T.departure_time, T.end_time
FROM (Routes NATURAL JOIN (
    SELECT * FROM Flights
    WHERE departure_time >= @date_time
    AND status LIKE 'canceled'
    AND route_id = @route_id
  ) as T)
JOIN Airport AS a1 ON origin_ap_code = a1.code
JOIN Airport AS a2 ON dest_ap_code = a2.code
JOIN Airlines ON T.airline_code = Airlines.code;
