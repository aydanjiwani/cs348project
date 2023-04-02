SELECT f.departure_time,
    r.origin_ap_code,
    p.name,
    p.email
FROM Flights as f
    LEFT JOIN Routes as r ON (f.route_id = r.ID)
    LEFT JOIN Ticket as t ON (t.flight_id = f.ID)
    LEFT JOIN Passenger as p ON (t.passenger_id = p.ID)
WHERE f.ID = { f_id }