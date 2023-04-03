-- Insert dummy data for demonstrative purposes. Had to run this by hand, something weird happens with the sql connection
INSERT INTO Passenger(id, name)
VALUES (2, 'Rohan');
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
INSERT INTO Users (username, password, role, profile_picture_url)
VALUES ('vaanie', '1234', 'default', null);
INSERT INTO Users (username, password, role, profile_picture_url)
VALUES ('john', '123', 'admin', 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80');
