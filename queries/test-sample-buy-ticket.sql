-- Set variables - in the application these will be dynamic (supplied by the user)
SET @passenger_id = 1, @flight_id = 2, @seat_number = 5;

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
