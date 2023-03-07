-- Insert dummy data for demonstrative purposes
INSERT INTO Passenger(id, name)
VALUES (1, 'Rohan');
INSERT INTO Airlines(code, name)
VALUES ("AA", "American Airlines");
INSERT INTO Airport(code)
VALUES ("YYZ");
INSERT INTO Airport(code)
VALUES ("YUL");
INSERT INTO Airplane(code, capacity)
VALUES ("747", 10);
INSERT INTO Routes(id, origin_ap_code, dest_ap_code, airline_code)
VALUES (1, "YYZ", "YUL", "AA");
INSERT INTO Flights(id, route_id, airline_code, airplane_code, departure_time, end_time, status)
VALUES (1, 1, "AA", "747", null, null, "free");
INSERT INTO Ticket(id, passenger_id, flight_id, seat_number, status)
VALUES (1, 1, 1, 1, "book");
INSERT INTO Ticket(id, passenger_id, flight_id, seat_number, status)
VALUES (2, 1, 1, 2, "book");
INSERT INTO Ticket(id, passenger_id, flight_id, seat_number, status)
VALUES (3, 1, 1, 3, "book");
INSERT INTO Ticket(id, passenger_id, flight_id, seat_number, status)
VALUES (4, 1, 1, 4, "book");

-- Set variables - in the application these will be dynamic (supplied by the user)
SET @passenger_id = 1, @flight_id = 1, @seat_number = 5;

SELECT 'Inserting on successful case';
SELECT 'Ticket table before insert';
SELECT * FROM Ticket;

INSERT INTO Ticket (passenger_id, flight_id, seat_number, status)
SELECT @passenger_id, @flight_id, @seat_number, 'book'
WHERE NOT EXISTS (
	SELECT *
  FROM (
    SELECT capacity as common
    FROM (
        SELECT F.airplane_code
        FROM Flights AS F
        WHERE F.id = @flight_id
      ) AS T
      JOIN Airplane AS A
      WHERE A.code = T.airplane_code
    ) AS R
  WHERE @seat_number > R.common OR @seat_number < 1
  UNION ALL
  SELECT T2.id as common
  FROM Ticket AS T2
  WHERE T2.flight_id = @flight_id AND T2.seat_number = @seat_number
);

SELECT 'Ticket table after insert';
SELECT * FROM Ticket;

SELECT 'Inserting on error case: ticket has already been sold';
SELECT 'Ticket table before insert';
SELECT * FROM Ticket;

SET @seat_number = 1;
INSERT INTO Ticket (passenger_id, flight_id, seat_number, status)
SELECT @passenger_id, @flight_id, @seat_number, 'book'
WHERE NOT EXISTS (
	SELECT *
  FROM (
    SELECT capacity as common
    FROM (
        SELECT F.airplane_code
        FROM Flights AS F
        WHERE F.id = @flight_id
      ) AS T
      JOIN Airplane AS A
      WHERE A.code = T.airplane_code
    ) AS R
  WHERE @seat_number > R.common OR @seat_number < 1
  UNION ALL
  SELECT T2.id as common
  FROM Ticket AS T2
  WHERE T2.flight_id = @flight_id AND T2.seat_number = @seat_number
);

SELECT 'Ticket table after insert';
SELECT * FROM Ticket;

SELECT 'Inserting on error case: seat number is greater than the capacity of the plane';
SELECT 'Ticket table before insert';
SELECT * FROM Ticket;

SET @seat_number = 20;
INSERT INTO Ticket (passenger_id, flight_id, seat_number, status)
SELECT @passenger_id, @flight_id, @seat_number, 'book'
WHERE NOT EXISTS (
	SELECT *
  FROM (
    SELECT capacity as common
    FROM (
        SELECT F.airplane_code
        FROM Flights AS F
        WHERE F.id = @flight_id
      ) AS T
      JOIN Airplane AS A
      WHERE A.code = T.airplane_code
    ) AS R
  WHERE @seat_number > R.common OR @seat_number < 1
  UNION ALL
  SELECT T2.id as common
  FROM Ticket AS T2
  WHERE T2.flight_id = @flight_id AND T2.seat_number = @seat_number
);

SELECT 'Ticket table after insert';
SELECT * FROM Ticket;
