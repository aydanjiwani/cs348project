from sqlalchemy import create_engine, text
from sys import argv
import pandas as pd

if len(argv) < 2:
    print("ERR: missing database URL")
    exit()

DB_URL = argv[1]

engine = create_engine(DB_URL)

with engine.connect() as connection:
    print(f'connected to MySQL server at {DB_URL}')

    def seed_flights_dataset(filename):
        flights = pd.read_csv(filename, chunksize=2000)
        for chunk in flights:

            print('processing chunk...')
            sql = f'''INSERT INTO Flights(route_id, flight_number,airline_code,departure_time,duration_minutes,distance_miles) VALUES
                {",".join([f'((SELECT ID FROM Routes WHERE origin_ap_code="{row["origin_ap_code"]}" AND dest_ap_code="{row["dest_ap_code"]}"),"{row["flight_number"]}","{row["airline_code"]}","{row["departure_time"]}",{row["duration_minutes"]},{row["distance_miles"]})' for i, row in chunk.iterrows()])};
            '''
            connection.execute(text(sql))

    print('processing clean_flights1...')
    seed_flights_dataset('clean_flights1.csv')
    connection.commit()
    print('processing clean_flights2...')
    seed_flights_dataset('clean_flights2.csv')
    connection.commit()
    print('processing clean_flights3...')
    seed_flights_dataset('clean_flights3.csv')
    connection.commit()
    print('processing clean_flights4...')
    seed_flights_dataset('clean_flights4.csv')
    connection.commit()
    print('processing clean_flights5...')
    seed_flights_dataset('clean_flights5.csv')
    connection.commit()

    update = '''UPDATE Flights
                INNER JOIN Routes ON Routes.origin_ap_code = Flights.origin

                )
             '''
