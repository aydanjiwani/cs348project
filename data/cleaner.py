import pandas as pd

airport_icao_to_iata = {}
airline_icao_to_iata = {}
country_to_iso = {}

# -- countries

print("cleaning countries.csv...")
countries = pd.read_csv('countries.csv')
countries.drop(['dafif'], axis=1, inplace=True)

for index, row in countries.iterrows():
    if row['name'] and row['iso']:
        country_to_iso[row['name']] = row['iso']

countries.to_csv('clean_countries.csv', index=False)

# -- airports

print("cleaning airports.csv...")
airports = pd.read_csv('airports.csv', quotechar='"')
airports.dropna(subset=['iata'], inplace=True)
airports.drop(['dst', 'db_timezone', 'source'], axis=1, inplace=True)
airports.drop(airports[~airports.country.isin(country_to_iso.keys())].index, inplace=True)

for index in airports.index:
    if airports.at[index, 'icao'] and airports.at[index, 'iata']:
        airport_icao_to_iata[airports.at[index, 'icao']] = airports.at[index, 'iata']

    airports.at[index, 'country'] = country_to_iso[airports.at[index, 'country']]

airports.drop(['icao', 'type', 'timezone'], axis=1, inplace=True)
airports.rename(columns={'country': 'country_iso', 'iata': 'code', 'long': 'longit'}, inplace=True)

airports.to_csv('clean_airports.csv', index=False)

# -- airlines

print("cleaning airlines.csv...")
airlines = pd.read_csv('airlines.csv')
airlines.drop(airlines[airlines.active == 'N'].index, inplace=True)
airlines.drop(['active'], axis=1, inplace=True)
airlines.dropna(subset=['iata'], inplace=True)

for index, row in airlines.iterrows():
    if row['icao']:
        airline_icao_to_iata[row['icao']] = row['iata']

airlines.drop(['icao', 'alias', 'callsign', 'country'], axis=1, inplace=True)
airlines.rename(columns={'iata': 'code'}, inplace=True)

airlines.to_csv('clean_airlines.csv', index=False)

# -- routes

print("cleaning routes.csv...")
routes = pd.read_csv('routes.csv')
routes.dropna(subset=['airline_iata_icao', 'origin', 'dest'], how='any', inplace=True)
routes.drop_duplicates(subset=['origin', 'dest'], keep='first', inplace=True)

for index in routes.index:
    if routes.at[index, 'airline_iata_icao'] in airline_icao_to_iata:
        new = airline_icao_to_iata[routes.at[index, 'airline_iata_icao']]
        routes.at[index, 'airline_iata_icao'] = new

    if routes.at[index, 'origin'] in airport_icao_to_iata:
        new = airport_icao_to_iata[routes.at[index, 'origin']]
        routes.at[index, 'origin'] = new

    if routes.at[index, 'dest'] in airport_icao_to_iata:
        new = airport_icao_to_iata[routes.at[index, 'dest']]
        routes.at[index, 'dest'] = new

routes.drop(routes[~routes.airline_iata_icao.isin(airlines.code)].index, inplace=True)
routes.drop(routes[~routes.origin.isin(airports.code)].index, inplace=True)
routes.drop(routes[~routes.dest.isin(airports.code)].index, inplace=True)

routes.drop(['airline_id', 'src_id', 'dest_id', 'codeshare', 'stops', 'equipment'], axis=1, inplace=True)
airports.rename(columns={'origin': 'origin_ap_code', 'dest': 'dest_ap_code', 'airline_iata': 'airline_code'}, inplace=True)

routes.to_csv('clean_routes.csv', index=False)

# -- airplanes

print("cleaning airplanes.csv...")
airplanes = pd.read_csv('airplanes.csv')
airplanes.dropna(subset=['iata'], inplace=True)
airplanes.drop(['icao'], axis=1, inplace=True)

airplanes.to_csv('clean_airplanes.csv', index=False)

# -- flights


def clean_flights(filename):
    print(f'cleaning {filename}...')
    flights = pd.read_csv(filename, quotechar='"')
    flights.rename(columns={'ORIGIN': 'origin', 'DEST': 'dest'}, inplace=True)

    # validate airline
    flights.drop(flights[~flights.OP_CARRIER.isin(airlines.code)].index, inplace=True)

    flights = pd.merge(flights, routes, on=['origin', 'dest'], how='outer', indicator=True)
    flights = flights.loc[flights['_merge'] == 'both'].drop('_merge', axis=1)
    flights = flights[[
        'FL_DATE', 'OP_CARRIER', 'OP_CARRIER_FL_NUM', 'TAIL_NUM',
        'origin', 'dest', 'DEP_TIME', 'CRS_ELAPSED_TIME', 'DISTANCE'
    ]]

    flights.dropna(subset=['DEP_TIME', 'FL_DATE'], how='any', inplace=True)

    for index in flights.index:
        date_comps = flights.at[index, 'FL_DATE'].split(" ")[0].split("/")
        date_comps[0], date_comps[1], date_comps[2] = date_comps[2], date_comps[0], date_comps[1]
        if len(date_comps[1]) == 1:
            date_comps[1] = "0" + date_comps[1]
        if len(date_comps[2]) == 1:
            date_comps[2] = "0" + date_comps[2]

        date = "-".join(date_comps)
        assert len(date) == 10

        time = str(int(flights.at[index, 'DEP_TIME'])).zfill(4)
        time = f'{time[0:2]}:{time[2:4]}:00'

        datetime = f'{date} {time}'
        flights.at[index, 'FL_DATE'] = datetime

        flights.at[index, 'OP_CARRIER_FL_NUM'] = str(int(flights.at[index, 'OP_CARRIER_FL_NUM'])).zfill(2)

    flights.rename(columns={
        'FL_DATE': 'departure_time',
        'OP_CARRIER': 'airline_code',
        'OP_CARRIER_FL_NUM': 'flight_number',
        'CRS_ELAPSED_TIME': 'duration_minutes',
        'DISTANCE': 'distance_miles',
        'TAIL_NUM': 'tail_num',
    }, inplace=True)
    flights.drop(['DEP_TIME', 'tail_num'], axis=1, inplace=True)
    flights.to_csv(f'clean_{filename}', index=False)


clean_flights('flights1.csv')
clean_flights('flights2.csv')
clean_flights('flights3.csv')
clean_flights('flights4.csv')
clean_flights('flights5.csv')
