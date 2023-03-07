from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'world'
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/createflight')
def createflight():
    route_id = request.args.get('route_id')
    start = request.args.get('start')
    end = request.args.get('end')
    airline = request.args.get('airline')
    print(route_id,start,end,airline)
    with open('createflight.sql', 'r') as f:
        query = f.read().replace('{route_id}', route_id)
        query = f.read().replace('{start}', start)
        query = f.read().replace('{end}', end)
        query = f.read().replace('{airline}', airline)
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return str(data)


@app.route('/findflight')
def findflight():
    src = request.args.get('src')
    dest = request.args.get('dest')
    with open('findflight.sql', 'r') as f:
        query = f.read().replace('{src}', src)
        query = f.read().replace('{dest}', dest)
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return str(data)

@app.route('/buyticket')
def buyticket():
    f_id = request.args.get('f_id')
    p_id = request.args.get('p_id')
    with open('buyticket.sql', 'r') as f:
        query = f.read().replace('{f_id}', f_id)
        query = f.read().replace('{p_id}', p_id)
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return str(data)

@app.route('/cancelflight')
def cancelflight():
    f_id = request.args.get('f_id')
    with open('cancelflight.sql', 'r') as f:
        query = f.read().replace('{f_id}', f_id)
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return str(data)

if __name__ == '__main__':
    with open('create-tables.sql', 'r') as f:
    cur = mysql.connection.cursor()
    cur.execute(query)
    cur.close()
    app.run(host="localhost", port=8000, debug=True)
