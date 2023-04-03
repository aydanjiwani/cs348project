from flask import Flask, render_template, request, redirect, session, jsonify, Markup
import mysql.connector
import pymysql
from flask_cors import CORS
import hashlib
from flask_session import Session
from datetime import timedelta
import pydeck as pdk
import smtplib
import ssl
from email.message import EmailMessage

from_addr = "airportabcde@gmail.com"
password = "bqexdlglojgpovra"

# rows[0] = departure time
# rows[1] = departure origin
# rows[2] = departure destination
# rows[3] = departure name
# rows[4] = departure email

def email_all(rows):
    for passenger in range(rows):
        txt = passenger[4]
        end = txt.split("@")
        if end[-1] == "gmail.com":
            subject = "flight notifiation"
            message = "hello " + passenger[3] + " your flight from " + passenger[1] + " to " + passenger[2] + " will depart at " + passenger[0].strftime("%Y-%m-%d %H:%M") + " please be there at least 2 hours in advance to check in your bags. Enjoy your flight ;)"

            em = EmailMessage()
            em['From'] = from_addr
            em['To'] = passenger[4]
            em['Subject'] = subject
            em.set_content(message)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(from_addr, password)
                smtp.sendmail(from_addr, passenger[4], em.as_string())

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.update(
    SECRET_KEY='a secret key',
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=30)
)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Change these according to your database
DB_NAME = 'world'
DB_USER = 'username'
DB_PWD = 'password'


def displaymap(points):
    # Extracting start and end coordinates from the list
    start_points = [[float(point[0]), float(point[1])] for point in points]
    end_points = [[float(point[2]), float(point[3])] for point in points]
    points_dict = [{'start_lon': float(point[0]), 'start_lat':float(
        point[1]), 'end_lon':float(point[2]), 'end_lat': float(point[3])} for point in points]

    # Creating the scatterplot layer for start points
    start_layer = pdk.Layer(
        'ScatterplotLayer',
        data=start_points,
        get_position='-',
        get_radius=20000,
        get_fill_color=[0, 255, 0],
        pickable=True,
        filled=True
    )

    # Creating the scatterplot layer for end points
    end_layer = pdk.Layer(
        'ScatterplotLayer',
        data=end_points,
        get_position='-',
        get_radius=20000,
        get_fill_color=[0, 255, 0],
        pickable=True,
        filled=True
    )

    # Creating the line layer
    line_layer = pdk.Layer(
        'LineLayer',
        data=points_dict,
        get_source_position='[start_lon,start_lat]',
        get_target_position='[end_lon,end_lat]',
        get_color=[255, 255, 255],
        get_width=1,
        pickable=True
    )

    # Combining the layers in a deck
    deck = pdk.Deck(layers=[start_layer, end_layer, line_layer])

    # Displaying the deck
    # Get the HTML code for the Pydeck visualization
    html = deck.to_html(as_string=True)

    # Render the HTML template with the Pydeck visualization
    return html

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
        cursor.execute(query, multi=True)
    cursor.close()
    cnx.close()
    return redirect('/')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/routemap')
