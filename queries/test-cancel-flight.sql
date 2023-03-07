SET @flight_id = 1;

UPDATE Flights
SET status = 'canceled'
WHERE ID = @flight_id;
