# DON'T USE THIS

import pandas as pd

airport_icao_to_iata = {}
airline_icao_to_iata = {}
country_to_iso = {}

# countries

countries = pd.read_csv('countries.csv')
countries.drop(['dafif'], axis=1, inplace=True)

for index, row in countries.iterrows():
    if row['name'] and row['iso']:
        country_to_iso[row['name']] = row['iso']

# airports

airports = pd.read_csv('airports.csv')
airports.dropna(subset=['iata'], inplace=True)
airports.drop(['dst', 'db_timezone', 'source'], axis=1, inplace=True)
airports.drop(airports[~airports.country.isin(country_to_iso.keys())].index, inplace=True)

for index in airports.index:
    if airports.at[index, 'icao'] and airports.at[index, 'iata']:
        airport_icao_to_iata[airports.at[index, 'icao']] = airports.at[index, 'iata']

    airports.at[index, 'country'] = country_to_iso[airports.at[index, 'country']]

airports.drop(['icao'], axis=1, inplace=True)
airports.rename(columns={'country': 'country_iso'}, inplace=True)

# airlines

airlines = pd.read_csv('airlines.csv')
airlines.drop(airlines[airlines.active == 'N'].index, inplace=True)
airlines.drop(['active'], axis=1, inplace=True)
airlines.dropna(subset=['iata'], inplace=True)

for index, row in airlines.iterrows():
    if row['icao']:
        airline_icao_to_iata[row['icao']] = row['iata']

airlines.drop(['icao'], axis=1, inplace=True)

# routes

routes = pd.read_csv('routes.csv')
routes.dropna(subset=['airline_iata_icao', 'src', 'dest'], how='any', inplace=True)

for index in routes.index:
    if routes.at[index, 'airline_iata_icao'] in airline_icao_to_iata:
        new = airline_icao_to_iata[routes.at[index, 'airline_iata_icao']]
        routes.at[index, 'airline_iata_icao'] = new

    if routes.at[index, 'src'] in airport_icao_to_iata:
        new = airport_icao_to_iata[routes.at[index, 'src']]
        routes.at[index, 'src'] = new

    if routes.at[index, 'dest'] in airport_icao_to_iata:
        new = airport_icao_to_iata[routes.at[index, 'dest']]
        routes.at[index, 'dest'] = new

routes.drop(routes[~routes.airline_iata_icao.isin(airlines.iata)].index, inplace=True)
routes.drop(routes[~routes.src.isin(airports.iata)].index, inplace=True)
routes.drop(routes[~routes.dest.isin(airports.iata)].index, inplace=True)

routes.drop(['airline_id', 'src_id', 'dest_id', 'codeshare', 'stops'], axis=1, inplace=True)

# airplanes

airplanes = pd.read_csv('airplanes.csv')
airplanes.dropna(subset=['iata'], inplace=True)
airplanes.drop(['icao'], axis=1, inplace=True)

# new CSVs

countries.to_csv('clean_countries.csv', index=False)
airports.to_csv('clean_airports.csv', index=False)
airlines.to_csv('clean_airlines.csv', index=False)
routes.to_csv('clean_routes.csv', index=False)
airplanes.to_csv('clean_airplanes.csv', index=False)
