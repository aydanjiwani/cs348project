from flask import Flask, render_template, request, redirect
import mysql.connector
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_NAME = 'prod'
DB_USER = 'noor'
DB_PWD = 'password'


@app.route('/init')
def init():
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor()
    with open('queries/create-tables.sql', 'r') as f:
        query = f.read()
        cursor.execute(query)
    cursor.close()
    cnx.close()
    return redirect('/')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/airports')
def get_airports():
    origin = request.args.get('origin_ap_code')
    dest = request.args.get('dest_ap_code')
    origin_search = request.args.get('origin_ap_code_search')
    dest_search = request.args.get('dest_ap_code_search')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    if dest_search:
        args = [dest_search]
        query = '''SELECT DISTINCT dest_ap_code AS airport_code, min(ID) AS route_id, min(Airplane.model) AS airplane_model
                   FROM Routes
                   INNER JOIN Airplane ON Airplane.code = Routes.airplane_code
                   WHERE dest_ap_code LIKE CONCAT('%', %s, '%')
                '''

        if origin:
            query += " AND origin_ap_code = %s "
            args.append(origin)

        query += f'GROUP BY dest_ap_code{", origin_ap_code" if origin else ""} LIMIT 40;'

    else:
        args = [origin_search]
        query = '''SELECT DISTINCT origin_ap_code AS airport_code, min(ID) as route_id, min(Airplane.model) AS airplane_model
                   FROM Routes
                   INNER JOIN Airplane ON Airplane.code = Routes.airplane_code
                   WHERE origin_ap_code LIKE CONCAT('%', %s, '%')
                '''

        if dest:
            query += " AND dest_ap_code = %s "
            args.append(dest)

        query += f'GROUP BY origin_ap_code{", dest_ap_code" if dest else ""} LIMIT 40;'

    cursor.execute(query, args)
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


@app.route('/createflight')
def createflight():
    route_id = request.args.get('route_id')
    flight_number = request.args.get('flight_number')
    departure_time = request.args.get('departure_time')
    distance_miles = request.args.get('distance_miles')
    duration_minutes = request.args.get('duration_minutes')
    airline_code = request.args.get('airline_code')

    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )

    cursor = cnx.cursor()
    query = '''INSERT INTO
                 Flights(route_id,flight_number,departure_time,airline_code,distance_miles,duration_minutes)
                 VALUES (%s, %s, %s, %s, %s, %s);
            '''
    cursor.execute(query, [route_id, flight_number, departure_time, airline_code, distance_miles, duration_minutes])
    data = cursor.fetchall()
    cnx.commit()
    cursor.close()
    cnx.close()
    return str(data)


@app.route('/passengers')
def get_passengers():
    name = request.args.get('name')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    query = '''SELECT ID as id, name
               FROM Passenger
               WHERE name LIKE CONCAT('%', %s, '%')
               LIMIT 20;
            '''

    cursor.execute(query, [name])
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data



