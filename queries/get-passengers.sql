SELECT f.departure_time as departure_time,
    r.origin_ap_code as origin,
    r.dest_ap_code as destination,
    p.name as name,
    p.email as email
FROM Flights as f
    LEFT JOIN Routes as r ON (f.route_id = r.ID)
    LEFT JOIN Ticket as t ON (t.flight_id = f.ID)
    LEFT JOIN Passenger as p ON (t.passenger_id = p.ID)
WHERE f.ID = { f_id }