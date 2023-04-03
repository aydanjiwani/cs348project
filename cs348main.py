from flask import Flask, render_template, request, redirect,  Markup
import mysql.connector
from flask_cors import CORS
import pydeck as pdk

app = Flask(__name__)
CORS(app)

DB_NAME = 'prod'
DB_USER = 'noor'
DB_PWD = 'passowrd'

def displaymap(points):
    # Extracting start and end coordinates from the list
    start_points = [[float(point[0]), float(point[1])] for point in points]
    end_points = [[float(point[2]), float(point[3])] for point in points]
    points_dict = [{'start_lon': float(point[0]), 'start_lat':float(point[1]), 'end_lon':float(point[2]), 'end_lat': float(point[3])} for point in points]

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

@app.route('/init')
def init():
    cnx = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='prod'
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

@app.route('/routemap')
def routemap():
    cnx = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='world'
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
    cnx = mysql.connector.connect(
        host='localhost',
        user='noor',
        password='password',
        database='prod'
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
        user='root',
        password='password',
        database='world'
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
        user='root',
        password='password',
        database='world'
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
        user='root',
        password='password',
        database='world'
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
        user='root',
        password='password',
        database='world',
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
        user='root',
        password='password',
        database='world',
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
        user='root',
        password='password',
        database='world',
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