@app.route('/flights')
def get_flights():
    src = request.args.get('origin')
    dest = request.args.get('dest')
    status = request.args.get('status')
    id = request.args.get('id')

    page = int(request.args.get('page'))
    results_per_page = int(request.args.get('results_per_page'))

    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    if id:
        query = '''SELECT Flights.ID AS id,
                          Routes.origin_ap_code,
                          Routes.dest_ap_code,
                          departure_time,
                          flight_number,
                          count(*) AS ticket_count
                   FROM Flights
                   INNER JOIN Routes ON Routes.ID = Flights.route_id
                   WHERE Flights.ID = %s;
                '''
        cursor.execute(query, [id])
        data = cursor.fetchall()
    else:
        query = '''SELECT Flights.ID as id, departure_time, flight_number,
                          origin_ap.code AS origin_ap_code,
                          dest_ap.code AS dest_ap_code,
                          origin_ap.city AS from_city,
                          dest_ap.city AS to_city,
                          Airplane.model AS airplane_model,
                          Flights.status, Airlines.name as airline_name,
                          (SELECT COUNT(*) FROM Ticket WHERE Ticket.flight_id = Flights.ID) AS ticket_count
                   FROM Flights
                   INNER JOIN Airlines ON (Airlines.code = Flights.airline_code)
                   INNER JOIN Routes ON (Flights.route_id = Routes.ID)
                   INNER JOIN Airplane ON (Airplane.code = Routes.airplane_code)
                   INNER JOIN Airport AS origin_ap ON (origin_ap.code = Routes.origin_ap_code)
                   INNER JOIN Airport AS dest_ap ON (dest_ap.code = Routes.dest_ap_code)
                   '''

        arg_arr = []
        if src or dest or status:
            query += ' WHERE '
        if src:
            query += 'Routes.origin_ap_code = %s '
            arg_arr.append(src)
        if dest:
            query += f'{"AND" if src else ""} Routes.dest_ap_code = %s '
            arg_arr.append(dest)
        if status:
            query += f'{"AND" if src or dest else ""} Flights.status = %s '
            arg_arr.append(status)


        query += ''' ORDER BY Flights.departure_time LIMIT %s,%s;'''

        offset = (page-1) * results_per_page
        cursor.execute(query, arg_arr + [offset, results_per_page])

        data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data


@app.route('/airlines')
def get_airlines():
    name = request.args.get('airline_name')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    query = '''SELECT Airlines.code AS airline_code, Airlines.name AS airline_name
               FROM Airlines
               WHERE Airlines.name LIKE CONCAT('%', %s, '%')
               LIMIT 20;
            '''

    cursor.execute(query, [name])
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


@app.route('/routes')
def get_routes():
    src = request.args.get('origin_ap_code')
    dest = request.args.get('dest_ap_code')

    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    query = '''SELECT Routes.ID AS id, Airplane.model AS airplane_model
               FROM Routes
               INNER JOIN Airplane on Airplane.code = Routes.airplane_code
               WHERE Routes.origin_ap_code = %s
                 AND Routes.dest_ap_code = %s
            '''

    cursor.execute(query, [src, dest])

    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data


@app.route('/buyticket')
def buyticket():
    f_id = int(request.args.get('f_id'))
    p_id = int(request.args.get('p_id'))
    seat_number = int(request.args.get('seat_number'))
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME,
        autocommit=True
    )
    cursor = cnx.cursor(dictionary=True)
    query = '''
            INSERT INTO Ticket(passenger_id, flight_id, seat_number, status)
            VALUES (%s, %s, %s, "booked");
            '''
    cursor.execute(query, [p_id, f_id, seat_number])
    cnx.commit()
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data


@app.route('/cancel_flight')
def cancel_flight():
    f_id = request.args.get('flight_id')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME,
        autocommit=True
    )
    cursor = cnx.cursor()
    with open('queries/test-cancel-flight.sql', 'r') as f:
        query = f.read().replace('{f_id}', f_id)
        print(query)
        cursor.execute(query)
        cnx.commit()
    cursor.close()
    cnx.close()
    return "flight cancelled"


# the new UI does not use this
@app.route('/findflightcancellation')
def findflightcancellation():
    r_id = request.args.get('r_id')
    dep_time = request.args.get('dep_time')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME,
        autocommit=True
    )
    cursor = cnx.cursor()
    with open('queries/test-show-cancel-flights.sql', 'r') as f:
        query = f.read().replace('{route_id}', r_id)
        query = query.replace('{date_time}', dep_time)
        cursor.execute(query)
        data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return str(data)


@app.route('/displaymonthlydelays')
def displaymonthlydelays():
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME,
        autocommit=True
    )
    cursor = cnx.cursor()
    with open('queries/delay-linegraph.sql', 'r') as f:
        query = f.read()
        cursor.execute(query)
        data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return str(data)


if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True, ssl_context="adhoc")