def routemap():
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME
    )
    cursor = cnx.cursor()
    code = request.args.get('code', default='', type=str)
    cursor.execute("""SELECT origin.longit AS start_long, origin.lat AS start_lat, dest.longit AS end_long, dest.lat AS end_lat
FROM airport AS origin
JOIN routes ON origin.code = routes.origin_ap_code
JOIN airport AS dest ON dest.code = routes.dest_ap_code
JOIN (
  SELECT DISTINCT route_id, COUNT(*) AS num_flights
  FROM flights
  GROUP BY route_id
) AS flight_counts ON routes.ID = flight_counts.route_id
ORDER BY num_flights DESC
LIMIT 100;
""")
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return Markup(displaymap(data))


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
@app.route('/emailpassengers')
def emailpassengers():
    f_id = request.args.get('f_id')
    cnx = mysql.connector.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PWD,
        database=DB_NAME,
        autocommit=True
    )
    cursor = cnx.cursor()
    with open('queries/get-passengers.sql', 'r') as f:
        query = f.read().replace('{f_id}', f_id)
        print(query)
        cursor.execute(query)
        emaildata = cursor.fetchall()
        email_all(emaildata)
        cnx.commit()
    cursor.close()
    cnx.close()
    return "passengers emailed"


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


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        profile_picture_url = data['profilePicture']
        role = data['role']
        db_name = DB_NAME
        host_name = 'localhost'

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cnx = mysql.connector.connect(
            host='localhost',
            user=DB_USER,
            password=DB_PWD,
            database=DB_NAME,
            autocommit=True
        )

        cursor = cnx.cursor()
        cursor.execute("INSERT INTO Users (username, password, role, profile_picture_url) VALUES (%s, %s, %s, %s)", [
            username, hashed_password, role, profile_picture_url])
        cnx.commit()

        # This code was breaking the register process
        # cursor.execute(
        #         "CREATE USER %s@%s IDENTIFIED BY %s", [username, host_name, password])
        # if role == 'admin':
        #     cursor.execute(
        #         "GRANT ALL PRIVILEGES ON %s.* TO %s@%s", [db_name, username, host_name]) #all access
        # else:
        #     cursor.execute(
        #         "GRANT SELECT ON %s.* TO %s@%s", [db_name, username, host_name]) #read-only/select access
        # cnx.commit()

        cursor.execute(
            "SELECT ID, username, role, profile_picture_url FROM Users WHERE username=%s", [username])
        user = cursor.fetchone()

        session.permanent = True
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[2]
        session['profile_picture_url'] = user[3]

        cursor.close()

        user_dict = {
            'id': user[0],
            'username': user[1],
            'role': user[2],
            'profile_picture_url': user[3]
        }

        return jsonify({'status': 'success', 'user': user_dict})
    except Exception as e:
        return jsonify({'status': e}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cnx = mysql.connector.connect(
            host='localhost',
            user=DB_USER,
            password=DB_PWD,
            database=DB_NAME,
            autocommit=True
        )
        cursor = cnx.cursor()
        cursor.execute("SELECT ID, username, role, profile_picture_url FROM Users WHERE username=%s AND password=%s", [
            username, hashed_password])
        user = cursor.fetchone()
        cursor.close()

        if user:
            session.permanent = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            session['profile_picture_url'] = user[3]

            user_dict = {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'profile_picture_url': user[3]
            }

            return jsonify({'status': 'success', 'user': user_dict})
        else:
            return jsonify({'status': 'User does not exist'}), 401
    except Exception as e:
        return jsonify({'status': e}), 500


@app.route('/currentuser', methods=['GET'])
def current_user():
    if 'user_id' in session:
        user_id = session['user_id']

        cnx = mysql.connector.connect(
            host='localhost',
            user=DB_USER,
            password=DB_PWD,
            database=DB_NAME,
            autocommit=True
        )
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT ID, username, role, profile_picture_url FROM Users WHERE ID = %s", [user_id])
        user = cursor.fetchone()
        cursor.close()

        if user:
            return jsonify({
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'profile_picture_url': user[3]
            })

    return jsonify({'error': 'No user is logged in'}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success'})


@app.route("/users", methods=["GET"])
def get_users():
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user=DB_USER,
            password=DB_PWD,
            database=DB_NAME,
            autocommit=True
        )
        cursor = cnx.cursor()
        cursor.execute(
            "SELECT id, username, role, profile_picture_url FROM Users")
        users = cursor.fetchall()
        cursor.close()

        users_list = []
        for user in users:
            user_dict = {
                "id": user[0],
                "username": user[1],
                "role": user[2],
                "profile_picture_url": user[3]
            }
            users_list.append(user_dict)
        users_list.reverse()

        return jsonify(users_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/updaterole", methods=["POST"])
def update_role():
    try:
        data = request.get_json()
        user_id = data['user_id']
        new_role = data['role']

        if user_id is None or new_role is None:
            return jsonify({"error": "Missing user_id or role"}), 400

        cnx = mysql.connector.connect(
            host="localhost",
            user=DB_USER,
            password=DB_PWD,
            database=DB_NAME,
            autocommit=True
        )
        cursor = cnx.cursor()
        cursor.execute("UPDATE Users SET role = %s WHERE id = %s", [
                       new_role, user_id])

        cursor.close()
        cnx.close()

        return jsonify({"message": "Role updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True, ssl_context="adhoc")
