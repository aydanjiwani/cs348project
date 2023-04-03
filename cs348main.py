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
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor()
    code = request.args.get('code', default='', type=str)
    cursor.execute("SELECT code FROM Airport WHERE code LIKE CONCAT('%', %s, '%')", [code])
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return {"data": data}


@app.route('/createflight')
def createflight():
    route_id = request.args.get('route_id')
    start = request.args.get('start')
    end = request.args.get('end')
    airline = request.args.get('airline')
    print(route_id, start, end, airline)
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor()
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return "flight created"


@app.route('/flights')
def get_flights():
    src = request.args.get('origin')
    dest = request.args.get('dest')
    status = request.args.get('status')

    page = int(request.args.get('page'))
    results_per_page = int(request.args.get('results_per_page'))

    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    query = '''SELECT Flights.ID as id, departure_time, flight_number,
                      origin_ap.code AS origin_ap_code,
                      dest_ap.code AS dest_ap_code,
                      origin_ap.city AS from_city,
                      dest_ap.city AS to_city,
                      Airplane.model AS airplane_model,
                      status, Airlines.name as airline_name
               FROM Flights
               INNER JOIN Airlines ON (Airlines.code = Flights.airline_code)
               INNER JOIN Routes ON (Flights.route_id = Routes.ID)
               INNER JOIN Airplane ON (Airplane.code = Routes.airplane_code)
               INNER JOIN Airport AS origin_ap ON (origin_ap.code = Routes.origin_ap_code)
               INNER JOIN Airport AS dest_ap ON (dest_ap.code = Routes.dest_ap_code)
               '''

    arg_arr = []
    if src or dest or status:
        query += 'WHERE '
    if src:
        query += 'Routes.origin_ap_code = %s '
        arg_arr.append(src)
    if dest:
        query += f'{"AND" if src else ""} Routes.dest_ap_code = %s '
        arg_arr.append(dest)
    if status:
        query += f'{"AND" if src or dest else ""} Flights.status = %s '
        arg_arr.append(status)


    query += 'ORDER BY Flights.departure_time LIMIT %s,%s;'
    print(query)

    offset = (page-1) * results_per_page
    cursor.execute(query, arg_arr + [offset, results_per_page])

    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data


@app.route('/routes')
def get_routes():
    src = request.args.get('origin_ap_code')
    dest = request.args.get('dest_ap_code')
    airline_name = request.args.get('airline_name')

    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)

    query = ''' '''

    cursor.execute(query, [src, dest, airline_name])

    data = cursor.fetchall()

    cursor.close()
    cnx.close()
    return data


@app.route('/buyticket')
def buyticket():
    f_id = request.args.get('f_id')
    p_id = request.args.get('p_id')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor()
    with open('queries/test-sample-buy-ticket.sql', 'r') as f:
        query = f.read().replace('{f_id}', f_id)
        query = query.replace('{p_id}', p_id)
        cursor.execute(query)
        cnx.commit()
    cursor.close()
    cnx.close()
    return "ticket bought"


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
