from sqlalchemy import create_engine, text
from sys import argv, exit
import csv

if len(argv) < 2:
    print("ERR: missing database URL")
    exit()

DB_URL = argv[1]

engine = create_engine(DB_URL)

with engine.connect() as connection:
    # seed airports
    with open('clean_airports.csv', newline='') as airports_file:
        airports_reader = csv.DictReader(airports_file)
        sql = f'''
        INSERT INTO Airport(code,name,city,country_iso,lat,longit,altitude) VALUES
            {",".join([f'("{row["code"]}","{row["name"]}","{row["city"]}","{row["country_iso"]}","{row["lat"]}","{row["longit"]}",{row["altitude"]})' for row in airports_reader])};
        '''
        connection.execute(text(sql))

    # seed airlines
    with open('clean_airlines.csv', newline='') as airlines_file:
        airlines_reader = csv.DictReader(airlines_file)
        sql = f'''
        INSERT INTO Airlines(code,name) VALUES
            {",".join([f'("{row["code"]}","{row["name"]}")' for row in airlines_reader])};
        '''
        connection.execute(text(sql))

    # seed routes
    with open('clean_routes.csv', newline='') as routes_file:
        routes_reader = csv.DictReader(routes_file)
        sql = f'''
        INSERT INTO Routes(origin_ap_code,dest_ap_code,airline_code) VALUES
            {",".join([f'("{row["origin_ap_code"]}","{row["dest_ap_code"]}","{row["airline_code"]}")' for row  in routes_reader])};
        '''
        connection.execute(text(sql))

    connection.commit()
