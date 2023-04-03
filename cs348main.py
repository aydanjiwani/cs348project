from flask import Flask, render_template, request, redirect
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Change these according to your database
DB_NAME = 'world'
DB_USER = 'username'
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
        cursor.execute(query, multi=True)
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
    cursor.execute(
        "SELECT code FROM Airport WHERE code LIKE CONCAT('%', %s, '%')", [code])
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


@app.route('/findflight')
def findflight():
    src = request.args.get('src')
    dest = request.args.get('dest')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor()
    with open('queries/test-find-flight.sql', 'r') as f:
        query = f.read().replace('{src}', src)
        query = query.replace('{dest}', dest)
        cursor.execute(query)
        data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return str(data)


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


@app.route('/cancelflight')
def cancelflight():
    f_id = request.args.get('f_id')
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
    app.run(host="localhost", port=8000, debug=True)
