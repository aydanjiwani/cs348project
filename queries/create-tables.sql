-- Creating tables for the database schema
CREATE TABLE Airlines (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Airport (
    code VARCHAR(10) PRIMARY KEY
);

CREATE TABLE Passenger (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Airplane (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    model VARCHAR(100) NOT NULL,
    capacity INT NOT NULL
);

CREATE TABLE Routes (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    origin_ap_code VARCHAR(10) NOT NULL,
    dest_ap_code VARCHAR(10) NULL,
    airline_code VARCHAR(10) NOT NULL,
    FOREIGN KEY (origin_ap_code) REFERENCES Airport(code),
    FOREIGN KEY (dest_ap_code) REFERENCES Airport(code),
    FOREIGN KEY (airline_code) REFERENCES Airlines(code)
);

CREATE TABLE Flights (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    airline_code VARCHAR(10) NOT NULL,
    airplane_code VARCHAR(10) NOT NULL,
    departure_time DATETIME,
    end_time DATETIME,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (route_id) REFERENCES Routes(ID),
    FOREIGN KEY (airline_code) REFERENCES Airlines(code),
    FOREIGN KEY (airplane_code) REFERENCES Airplane(code)
);

CREATE TABLE Ticket (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    passenger_id INT NOT NULL,
    flight_id INT NOT NULL,
    seat_number INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (passenger_id) REFERENCES Passenger(ID),
    FOREIGN KEY (flight_id) REFERENCES Flights(ID)
);
