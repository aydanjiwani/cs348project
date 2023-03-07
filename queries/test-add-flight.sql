CREATE PROCEDURE flight(IN route_id INT, IN airline_id INT, IN airplane_id INT, IN deperature_time DATETIME, IN end_time DATETIME, IN st VARCHAR(20))
BEGIN
	INSERT INTO flights (ID, route_id, airline_id, airplane_id, deperature_time, end_time, st)
        VALUES (ID, route_id, airline_id, airplane_id, deperature_time, end_time, st);
END
