-- Creating tables for the database schema
CREATE TABLE Airlines (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Airport (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country_iso VARCHAR(10) NOT NULL,
    lat VARCHAR(30) NOT NULL,
    longit VARCHAR(30) NOT NULL,
    altitude INT NOT NULL
);

CREATE TABLE Passenger (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Airplane (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL UNIQUE,
    model VARCHAR(100) NOT NULL,
    -- we don't have this data yet so we make it nullable
    capacity INT -- NOT NULL
);

CREATE TABLE Routes (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    origin_ap_code VARCHAR(10) NOT NULL,
    dest_ap_code VARCHAR(10) NULL,
    airline_code VARCHAR(10) NOT NULL,
    airplane_code VARCHAR(10) NOT NULL,
    FOREIGN KEY (origin_ap_code) REFERENCES Airport(code),
    FOREIGN KEY (dest_ap_code) REFERENCES Airport(code),
    FOREIGN KEY (airline_code) REFERENCES Airlines(code)
);

CREATE TABLE Flights (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    flight_number VARCHAR(10) NOT NULL,
    route_id INT NOT NULL,
    airline_code VARCHAR(10) NOT NULL,
    departure_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_minutes INT NOT NULL,
    distance_miles INT NOT NULL, -- this should be moved to Routes but whatever
    status VARCHAR(50),
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
